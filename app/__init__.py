import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from .models import db, User

csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
login_manager = LoginManager()
login_manager.login_view = 'main.admin_login'

def create_app():
    """Application factory for the Aura platform."""
    from werkzeug.middleware.proxy_fix import ProxyFix
    
    app = Flask(__name__, static_folder="static", template_folder="templates")
    # Wrap wsgi_app with ProxyFix to correctly handle X-Forwarded headers from Nginx reverse proxy
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "aura-dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "postgresql://aura_user:aura_pass@db:5432/aura_db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Trust reverse proxy for CSRF (allow HTTP to HTTPS and port mismatches behind proxy)
    app.config["WTF_CSRF_SSL_STRICT"] = False

    # Initialize extensions
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from . import routes
    app.register_blueprint(routes.bp)

    # Exempt driver JSON API endpoints from CSRF — they're protected by driver session checks
    # and are pure JSON APIs, not form submissions
    csrf.exempt(routes.driver_update_status)
    csrf.exempt(routes.driver_post_location)
    csrf.exempt(routes.order_location)

    return app
