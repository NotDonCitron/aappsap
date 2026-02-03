from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_mail import Mail
from config import config

db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
migrate = Migrate()
mail = Mail()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    
    # Initialize Firebase (optional - only if config exists)
    try:
        from app.firebase import init_firebase
        init_firebase()
        app.config['FIREBASE_ENABLED'] = True
    except FileNotFoundError:
        app.config['FIREBASE_ENABLED'] = False
        print("⚠️  Firebase not configured. Run without Firebase features.")
    except Exception as e:
        app.config['FIREBASE_ENABLED'] = False
        print(f"⚠️  Firebase initialization failed: {e}")
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.inventory import inventory_bp
    from app.routes.orders import orders_bp
    from app.routes.admin import admin_bp
    from app.routes.firebase import firebase_bp
    from app.routes.shipping import shipping_bp
    from app.routes.cart import cart_bp
    from app.routes.reviews import reviews_bp
    from app.admin.routes import admin_bp as admin_dashboard_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(firebase_bp)
    app.register_blueprint(shipping_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(reviews_bp)
    app.register_blueprint(admin_dashboard_bp, name='admin_dashboard')
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'error': 'Forbidden'}), 403
    
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(429)
    def rate_limit(e):
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    return app

# Token blacklist (use Redis in production)
token_blacklist = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload['jti'] in token_blacklist
