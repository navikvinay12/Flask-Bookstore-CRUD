from core import db


class Book(db.Model):
    __tablename__ = "book"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)

    @property
    def to_dict(self):
        return {"id": self.id, "name": self.name, "author": self.author, "price": self.price, "quantity": self.quantity}
