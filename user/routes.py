from core import create_app, db
from flask import request, jsonify, url_for
from .models import User
from .schemas import UserValidator
from .utils import send_email, decode_token, encode_jwt
from settings import setting

app = create_app(config_mode="development")


@app.route('/user', methods=['POST'])
def user_registration():
    try:
        """
        Description
           Handle user registration.
           Expects JSON data in the request body with user information.
           If successful, adds the new user to the database.
        Returns:
           JSON response with registration status and message.
        """
        # get_json() = (expect json_data --> parse+convert to dict)
        serializer = UserValidator(**request.get_json())

        # Generate a dictionary representation of the model, optionally specifying which fields to include or exclude.
        user = User(**serializer.model_dump())

        data = request.get_json()
        if data.get('admin_key') is not None:
            if data.get('admin_key') == setting.ADMIN_KEY:
                user.is_superuser = True
            else:
                return jsonify({"message": "Invalid Admin Key", "status": 401, "data": user.to_dict}), 401

        db.session.add(user)
        db.session.commit()

        # Generates a token for verification
        token = encode_jwt(user.id)

        # Sends mail having token in the mail to user for verification while registration
        link = f"http://{request.host}{url_for('verify_user', token=token)}"
        print(link)
        send_email(user.email, link)

        return jsonify({"message": "Registered", "status": 201, "data": user.to_dict}), 201
    except Exception as e:
        return jsonify({"message": "Registration failed", "error": str(e)}), 400


@app.route('/verified')
def verify_user():
    """
    Description:
        Verify user registration using the provided token.
        Expects a JSON object with the 'token' field in the request body.
    Returns:
        JSON response with verification status and message.
    """
    # token = request.args.to_dict().get('token')  # dict of query string
    token = request.args.get('token')
    if not token:
        return jsonify({"Status": "Token data is missing"})
    payload = decode_token(token)  # Decode the token
    user_id = payload.get('user_id')
    if not user_id:
        return jsonify({"Message": "User ID Not Found", "status": 404}), 404
    user = User.query.filter_by(id=user_id).first()  # Find the user in the database by user_id
    if not user:
        return jsonify({"Message": "User Not Found", "status": 404}), 404

    user.is_verified = True  # Mark the user as verified
    db.session.commit()
    return {'message': 'Account verification successfully', 'status': 200}, 200


@app.route('/user/login', methods=['POST'])
def login():
    """
    Description:
            Handle's user login.
            Expects JSON data in the request body with 'username' and 'password'.
            Checks if the provided credentials are valid and the user is verified.
    Parameter: nothing
    Return:  JSON response with login status and message.
    """
    try:
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        # verify_pass() fn used from models.py
        if not (user or user.verify_pass(data.get("password")) or user.is_verified):
            raise Exception("Invalid Username or Password")
        token = encode_jwt(user.id)

        return jsonify({"message": "Login Successfully", "token": token, "status": 200}), 200
    except Exception as e:
        return jsonify({"message": "Unable to Login", "error": str(e)}), 400


@app.route('/retrieve_user', methods=['GET'])
def retrieve_user():
    """
    Description: Retrieve user information from a JWT token.
    Parameter: None
    Returns: JSON: User information excluding the password.
    """
    # Retrieve the token from the request headers
    token = request.args.get('token')
    print(token)
    if not token:
        return jsonify({'message': 'Token is missing'}), 404

    try:
        # Decode and verify the JWT token
        payload = decode_token(token)

        # Access user information from the token
        user_id = payload["user_id"]

        # Check if the user exists in the database
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        # Return user data with a 200 OK response
        return jsonify(user.to_dict), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 400

# @app.route('/user/forgot_password', methods=['POST'])
# def forgot_password():
#     try:
#         data = request.get_json()
#         user = db.User.query(User.username == data.get("email")).first()
#         if not user:
#             raise Exception("User Not Found")
#
#         # Generates a token for verification
#         token = create_jwt_token(user.id)
#
#         link = f"http://{request.host}{url_for('/reset_password', token=token)}"
#         send_email(user.email, link)
#
#         return jsonify({"message": "password retrieval in progress", "status": 201}), 201
#     except Exception as e:
#         return jsonify({"message": "Unable to reset password", "error": str(e)}), 400
#
#
# @app.route('/user/reset_password', methods=['POST'])
# def reset_password():
#     token = request.args.get('token')
#     if not token:
#         return jsonify({"Status": "Token data is missing"})
#     payload = decode_token(token)  # Decode the token
#     user_id = payload.get('user_id')
#     if not user_id:
#         return jsonify({"Message": "User ID Not Found", "status": 404}), 404
#     user = User.query.filter_by(id=user_id).first()  # Find the user in the database by user_id
#     if not user:
#         return jsonify({"Message": "User Not Found", "status": 404}), 404
