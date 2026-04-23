from flask import Blueprint, request, jsonify
from services.product_service import search_products, get_product_by_id, _fetch_all_products
from utils.validators import extract_price_from_text

product_bp = Blueprint('products', __name__)

@product_bp.route('/', methods=['GET'])
def list_products():
    category = request.args.get('category')
    platform = request.args.get('platform')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    limit = request.args.get('limit', 20, type=int)

    products = _fetch_all_products()
    
    if category:
        products = [p for p in products if p.get('category') == category]
    if platform:
        products = [p for p in products if p.get('platform') == platform]
    if min_price:
        products = [p for p in products if p.get('price', 0) >= min_price]
    if max_price:
        products = [p for p in products if p.get('price', 0) <= max_price]
    
    return jsonify({
        "success": True,
        "products": products[:limit],
        "total": len(products)
    })

@product_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({"success": False, "error": "Không tìm thấy sản phẩm"}), 404
    return jsonify({"success": True, "product": product})

@product_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    max_price = request.args.get('max_price', type=int)
    category = request.args.get('category')
    limit = request.args.get('limit', 5, type=int)
    
    price_constraints = {}
    if max_price:
        price_constraints['max'] = max_price
    else:
        price_constraints = extract_price_from_text(query)
    
    categories = [category] if category else None
    results = search_products(query, price_constraints, categories, limit)
    
    return jsonify({
        "success": True,
        "products": results,
        "count": len(results)
    })

@product_bp.route('/categories', methods=['GET'])
def list_categories():
    from services.product_service import CATEGORY_KEYWORDS
    categories = [
        {"id": k, "name": k.replace('-', ' ').title()}
        for k in CATEGORY_KEYWORDS.keys()
    ]
    return jsonify({"success": True, "categories": categories})