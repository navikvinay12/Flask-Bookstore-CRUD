from flask import request, jsonify, make_response
from flask_restx import Api, Resource
from core.utils import verify_user
from .schemas import CartValidator
from core import create_app, db
from .models import Cart, CartItems
from .swagger_cart_schema import models
import httpx
from settings import setting

app = create_app(config_mode="development")
api = Api(app=app,
          title='Cart_APIs',
          default='Cart_Items & Orders',
          default_label='APIs',
          security='Bearer',
          doc='/docs',
          authorizations={"Bearer": {"type": "apiKey", "in": "header", "name": "authorization"}})


@api.route('/cart')
class CartAPI(Resource):
    """
    Cart API
    This API allows you to manage the user's cart.
    """

    @api.doc(body=api.model('cart_schema', models.get('cart_schema')))
    @verify_user
    def post(self, **kwargs):
        """
        Description: This endpoint allows users to add/update books to their cart
                It validates the input data, checks the availability of the requested book, and manages the user's cart
        :param kwargs:
                "book_id": int,        # ID of the book to add to the cart
                "quantity": int        # Quantity of the book to add to the cart
        :return:
          - 200 OK: Returns a success message and updated cart data in JSON format.
          - 400 Bad Request: Returns an error message if the input data is invalid or if the requested book is not found
           or the quantity exceeds the available stock.
        """
        try:
            # Taken user input that which book and how much quantity is required and converted to dict.
            data = CartValidator(**request.get_json()).model_dump()

            # Checking if the asked book is really in my stock/db or not. Requesting to Book API
            base_url = ":".join(request.url_root.split(":")[:-1])
            response = httpx.get(url=f"{base_url}:{setting.BOOK_PORT}/get_book_by_id", params={"book_id": data.get(
                "book_id")})
            if response.status_code >= 400:
                return jsonify({"message": "Book Not Found"}, 404)
            book_data = response.json()
            print(book_data['quantity'], )
            # Check if the requested quantity exceeds the available quantity of the book
            if data.get("quantity") > book_data['quantity']:
                return make_response({"message": "Requested quantity exceeds available stock"}, 400)

            # Checking if the user is already having cart or not.
            cart = Cart.query.filter_by(user_id=kwargs['current_user']['id'], is_ordered=False).one_or_none()

            # if cart is not yet created , then create a cart
            if not cart:
                cart = Cart(user_id=kwargs['current_user']['id'])
                db.session.add(cart)
                db.session.commit()

            # If there is a cart, find what cart items are there in the cart_items
            cart_items = CartItems.query.filter_by(book_id=book_data['id'], cart_id=cart.id).one_or_none()

            # if cart_items is not there create cart_items else reset cart_items to 0
            if not cart_items:
                cart_items = CartItems(book_id=book_data['id'], cart_id=cart.id)
            else:
                cart.total_quantity -= cart_items.quantity
                cart.total_price -= cart_items.price

            # Update price and quantity of cart_items as per user requirements
            cart_items.price = book_data['price'] * data.get("quantity")
            cart_items.quantity = data.get("quantity")
            db.session.add(cart_items)
            db.session.commit()

            # Same add/update to cart table also .
            cart.total_price += book_data['price'] * data.get("quantity")
            cart.total_quantity += data.get("quantity")
            db.session.commit()

            return {"msg": "Data updated", "status": 200, "data": cart.to_dict}
        except Exception as e:
            return {"message": str(e), "status": 400}, 400

    @verify_user
    def get(self, **kwargs):
        """
        Retrieves user's cart details or signals an empty cart

        :param kwargs: Getting current user data
        :return: A JSON response with cart details if the cart is not empty,
                 or a message indicating an empty cart.
        """
        try:
            cart = Cart.query.filter_by(user_id=kwargs['current_user']['id'], is_ordered=False).one_or_none()
            if cart:
                # Fetch all cart_items associated with the cart
                cart_items = CartItems.query.filter_by(cart_id=cart.id).all()

                # Clean up the cart_items data by creating dictionaries for each item without the SQLAlchemy-specific
                # '_sa_instance_state' attribute.
                cart_items_data = [{key: value for key, value in item.__dict__.items() if not key.startswith('_')} for
                                   item in cart_items if item.quantity > 0 and item.price > 0]

                cart_with_cart_items = cart.to_dict
                cart_with_cart_items['cart_items'] = cart_items_data
                return {"msg": "Retrieved Cart Details Successfully", "status": 200, "data": cart_with_cart_items}, 200
            return {"message": "No items in the Cart", "status": 200}, 200
        except Exception as e:
            return {"message": str(e), "status": 400}, 400

    @api.doc(params={'cart_id': 'cart_id id to be deleted'})
    @verify_user
    def delete(self, **kwargs):
        """
        Deletes the user's cart and associated cart items if it exists

        :param kwargs: Current User Details
        :return: A JSON response indicating successful deletion, a message if no cart is found, or an error message.
        """
        try:
            cart = Cart.query.filter_by(user_id=kwargs['current_user']['id'], is_ordered=False).one_or_none()
            if cart:
                # Delete all cart_items associated with the cart
                CartItems.query.filter_by(cart_id=cart.id).delete()

                # Deleting cart too.
                db.session.delete(cart)
                db.session.commit()
                return {"msg": "Cart deleted successfully", "status": 200, "data": {}}, 200
            return {"msg": "No cart found for the user", "status": 404}, 404
        except Exception as e:
            return {"message": str(e), "status": 400}, 400


