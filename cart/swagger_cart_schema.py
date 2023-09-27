from flask_restx import fields

models = {
    "cart_schema": {
        "book_id": fields.Integer,
        "quantity": fields.Integer
    }
}
