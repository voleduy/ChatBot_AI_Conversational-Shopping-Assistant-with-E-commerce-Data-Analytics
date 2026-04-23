import json
import os
import re
import logging
import threading
from services.product_service import format_price, get_seller_trust_label
from services.session_service import get_session_history

logger = logging.getLogger(__name__)

AI_BACKEND = os.environ.get("AI_BACKEND", "auto")

LLAMACPP_MODEL_PATH  = os.environ.get("LLAMACPP_MODEL_PATH",
                                      "models/qwen2.5-0.5b-instruct-q4_k_m.gguf")
LLAMACPP_N_CTX       = int(os.environ.get("LLAMACPP_N_CTX",    "2048"))
LLAMACPP_N_THREADS   = int(os.environ.get("LLAMACPP_N_THREADS", "4"))
LLAMACPP_MAX_TOKENS  = int(os.environ.get("LLAMACPP_MAX_TOKENS","512"))

HF_MODEL_NAME  = os.environ.get("HF_MODEL_NAME",  "Qwen/Qwen2.5-0.5B-Instruct")
HF_MAX_TOKENS  = int(os.environ.get("HF_MAX_TOKENS", "512"))
HF_DEVICE      = os.environ.get("HF_DEVICE",      "cpu")
HF_CACHE_DIR   = os.environ.get("HF_CACHE_DIR",   "models/hf_cache")


SYSTEM_PROMPT = """Tôi là ShopBot, chỉ là trợ lý mua sắm AI.
Chỉ trả lời về sản phẩm và mua sắm. Không thảo luận chính trị, tôn giáo, thời tiết, cảm xúc.
Luôn trả lời bằng tiếng Việt, ngắn gọn, thân thiện.
Khi tư vấn sản phẩm: nêu lý do chọn, giá, ưu điểm chính.
Nếu được cung cấp danh sách sản phẩm, hãy tóm tắt và giải thích từng sản phẩm.
Cuối response, nếu muốn đề xuất sản phẩm cụ thể, đặt JSON vào thẻ:
<PRODUCTS>[{"id":"SP001","reason":"lý do ngắn"}]</PRODUCTS>"""

_model_lock      = threading.Lock()
_active_backend  = "none"   
_llama_model     = None
_hf_pipeline     = None


def _load_model_once():
    global _active_backend, _llama_model, _hf_pipeline
    if _active_backend != "none":
        return
    with _model_lock:
        if _active_backend != "none":
            return

        backend = AI_BACKEND.lower()

        # ── 1. llama-cpp ──
        if backend in ("llamacpp", "auto"):
            try:
                from llama_cpp import Llama  # type: ignore
                model_path = LLAMACPP_MODEL_PATH
                if not os.path.isabs(model_path):
                    base = os.path.join(os.path.dirname(__file__), "..", "..")
                    model_path = os.path.normpath(os.path.join(base, model_path))
                if os.path.exists(model_path):
                    logger.info(f"Loading llama-cpp model: {model_path}")
                    _llama_model = Llama(
                        model_path=model_path,
                        n_ctx=LLAMACPP_N_CTX,
                        n_threads=LLAMACPP_N_THREADS,
                        verbose=False,
                    )
                    _active_backend = "llamacpp"
                    logger.info("llama-cpp model loaded")
                    return
                else:
                    logger.warning(f"GGUF not found: {model_path}")
            except ImportError:
                logger.warning("llama-cpp-python not installed")
            except Exception as e:
                logger.error(f"llama-cpp error: {e}")

        if backend in ("transformers", "auto"):
            try:
                import torch                         # type: ignore
                from transformers import pipeline    # type: ignore
                logger.info(f"Loading HF model: {HF_MODEL_NAME} ...")
                os.makedirs(HF_CACHE_DIR, exist_ok=True)
                _hf_pipeline = pipeline(
                    "text-generation",
                    model=HF_MODEL_NAME,
                    device=HF_DEVICE,
                    torch_dtype=torch.float32,
                    max_new_tokens=HF_MAX_TOKENS,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    repetition_penalty=1.1,
                    model_kwargs={"cache_dir": HF_CACHE_DIR},
                )
                _active_backend = "transformers"
                logger.info(f"HF model loaded: {HF_MODEL_NAME}")
                return
            except ImportError:
                logger.warning("transformers/torch not installed")
            except Exception as e:
                logger.error(f"HF model error: {e}")

        _active_backend = "rule"
        logger.info("ℹUsing rule-based AI (no model loaded)")


