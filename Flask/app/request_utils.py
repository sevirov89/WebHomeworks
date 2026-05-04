from flask import request

from app.errors import APIError


def parse_json_body():
    data = request.get_json(silent=True)
    if data is None:
        raise APIError("Тело запроса должно содержать JSON", 400)
    if not isinstance(data, dict):
        raise APIError("Ожидается объект JSON", 400)
    return data
