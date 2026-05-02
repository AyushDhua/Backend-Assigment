import logging
import os

import click
from flask import Flask

from .config import get_config
from .extensions import db, jwt, migrate, limiter
from flask_cors import CORS
from .utils.error_handler import register_error_handlers
from .utils.logger import configure_logging
from .utils.response import error_response

logger = logging.getLogger(__name__)


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(get_config(config_name))
    app.url_map.strict_slashes = False
    CORS(app)

    configure_logging(app)
    logger.info("Starting app in %s mode", app.config.get("ENV", "development"))

    _register_extensions(app)
    _register_models()
    _register_jwt_callbacks()
    _register_blueprints(app)
    _register_health_route(app)
    _register_cli_commands(app)
    register_error_handlers(app)

    return app


def _register_extensions(app: Flask) -> None:
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)


def _register_models() -> None:
    """Import models so they are registered against db.metadata."""
    from . import models  # noqa: F401


def _register_jwt_callbacks() -> None:
    @jwt.unauthorized_loader
    def _missing_token(reason):
        return error_response("Unauthorized", 401, message=reason)

    @jwt.invalid_token_loader
    def _invalid_token(reason):
        return error_response("Invalid token", 401, message=reason)

    @jwt.expired_token_loader
    def _expired_token(_jwt_header, _jwt_payload):
        return error_response("Token has expired", 401)

    @jwt.revoked_token_loader
    def _revoked_token(_jwt_header, _jwt_payload):
        return error_response("Token has been revoked", 401)


def _register_blueprints(app: Flask) -> None:
    from .routes.auth_routes import auth_bp
    from .routes.task_routes import task_bp
    from .routes.trade_routes import trade_bp

    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(task_bp, url_prefix="/api/v1/tasks")
    app.register_blueprint(trade_bp, url_prefix="/api/v1/trades")


def _register_health_route(app: Flask) -> None:
    @app.route("/health", methods=["GET"])
    def health():
        return "OK", 200


def _register_cli_commands(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db_command():
        """Create all database tables defined by SQLAlchemy models. (Deprecated: Use Flask-Migrate)"""
        click.echo("Please use 'flask db init', 'flask db migrate', and 'flask db upgrade' instead.")

    @app.cli.command("drop-db")
    def drop_db_command():
        """Drop all database tables. Use with care."""
        if not click.confirm("This will DROP ALL TABLES. Continue?", default=False):
            click.echo("Aborted.")
            return
        db.drop_all()
        click.echo("Database tables dropped.")


app = create_app()


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=app.config.get("DEBUG", False))
