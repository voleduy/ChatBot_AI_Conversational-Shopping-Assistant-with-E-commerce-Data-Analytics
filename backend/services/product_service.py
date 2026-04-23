
from database.mongo_client import get_db, is_connected
from database.seed_data import get_all_products
from utils.validators import validate_product_content
import re
import logging

logger = logging.getLogger(__name__)

CATEGORY_KEYWORDS = {
    "dien-thoai": ["điện thoại", "phone", "iphone", "samsung galaxy", "xiaomi", "oppo", "smartphone", "di động"],
    "laptop": ["laptop", "máy tính xách tay", "macbook", "notebook", "máy tính", "dell", "asus", "máy tính cá nhân"],
    "tai-nghe": ["tai nghe", "earphone", "headphone", "airpods", "buds", "âm thanh", "headset"],
    "gia-dung": ["gia dụng", "nồi chiên", "máy xay", "lò vi sóng", "tủ lạnh", "máy giặt", "quạt", "điều hòa"],
    "giay-dep": ["giày", "dép", "sneaker", "boot", "sandal", "loafer"],
    "thoi-trang-nam": ["áo nam", "quần nam", "polo", "thời trang nam", "áo phông nam"],
    "my-pham": ["mỹ phẩm", "kem", "serum", "son môi", "phấn", "dưỡng da", "chăm sóc da", "skincare", "chống nắng"],
    "sach": ["sách", "book", "truyện", "tiểu thuyết", "học thuật"],
    "dong-ho-thong-minh": ["đồng hồ thông minh", "smartwatch", "apple watch", "galaxy watch", "đồng hồ"],
    "phu-kien-may-tinh": ["chuột", "bàn phím", "tai nghe máy tính", "màn hình", "hub", "cáp"],
    "thuc-pham": ["thực phẩm", "cà phê", "trà", "đồ ăn", "đồ uống", "snack"],
}

def detect_categories(query: str) -> list:
    query_lower = query.lower()
    matched = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in query_lower:
                if cat not in matched:
                    matched.append(cat)
                break
    return matched

def score_product(product: dict, query_lower: str, price_constraints: dict) -> float:

    score = 0.0

    price = product.get('price', 0)
    if price_constraints.get('max') and price > price_constraints['max']:
        return -1  # Exclude
    if price_constraints.get('min') and price < price_constraints['min']:
        return -1  # Exclude

    seller = product.get('seller', {})
    seller_rating = seller.get('rating', 3.0)
    response_rate = seller.get('response_rate', 80)
    total_sales = seller.get('total_sales', 0)
    verified = seller.get('verified', False)

    score += (seller_rating / 5.0) * 20
    score += (response_rate / 100.0) * 10
    score += min(total_sales / 50000, 1.0) * 5
    if verified:
        score += 5

    product_rating = product.get('product_rating', 3.0)
    review_count = product.get('review_count', 0)
    score += (product_rating / 5.0) * 15
    score += min(review_count / 10000, 1.0) * 5

    name = product.get('name', '').lower()
    description = product.get('description', '').lower()
    tags = ' '.join(product.get('tags', [])).lower()
    specs = str(product.get('specs', {})).lower()

    words = query_lower.split()
    matches = sum(1 for w in words if len(w) > 2 and (w in name or w in description or w in tags or w in specs))
    score += min(matches / max(len(words), 1), 1.0) * 30

    sold_count = product.get('sold_count', 0)
    score += min(sold_count / 100000, 1.0) * 5

    orig = product.get('original_price', price)
    if orig > price:
        discount = (orig - price) / orig
        score += discount * 5

    return score

def search_products(query: str, price_constraints: dict = None, categories: list = None, limit: int = 5) -> list:
    if price_constraints is None:
        price_constraints = {}

    products = _fetch_all_products()

    query_lower = query.lower()
    scored = []

    for product in products:
        if not validate_product_content(product):
            continue

        if categories:
            if product.get('category') not in categories:
                continue

        s = score_product(product, query_lower, price_constraints)
        if s >= 0:
            scored.append((s, product))

    scored.sort(key=lambda x: (-x[0], x[1].get('price', 0)))

    return [p for _, p in scored[:limit]]

def get_product_by_id(product_id: str) -> dict | None:
    products = _fetch_all_products()
    for p in products:
        if p.get('id') == product_id:
            return p
    return None

def _fetch_all_products() -> list:
    db = get_db()
    if db is not None:
        try:
            return list(db.products.find({}, {'_id': 0}))
        except Exception as e:
            logger.warning(f"MongoDB fetch failed: {e}")
    return get_all_products()

def format_price(price: int) -> str:
    if price >= 1_000_000:
        m = price / 1_000_000
        return f"{m:.1f}".rstrip('0').rstrip('.') + " triệu đồng"
    if price >= 1000:
        return f"{price:,}đ".replace(',', '.')
    return f"{price}đ"

def get_seller_trust_label(seller: dict) -> str:
    rating = seller.get('rating', 0)
    verified = seller.get('verified', False)
    if rating >= 4.8 and verified:
        return "Nhà bán uy tín cao"
    if rating >= 4.5:
        return "Nhà bán tin cậy"
    if rating >= 4.0:
        return "Nhà bán tốt"
    return "Nhà bán mới"