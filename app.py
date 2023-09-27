from user.routes import app as user
from book.routes import app as book
from cart.routes import app as cart

if __name__ == '__main__':
    user.run(debug=True)
    book.run(debug=True)
    cart.run(debug=True)
