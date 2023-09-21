from core import create_app, db
from flask import request, jsonify, url_for
from .models import User
from .schemas import UserValidator
from .utils import send_email, decode_token, encode_jwt

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
        db.session.add(user)
        db.session.commit()

        # Generates a token for verification
        token = encode_jwt(user.id)

        # Sends mail having token in the mail to user for verification while registration
        link = f"http://{request.host}{url_for('verify_user', token=token)}"
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
