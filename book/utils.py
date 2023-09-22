from flask import request, jsonify, make_response
import httpx
from werkzeug.exceptions import Unauthorized


def verify_user(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token not found"}), 404
        response = httpx.get("http://127.0.0.1:5000/retrieve_user", params={"token": token})
        if response.status_code == 200:
            kwargs.update(current_user=response.json())
        elif response.status_code >= 400:
            return jsonify({"msg": "User not found"}), 401
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper


def verify_superuser(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token not found"}), 404
        # url = url_for(route_name)   # Generate the URL dynamically
        response = httpx.get("http://127.0.0.1:5000/retrieve_user", params={"token": token})
        data = response.json()
        if response.status_code == 200 and data.get('is_superuser') != True:
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