def get_backend_info() -> dict:
    _load_model_once()
    info = {"backend": _active_backend}
    if _active_backend == "llamacpp":
        info["model"] = os.path.basename(LLAMACPP_MODEL_PATH)
    elif _active_backend == "transformers":
        info["model"] = HF_MODEL_NAME
    return info


def chat_with_ai(session_id: str, user_message: str, search_results: list = None) -> dict:
    _load_model_once()
    history = get_session_history(session_id)
    context = _build_context(user_message, search_results, history)

    if _active_backend == "llamacpp":
        return _generate_llamacpp(context, user_message, search_results)
    elif _active_backend == "transformers":
        return _generate_transformers(context, user_message, search_results)
    else:
        return _rule_based_response(user_message, search_results)


def _generate_llamacpp(context: str, user_message: str, search_results: list) -> dict:
    try:
        out = _llama_model.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": context},
            ],
            max_tokens=LLAMACPP_MAX_TOKENS,
            temperature=0.7,
            top_p=0.9,
            repeat_penalty=1.1,
            stop=["</s>", "<|im_end|>", "<|endoftext|>"],
        )
        text = out["choices"][0]["message"]["content"].strip()
        return _parse_ai_response(text, search_results)
    except Exception as e:
        logger.error(f"llama-cpp generate error: {e}")
        return _rule_based_response(user_message, search_results)


def _generate_transformers(context: str, user_message: str, search_results: list) -> dict:
    try:
        tok = _hf_pipeline.tokenizer
        if hasattr(tok, "apply_chat_template"):
            prompt = tok.apply_chat_template(
                [{"role": "system", "content": SYSTEM_PROMPT},
                 {"role": "user",   "content": context}],
                tokenize=False, add_generation_prompt=True,
            )
        else:
            prompt = f"[SYSTEM]{SYSTEM_PROMPT}\n[USER]{context}\n[ASSISTANT]"

        out = _hf_pipeline(prompt, return_full_text=False)
        raw = out[0]["generated_text"].strip()
        if "[ASSISTANT]" in raw:
            raw = raw.split("[ASSISTANT]")[-1].strip()
        return _parse_ai_response(raw, search_results)
    except Exception as e:
        logger.error(f"HF generate error: {e}")
        return _rule_based_response(user_message, search_results)