@api.route('/order')
class OrderAPI(Resource):
    @api.doc(params={'id': 'Based on the given cart_id order will be placed'})
    @verify_user
    def post(self, **kwargs):
        """
        Places an order based on the given cart ID

        :param kwargs: Current User Details
        :return: A JSON response indicating the success of order placement or an error message.
        """
        try:
            cart_id = request.args.get('id')
            cart = Cart.query.filter_by(user_id=kwargs['current_user']['id'], is_ordered=False,
                                        id=cart_id).one_or_none()

            if cart:
                cart_items = CartItems.query.filter_by(cart_id=cart.id)
                books = list(map(lambda x: [x.book_id, x.quantity], cart_items))
                base_url = ":".join(request.url_root.split(":")[:-1])
                response = httpx.put(url=f"{base_url}:{setting.BOOK_PORT}/set_quantity", json={"book_data": books})
                if response.status_code >= 400:
                    raise Exception(response.json()['msg'])

                cart.is_ordered = True
                db.session.commit()

                return {"msg": "Order Created", "status": 201, "data": cart.to_dict}, 201
            return {"msg": "cart not found", "status": 404}, 404
        except Exception as e:
            return {"msg": e.args[0], "status": 400}, 400

    @verify_user
    def get(self, **kwargs):
        """
        Retrieves the user's ordered cart data, including ordered cart items

        :param kwargs: Getting current user data
        :return: A JSON response containing the ordered cart data, or a message indicating no ordered items found.
        """
        try:
            cart = Cart.query.filter_by(user_id=kwargs['current_user']['id'], is_ordered=True).one_or_none()
            if cart:
                # Fetch all cart_items associated with the cart
                cart_items = CartItems.query.filter_by(cart_id=cart.id).all()

                # Clean up the cart_items data by creating dictionaries for each item without the SQLAlchemy-specific
                # '_sa_instance_state' attribute.
                cart_items_data = [{key: value for key, value in item.__dict__.items() if not key.startswith('_')} for
                                   item in cart_items if item.quantity > 0 and item.price > 0]

                cart_with_cart_items = cart.to_dict
                cart_with_cart_items['cart_items'] = cart_items_data
                return {"msg": "Ordered Details", "status": 200, "data": cart_with_cart_items}, 200
            return make_response({"message": "No Ordered Items Found", "status": 404}, 404)
        except Exception as e:
            return {"message": e.args[0], "status": 400, "data": {}}, 400

    # @api.doc(params={'id': 'Order of the given ID will be deleted'})
    # @verify_user
    # def delete(self, **kwargs):
    #     """
    #     Deletes an order based on the given order ID
    #     :param kwargs: Current user data
    #     :return: A JSON response indicating the success of order deletion or a message if no orders are found.
    #     """
    #     try:
    #         cart_id = request.args.get('id')
    #         cart = Cart.query.filter_by(user_id=kwargs['current_user']['id'], is_ordered=True,
    #                                     id=cart_id).one_or_none()
    #         if cart:
    #             CartItems.query.filter_by(cart_id=cart.id).delete()
    #             db.session.delete(cart)
    #             db.session.commit()
    #             return {"msg": "Order deleted successfully", "status": 200}, 200
    #         return {"msg": "No Orders Found", "status": 404}, 404
    #     except Exception as e:
    #         return {"detail": e.args[0], "status": 400, "data": {}}, 400
