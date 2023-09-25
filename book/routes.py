from core import create_app, db
from .models import Book
from .schemas import BookValidator
from flask import request, jsonify, make_response
from flask_restx import Api, Resource
from core.utils import verify_user, verify_superuser

app = create_app(config_mode="development")
api = Api(app)


@api.route("/book")
class BookAPI(Resource):
    """
    Book API
    This API allows you to manage books.
    """

    @verify_user
    def get(self, **kwargs):
        """
        Get a list of books or a single book by ID.
        Args:
            book_id (int, optional): The ID of the book to retrieve. Defaults to None.
        Returns:
            dict: A JSON response with a list of books or a single book.
        """
        try:
            book_id = request.args.get('book_id')
            if book_id:
                book = Book.query.get(book_id)
                return {"msg": "Retrieved book", "status": 200, "data": book.to_dict}
            all_books = Book.query.all()
            response_data = [book.to_dict for book in all_books]
            return {"msg": "Retrieved all books", "status": 200, "data": response_data}
        except Exception as e:
            return {"message": str(e), "status": 400}

    @verify_superuser
    def post(self, **kwargs):
        """
        Add a new book to the database.
        Returns:
            dict: A JSON response with the newly created book's data.
        """
        try:
            serializer = BookValidator(**request.get_json())
            book = Book(**serializer.model_dump())
            db.session.add(book)
            db.session.commit()
            return make_response(jsonify(book.to_dict), 201)
        except Exception as e:
            return jsonify({"message": "Registration failed", "error": str(e)}), 400

    @verify_superuser
    def put(self, **kwargs):
        """
        Update a book by ID.
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

    @verify_superuser
    def delete(self, **kwargs):
        """
        Delete a book by ID.
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
