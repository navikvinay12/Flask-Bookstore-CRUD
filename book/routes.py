from core import create_app, db
from .models import Book
from .schemas import BookValidator
from flask import request, jsonify, make_response
from flask_restx import Api, Resource
from core.utils import verify_user, verify_superuser
from .swagger_book_schema import models

app = create_app(config_mode="development")
api = Api(app,
          title='Book',
          default='Book-CRUD',
          default_label='APIs',
          security='Bearer',
          doc='/docs',
          authorizations={"Bearer": {"type": "apiKey", "in": "header", "name": "authorization"}})


@api.route("/book")
class BookAPI(Resource):
    """
    Book API
    This API allows you to manage books.
    """

    @api.doc(params={'book_id': 'Get details by its book_id'})
    @verify_user
    def get(self, **kwargs):
        """ Description: Get a list of books or a single book by ID.
        Args:
            book_id (int, optional): The ID of the book to retrieve. Defaults to None.
        Returns:
            dict: A JSON response with a list of books or a single book.
        """
        try:
            book_id = request.args.get('book_id')
            if book_id:
                book = Book.query.get(book_id)
                if book is None:
                    return {"msg": "Book ID not found", "status": 404}
                return {"msg": "Retrieved book", "status": 200, "data": book.to_dict}
            all_books = Book.query.all()
            response_data = [book.to_dict for book in all_books]
            return {"msg": "Retrieved all books", "status": 200, "data": response_data}
        except Exception as e:
            return {"message": str(e), "status": 400}

    @api.doc(body=api.model('book_schema', models.get('book_schema')))
    @verify_superuser
    def post(self, **kwargs):
        """
        Description: Add a new book to the database.
        Returns:
            dict: A JSON response of the newly created book's data.
        """
        try:
            serializer = BookValidator(**request.get_json())
            book = Book(**serializer.model_dump())
            db.session.add(book)
            db.session.commit()
            return make_response(jsonify({"msg": "Book Created Successfully", "status": 201, "data": book.to_dict}),
                                 201)
        except Exception as e:
            return jsonify({"message": "Registration failed", "error": str(e)}), 400

    @api.doc(params={'book_id': 'book_id id to be updated'})
    @api.doc(body=api.model('book_schema', models.get('book_schema')))
    @verify_superuser
    def put(self, **kwargs):
        """
        Description: Update a book by ID.
        Args:
            book_id (int): The ID of the book to update.
        Returns:
            dict: A JSON response with the updated book's data.
        """
        try:
            book_id = request.args.get('book_id')
            if not book_id:
                return make_response({"msg": "Book Id Not Found", "status": 404}, 404)
            serializer = BookValidator(**request.get_json())
            book = Book.query.get(book_id)
            if not book:
                return make_response(jsonify({"msg": "Book Not Found", "status": 404}), 404)
            [setattr(book, x, y) for x, y in serializer.model_dump().items()]
            db.session.commit()
            return make_response({"msg": "Book Updated Successfully", "status": 200, "data": book.to_dict},
                                 200)
        except Exception as e:
            return {"message": str(e), "status": 400}, 400

    @api.doc(params={'book_id': 'book_id id to be deleted'})
    @verify_superuser
    def delete(self, **kwargs):
        """ Description: Delete a book by ID.
        Args:
            book_id (int): The ID of the book to delete.
        Returns:
            dict: A JSON response confirming the deletion.
        """
        try:
            book_id = request.args.get('book_id')
            if not book_id:
                return {"msg": "Book Id Not Found", "status": 404}, 404
            book = Book.query.get(book_id)
            if not book:
                return make_response(jsonify({"msg": "Book Not Found", "status": 404}), 404)
            db.session.delete(book)
            db.session.commit()
            return make_response(jsonify({"msg": "Book Deleted Successfully", "status": 200}), 200)
        except Exception as e:
            return {"message": str(e), "status": 400}, 400


@app.route('/set_quantity', methods=['PUT'])
def set_book_quantity():
    """
    Description:
            Updates book quantities based on provided data, ensuring stock limits aren't exceeded.
    :return:
        Response (Success): Status Code: 201 (Created)  (Data: Details of the created order.)
        Response (Error): Status Code: 404 (Not Found) (if the cart is not found.)
        Status Code: 400 (Bad Request) (with an error message if any other error occurs.)
    """
    try:
        books = request.json.get('book_data')
        for i in books:
            book = Book.query.get(i[0])
            if book.quantity - i[1] < 0:
                raise Exception("Book Quantity exceeds stock limit")
            book.quantity -= i[1]
        db.session.commit()
        return make_response({"msg": "success", "status": 200}, 200)
    except Exception as e:
        return make_response({"msg": str(e), "status": 400}, 400)


@app.route('/get_book_by_id', methods=['GET'])
def get_book():
    try:
        book_id = request.args.get('book_id')
        book = Book.query.filter_by(id=book_id).one_or_none()  # getting requested book from db
        if not book:
            return jsonify({"message": "Book Not Found"}, 404)
        return make_response(book.to_dict, 200)
    except Exception as e:
        return make_response({"msg": str(e), "status": 400}, 400)
