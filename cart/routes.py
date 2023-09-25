from flask import request, jsonify, make_response
from flask_restx import Api, Resource
from core.utils import verify_user, verify_superuser
from .schemas import CartValidator
from core import create_app, db
from .models import Cart, CartItems
from book.models import Book

app = create_app(config_mode="development")
api = Api(app)


@api.route('/cart')
class CartAPI(Resource):
    """
    Cart API
    This API allows you to manage the user's cart.
    """

    @verify_user
    def post(self, **kwargs):
        try:
            # taken user input that which book and how much quantity is required in my bookstore
            data = request.get_json()  # user input converted to dictionary format

            # looking if the asked book is really in my stock/db or not
            book = Book.query.filter_by(id=data.get("book_id")).one_or_none()  # getting requested book obj from db
            if not book:
                return jsonify({"message": "Book Not Found"})

            # checking if the user is already having cart or not
            cart = Cart.query.filter_by(user_id=kwargs['current_user']['id'], is_ordered=False).one_or_none()

            # if cart is not yet created , then create a cart
            if not cart:
                cart = Cart(user_id=kwargs['current_user']['id'])
                db.session.add(cart)
                db.session.commit()

            # Check if the requested quantity exceeds the available quantity of the book
            if data.get("quantity") > book.quantity:
                return jsonify({"message": "Requested quantity exceeds available stock"})

            # As there will definitely be a cart, find what cart items are there in the cart_items
            cart_items = CartItems.query.filter_by(book_id=book.id, cart_id=cart.id).one_or_none()

            # if cart_items is not there create cart_items else update cart_items
            if not cart_items:
                cart_items = CartItems(book_id=book.id, cart_id=cart.id)
            else:
                cart.total_quantity -= cart_items.quantity
                cart.total_price -= cart_items.price

            # accordingly update price and quantity of cart_items as well
            cart_items.price = book.price * data.get("quantity")
            cart_items.quantity = data.get("quantity")
            db.session.add(cart_items)
            db.session.commit()

            cart.total_price += book.price * data.get("quantity")
            cart.total_quantity += data.get("quantity")
            db.session.commit()
            return {"msg": "Data updated", "status": 200, "data": cart.to_dict}
        except Exception as e:
            return {"message": str(e), "status": 400}, 400

    @verify_user
    def get(self, **kwargs):
        try:
            cart = Cart.query.filter_by(user_id=kwargs['current_user']['id'], is_ordered=False).one_or_none()
            if cart:
                return {"msg": "Retrieved Cart Details Successfully", "status": 200, "data": cart.to_dict}, 200
            return {"message": "No items in the Cart", "status": 200}, 200
        except Exception as e:
            return {"message": str(e), "status": 400}, 400

    @verify_user
    def delete(self, **kwargs):
        try:
            cart = Cart.query.filter_by(user_id=kwargs['current_user']['id'], is_ordered=False).one_or_none()
            if cart:
                db.session.delete(cart)
                db.session.commit()
                return {"msg": "Cart deleted successfully", "status": 200, "data": {}}, 200
            return {"msg": "No cart found for the user", "status": 404}, 404
        except Exception as e:
            return {"message": str(e), "status": 400}, 400
