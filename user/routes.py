from core import create_app, db
from flask import request, jsonify, make_response
from .models import User
from .schemas import UserValidator
from .utils import send_email, decode_token, encode_jwt
from flask_restx import Api, Resource
from .swagger_user_schema import models
from settings import setting

app = create_app(config_mode="development")
api = Api(app,
          default='Registration and Login',
          title='User',
          default_label='APIs',
          doc='/docs'
          )


@api.route('/user')
class UserRegistrationAPI(Resource):

    @api.doc(body=api.model('user_register_schema', models.get('user_register_schema')))
    def post(self):
        """
        Description: Handle New User Registration.
                    Expects JSON data in the request body with user information.
                    If successful, adds the new user to the database.
        Returns:
           JSON response with registration status and message.
        """
        try:
            serializer = UserValidator(**request.get_json())
            user = User(**serializer.model_dump())

            data = request.get_json()
            if data.get('admin_key') is not None:
                if data.get('admin_key') == setting.ADMIN_KEY:
                    user.is_superuser = True
                else:
                    return make_response(jsonify({"message": "Invalid Admin Key", "status": 401,
                                                  "data": user.to_dict}), 401)
            db.session.add(user)
            db.session.commit()

            # Generates a token for verification
            token = encode_jwt(user.id)

            # Sends mail having token in the mail to user for verification while registration
            base_url = ":".join(request.url_root.split(":")[:-1])
            link = f"{base_url}:{setting.USER_PORT}/user?token={token}"
            send_email(user.email, link)

            return make_response(jsonify({"message": "Registered", "status": 201, "data": user.to_dict}), 201)
        except Exception as e:
            return make_response(jsonify({"message": "Registration failed", "error": str(e)}), 400)

    @api.doc(params={'token': 'input token for account verification'})
    def get(self):
        """
        Description: Verify user registration using the provided token as query string.
            Expects a JSON object with the 'token' field in the request body.
        Returns:
            JSON response with verification status and message.
        """
        # token = request.args.to_dict().get('token')  # dict of query string
        token = request.args.get('token')
        if not token:
            return make_response(jsonify({"msg": "Token data is missing", "status": 404})), 404
        payload = decode_token(token)  # Decode the token
        user_id = payload.get('user_id')
        if not user_id:
            return make_response(jsonify({"Message": "User ID Not Found from token", "status": 404}), 404)
        user = User.query.filter_by(id=user_id).first()  # Find the user in the database by user_id
        if not user:
            return make_response(jsonify({"Message": "User Not Found", "status": 404}), 404)

        user.is_verified = True  # Mark the user as verified
        db.session.commit()
        return make_response(jsonify({'message': 'Account verification successfully', 'status': 200}), 200)


@api.route('/login')
class UserLoginAPI(Resource):

    @api.doc(body=api.model('user_login_schema', models.get('user_login_schema')))
    def post(self):
        """
        Description: Handle's user login.
            Expects JSON data in the request body with 'username' and 'password'.
            Checks if the provided credentials are valid and the user is verified.
        Parameter: nothing
        Return:  JSON response with login status and message.
        """
        try:
            data = request.get_json()
            user = User.query.filter_by(username=data['username']).first()
            if not (user or user.verify_pass(data.get("password")) or user.is_verified):
                return make_response(jsonify({"msg": "Invalid Username or Password", "status": 401}), 401)
            token = encode_jwt(user.id)
            return make_response(jsonify({"message": "Login Successfully", "token": token, "status": 200}), 200)
        except Exception as e:
            return make_response(jsonify({"message": "Unable to Login", "error": str(e)}), 400)

    @api.doc(params={'token': 'Retrieve user information from a JWT token'})
    def get(self):
        """
        Description: Retrieves user information from a JWT token.
        Returns: JSON: User information excluding the password.
        """
        try:
            token = request.args.get('token')  # Retrieve the token from the request headers
            if not token:
                return make_response(jsonify({'message': 'Authentication token is missing', "status": 401}), 401)

            # Decode and verify the JWT token
            payload = decode_token(token)

            # Access user information from the token
            user_id = payload["user_id"]

            # Check if the user exists in the database
            user = User.query.get(user_id)
            if not user:
                return make_response(jsonify({'message': 'User not found', "status": 404}), 404)

            # Return user data with a 200 OK response
            return make_response(user.to_dict, 200)
        except Exception as e:
            return jsonify({'message': str(e)}), 400
