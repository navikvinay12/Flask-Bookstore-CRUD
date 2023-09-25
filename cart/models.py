from core import db


class Cart(db.Model):
    __tablename__ = 'cart'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    total_price = db.Column(db.Integer, default=0)
    total_quantity = db.Column(db.Integer, default=0)
    is_ordered = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.BigInteger, nullable=False)

    @property
    def to_dict(self):
        return {"id": self.id, "total_price": self.total_price, "total_quantity": self.total_quantity,
                "is_ordered": self.is_ordered, "user_id": self.user_id}


class CartItems(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    price = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)
    book_id = db.Column(db.BigInteger, nullable=False)
    cart_id = db.Column(db.BigInteger, nullable=False)

    @property
    def to_dict(self):
        return {"id": self.id, "price": self.price, "quantity": self.quantity, "book_id": self.book_id,
                "cart_id": self.cart_id}
