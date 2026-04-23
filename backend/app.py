from flask import Flask, render_template
from flask_cors import CORS
from api.chat_routes import chat_bp
from api.product_routes import product_bp
from api.analytics_routes import analytics_bp
from database.mongo_client import init_db
import os

def create_app():
    app = Flask(
        __name__,
        template_folder='../frontend/templates',
        static_folder='../frontend/static'
    )
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ecommerce-chatbot-secret-2024')
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/ecommerce_chatbot')

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    init_db(app)

    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/product/<product_id>')
    def product_detail(product_id):
        return render_template('product_detail.html', product_id=product_id)

    @app.route('/analytics')
    def analytics_dashboard():
        return render_template('analytics.html')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from database.seed_data import seed_database
        seed_database()
    app.run(debug=True, host='0.0.0.0', port=5000)