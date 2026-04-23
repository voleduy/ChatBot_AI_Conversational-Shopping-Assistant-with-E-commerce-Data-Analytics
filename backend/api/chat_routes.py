
from flask import Blueprint, request, jsonify
import uuid
from utils.validators import validate_user_input, sanitize_input, extract_price_from_text
from services.product_service import search_products, detect_categories
from services.ai_service import chat_with_ai
from services.session_service import save_message, log_search

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/message', methods=['POST'])
def send_message():
    data = request.get_json(silent=True) or {}
    
    raw_message = data.get('message', '').strip()
    session_id = data.get('session_id') or str(uuid.uuid4())

    message = sanitize_input(raw_message)

    is_valid, error_msg = validate_user_input(message)
    if not is_valid:
        return jsonify({
            "success": True,
            "session_id": session_id,
            "reply": error_msg,
            "products": [],
            "intent": "blocked"
        })
    
    save_message(session_id, "user", message)

    categories = detect_categories(message)
    price_constraints = extract_price_from_text(message)

    search_results = []
    is_product_query = bool(categories) or bool(price_constraints.get('max'))
    
    if is_product_query:
        search_results = search_products(
            query=message,
            price_constraints=price_constraints,
            categories=categories if categories else None,
            limit=5
        )
        log_search(
            session_id=session_id,
            query=message,
            categories=categories,
            price_max=price_constraints.get('max', 0),
            result_count=len(search_results)
        )

    ai_response = chat_with_ai(
        session_id=session_id,
        user_message=message,
        search_results=search_results if search_results else None
    )

    save_message(session_id, "assistant", ai_response["text"])

    ai_product_ids = [p["id"] for p in ai_response.get("products", [])]
    product_ids_order = ai_product_ids if ai_product_ids else [p["id"] for p in search_results]

    product_map = {p["id"]: p for p in search_results}
    ai_reason_map = {p["id"]: p.get("reason", "") for p in ai_response.get("products", [])}
    
    enriched_products = []
    for pid in product_ids_order:
        if pid in product_map:
            prod = product_map[pid].copy()
            prod["ai_reason"] = ai_reason_map.get(pid, "")
            enriched_products.append(prod)

    for p in search_results:
        if p["id"] not in [ep["id"] for ep in enriched_products]:
            prod = p.copy()
            prod["ai_reason"] = ""
            enriched_products.append(prod)
    
    return jsonify({
        "success": True,
        "session_id": session_id,
        "reply": ai_response["text"],
        "products": enriched_products[:5],
        "intent": {
            "categories": categories,
            "price_max": price_constraints.get("max"),
            "price_min": price_constraints.get("min"),
            "is_product_query": is_product_query
        }
    })

@chat_bp.route('/history/<session_id>', methods=['GET'])
def get_history(session_id):
    from services.session_service import get_session_history
    history = get_session_history(session_id)
    return jsonify({"success": True, "history": history})

@chat_bp.route('/new-session', methods=['POST'])
def new_session():
    session_id = str(uuid.uuid4())
    return jsonify({"success": True, "session_id": session_id})