def _rule_based_response(user_message: str, search_results: list = None) -> dict:
    msg = user_message.lower()

    if search_results:
        lines = [f"Tôi tìm được **{len(search_results)} sản phẩm** phù hợp!\n"]
        for i, p in enumerate(search_results[:3], 1):
            seller   = p.get("seller", {})
            discount = _discount_pct(p)
            disc_str = f" ~~{format_price(p['original_price'])}~~ **-{discount}%**" if discount else ""
            lines.append(
                f"**{i}. {p['name']}**\n"
                f"Giá: {format_price(p['price'])}{disc_str}\n"
                f"{get_seller_trust_label(seller)} | "
                f"Đánh giá: {p.get('product_rating', 0)}/5 ({p.get('review_count', 0):,} đánh giá)\n"
                f"Mô tả: {p.get('description', '')[:90]}...\n"
            )
        lines.append("Nhấn vào sản phẩm để xem chi tiết đầy đủ!")
        products_out = [{"id": p["id"], "reason": _auto_reason(p, msg)} for p in search_results]
        return {"text": "\n".join(lines), "products": products_out}

    if any(w in msg for w in ["xin chào", "hello", "chào", "hi", "hey"]):
        return {"text": (
            "**Xin chào! Tôi là ShopBot AI** - trợ lý mua sắm của bạn!\n\n"
            "Tôi có thể giúp bạn:\n"
            "• Tìm sản phẩm theo nhu cầu & ngân sách\n"
            "• So sánh sản phẩm cùng loại\n"
            "• Tư vấn lựa chọn phù hợp nhất\n\n"
            "Bạn muốn tìm gì hôm nay?"
        ), "products": []}

    if any(w in msg for w in ["cảm ơn", "thank", "thanks", "oke", "ok"]):
        return {"text": "Không có gì! Nếu cần tư vấn thêm, tôi luôn sẵn sàng!", "products": []}

    if any(w in msg for w in ["so sánh", "khác nhau", "tốt hơn", "nên chọn"]):
        return {"text": (
            "Để so sánh, hãy cho biết:\n"
            "• **Những sản phẩm/thương hiệu nào** bạn đang phân vân?\n"
            "• Ngân sách của bạn?\n"
            "• Mục đích sử dụng chính?"
        ), "products": []}

    if any(w in msg for w in ["giá", "bao nhiêu", "tiền", "triệu", "nghìn", "rẻ"]):
        return {"text": (
            "Hãy cho tôi biết thêm:\n"
            "• **Loại sản phẩm** bạn muốn mua?\n"
            "• **Ngân sách tối đa**? (VD: dưới 5 triệu)"
        ), "products": []}

    return {"text": (
        "Tôi chuyên tư vấn sản phẩm trên Shopee, Tiki và Lazada.\n\n"
        "Hãy thử:\n"
        "• *\"Điện thoại Samsung dưới 8 triệu\"*\n"
        "• *\"Laptop cho sinh viên giá rẻ\"*\n"
        "• *\"Tai nghe chống ồn tốt nhất\"*"
    ), "products": []}


def _build_context(user_message: str, search_results: list, history: list) -> str:
    parts = []
    recent = history[-6:]
    if recent:
        parts.append("=== LỊCH SỬ ===")
        for m in recent:
            role = "Người dùng" if m["role"] == "user" else "ShopBot"
            parts.append(f"{role}: {m['content'][:200]}")
        parts.append("")
    if search_results:
        parts.append("=== SẢN PHẨM TÌM ĐƯỢC ===")
        for p in search_results[:5]:
            seller = p.get("seller", {})
            parts.append(
                f"[{p['id']}] {p['name']}\n"
                f"  Giá: {format_price(p['price'])} | {p['platform'].upper()}\n"
                f"  Đánh giá: {p.get('product_rating',0)}/5 ({p.get('review_count',0):,} reviews)\n"
                f"  Nhà bán: {seller.get('name','')} ({seller.get('rating',0)}/5)\n"
                f"  Mô tả: {p.get('description','')[:120]}"
            )
        parts.append("")
    parts.append(f"Câu hỏi: {user_message}")
    return "\n".join(parts)


def _parse_ai_response(text: str, search_results: list = None) -> dict:
    products = []
    clean = text
    m = re.search(r"<PRODUCTS>(.*?)</PRODUCTS>", text, re.DOTALL)
    if m:
        try:
            products = json.loads(m.group(1).strip())
            clean = text[: m.start()].strip()
        except Exception:
            pass
    if not products and search_results:
        products = [{"id": p["id"], "reason": ""} for p in search_results]
    return {"text": clean or text, "products": products}


def _auto_reason(product: dict, query: str) -> str:
    rating  = product.get("product_rating", 0)
    seller  = product.get("seller", {})
    reasons = []
    if rating >= 4.8:
        reasons.append("đánh giá xuất sắc")
    elif rating >= 4.5:
        reasons.append("đánh giá tốt")
    if seller.get("verified"):
        reasons.append("nhà bán uy tín")
    d = _discount_pct(product)
    if d >= 15:
        reasons.append(f"giảm {d}%")
    return ", ".join(reasons) if reasons else "phù hợp nhu cầu"


def _discount_pct(p: dict) -> int:
    price = p.get("price", 0)
    orig  = p.get("original_price", price)
    if orig > price > 0:
        return round((orig - price) / orig * 100)
    return 0