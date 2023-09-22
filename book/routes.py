from core import create_app, db
from .models import Book
from .schemas import BookValidator
from flask import request, jsonify, make_response
from flask_restx import Api, Resource
from .utils import verify_user, exception_handler, verify_superuser

app = create_app(config_mode="development")
api = Api(app)


@api.route("/book")
class BookAPI(Resource):
    """
    Book API
    This API allows you to manage books.
    """

    @verify_user
    def get(self, current_user):
        """
        Retrieve a list of all books.
        :param current_user: The current user's information.
        :return: A JSON response with a list of books.
        """
        try:
            all_books = Book.query.all()
            response_data = [book.to_dict for book in all_books]
            return {"msg": "Retrieved all books", "status": 200, "data": response_data}
        except Exception as e:
            return {"message": str(e), "status": 400}

    @verify_superuser
    def post(self):
        """
        Add a new book to the database.
        :return: A JSON response with the newly created book's data.
        """
        try:
            serializer = BookValidator(**request.get_json())
            book = Book(**serializer.model_dump())
            db.session.add(book)
            db.session.commit()
            return make_response(jsonify(book.to_dict), 201)
        except Exception as e:
            return jsonify({"message": "Registration failed", "error": str(e)}), 400


@api.route("/book/<int:book_id>")
class BookByIDAPI(Resource):
    """
    Book APIs by ID
    This API allows you to perform operations on individual books by their unique ID.
    """

    @verify_user
    def get(self, current_user, book_id):
        """
        Get a Book by ID
        Retrieve information about a book using its unique ID.
        :param current_user: The current user's information.
        :param book_id: The ID of the book to retrieve.
        :return: A JSON response with the book's data.
        """
        try:
            book_data = Book.query.get(book_id)  # or book_data = Book.query.filter_by(id=book_id).first()
            if not book_data:
                return {"msg": "Book is not found", "status": 404}, 404
            return {"msg": "Retrieved Book Data", "status": 200, "data": book_data.to_dict}, 200
        except Exception as e:
            return {"message": str(e), "status": 400}, 400

    @verify_superuser
    def put(self, book_id):
        """
        Update a Book by ID
        Update information about a book using its unique ID.
        :param book_id: The ID of the book to update.
        :return: A JSON response with the updated book's data.
        """
        try:
            serializer = BookValidator(**request.get_json())
            updated_book = Book(**serializer.model_dump())
            book = Book.query.get(book_id)
            if not book:
                return make_response(jsonify({"msg": "Book Not Found", "status": 201}), 201)
            book.name = updated_book.name
            book.author = updated_book.author
            book.price = updated_book.price
            book.quantity = updated_book.quantity
            db.session.commit()
            return make_response(jsonify({"msg": "Book Updated Successfully", "status": 200, "data": book.to_dict}),
                                 200)
        except Exception as e:
            return {"message": str(e), "status": 400}, 400

    @verify_superuser
    def delete(self, book_id):
        """
        Delete a Book by ID
        Delete a book from the database using its unique ID.
        :param book_id: The ID of the book to delete.
        :return: A JSON response confirming the deletion.
        """
        try:
            book = Book.query.get(book_id)
            if not book:
                return {"msg": "Book Not found", "status": 404}, 404
            db.session.delete(book)
            db.session.commit()
            return make_response(jsonify({"msg": "Book Deleted Successfully", "status": 200, "data": book.to_dict}),
                                 200)
        except Exception as e:
            return {"message": str(e), "status": 400}, 400
