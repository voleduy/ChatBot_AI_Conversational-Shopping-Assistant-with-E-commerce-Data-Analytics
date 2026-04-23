
from flask import Blueprint, jsonify
from services.session_service import get_analytics_data
from services.product_service import _fetch_all_products

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
def dashboard():
    data = get_analytics_data()
    
    products = _fetch_all_products()
    platforms = {}
    categories = {}
    for p in products:
        plat = p.get('platform', 'other')
        platforms[plat] = platforms.get(plat, 0) + 1
        cat = p.get('category_name', 'Other')
        categories[cat] = categories.get(cat, 0) + 1
    
    data['product_stats'] = {
        "total": len(products),
        "by_platform": platforms,
        "by_category": categories
    }
    
    return jsonify({"success": True, "data": data})

@analytics_bp.route('/top-searches', methods=['GET'])
def top_searches():
    data = get_analytics_data()
    return jsonify({
        "success": True,
        "top_categories": data.get("top_categories", []),
        "total_searches": data.get("total_searches", 0)
    })

@analytics_bp.route('/price-distribution', methods=['GET'])
def price_distribution():
    data = get_analytics_data()
    return jsonify({
        "success": True,
        "distribution": data.get("price_distribution", [])
    })