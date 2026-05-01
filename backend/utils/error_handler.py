import logging

from werkzeug.exceptions import HTTPException

from .response import error_response

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        logger.warning("HTTP error %s: %s", err.code, err.description)
        return error_response(err.description or err.name, err.code)

    @app.errorhandler(404)
    def handle_not_found(_):
        return error_response("Resource not found", 404)

    @app.errorhandler(405)
    def handle_method_not_allowed(_):
        return error_response("Method not allowed", 405)

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        logger.exception("Unhandled exception: %s", err)
        return error_response("Internal server error", 500)
