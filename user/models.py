from core import db
from passlib.hash import pbkdf2_sha256


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String, unique=True)
    is_superuser = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    location = db.Column(db.String)
    phone = db.Column(db.BigInteger)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))

    @property
    def to_dict(self):
        return {"id": self.id, "firstname": self.firstname, "lastname": self.lastname, "username": self.username,
                "email": self.email, "is_superuser": self.is_superuser,
                "location": self.location, "phone": self.phone}
