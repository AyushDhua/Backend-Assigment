from flask import jsonify


def success_response(data=None, message: str = "OK", status_code: int = 200):
    return jsonify({"message": message, "data": data}), status_code


def error_response(
    error: str,
    status_code: int = 400,
    message: str | None = None,
    details=None,
):
    payload: dict = {"error": error}
    if message is not None:
        payload["message"] = message
    if details is not None:
        payload["details"] = details
    return jsonify(payload), status_code
