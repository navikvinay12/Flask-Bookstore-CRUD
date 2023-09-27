from flask_restx import fields

models = {
    "user_register_schema": {
        "username": fields.String,
        "password": fields.String,
        "email": fields.String,
        "location": fields.String,
        "phone": fields.Integer,
        "firstname": fields.String,
        "lastname": fields.String,
        "admin_key": fields.String
    },
    "user_login_schema": {
        "username": fields.String,
        "password": fields.String
    }
}
