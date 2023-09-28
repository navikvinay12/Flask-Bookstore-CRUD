from flask import request, jsonify, make_response
from werkzeug.exceptions import Unauthorized
import httpx
from settings import setting


def verify_user(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return make_response({"message": "Token not found"}, 404)
        base_url = ":".join(request.url_root.split(":")[:-1])
        response = httpx.get(f"{base_url}:{setting.USER_PORT}/login", params={"token": token})
        if response.status_code == 200:
            kwargs.update(current_user=response.json())
        elif response.status_code >= 400:
            return make_response({"msg": "User not found"}, 401)
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def verify_superuser(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token not found"}), 404

        base_url = ":".join(request.url_root.split(":")[:-1])
        response = httpx.get(f"{base_url}:{setting.USER_PORT}/login", params={"token": token})
        user_data = response.json()
        is_superuser = user_data['is_superuser']
        if response.status_code == 200 and not is_superuser:
            return make_response(jsonify({"Message": "Permission denied"}), 403)
        elif response.status_code >= 400:
            return jsonify({"msg": "User not found"}), 401
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def exception_handler(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Unauthorized as ex:
            return {'message': str(ex), 'status': 401, 'data': {}}, 401
        except Exception as ex:
            return {'message': str(ex), 'status': 400, 'data': {}}, 400

    wrapper.__name__ = function.__name__
    return wrapper
