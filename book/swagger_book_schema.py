from flask_restx import fields

models = {
    "book_schema": {
        "name": fields.String,
        "author": fields.String,
        "price": fields.Integer,
        "quantity": fields.Integer
    }
}
