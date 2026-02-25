import os
from flask import Flask


def create_app():
    """Application factory for the Aura platform."""
    app = Flask(__name__, static_folder="static", template_folder="templates")

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "aura-dev-secret-key")
    app.config["DATABASE_URL"] = os.environ.get(
        "DATABASE_URL", "postgresql://aura_user:aura_pass@db:5432/aura_db"
    )

    from . import routes
    app.register_blueprint(routes.bp)

    return app
