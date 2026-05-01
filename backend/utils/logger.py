import logging
import os
import json
import time
import uuid
from flask import request, g, has_request_context
from logging.handlers import RotatingFileHandler
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

class CustomJSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "time": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if has_request_context():
            log_record["request_id"] = getattr(g, "request_id", None)
            log_record["endpoint"] = request.path
            log_record["method"] = request.method
            try:
                verify_jwt_in_request(optional=True)
                log_record["user_id"] = get_jwt_identity()
            except Exception:
                log_record["user_id"] = None
        if hasattr(record, "execution_time"):
            log_record["execution_time_ms"] = record.execution_time
        return json.dumps(log_record)

def configure_logging(app):
    log_file = app.config.get("LOG_FILE", "logs/app.log")
    log_level = app.config.get("LOG_LEVEL", "INFO").upper()

    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    formatter = CustomJSONFormatter()

    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    app.logger.handlers = []
    app.logger.propagate = True
    app.logger.setLevel(log_level)

    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = str(uuid.uuid4())

    @app.after_request
    def after_request(response):
        if hasattr(g, "start_time"):
            execution_time = (time.time() - g.start_time) * 1000
            app.logger.info("Request completed", extra={"execution_time": execution_time})
        return response
