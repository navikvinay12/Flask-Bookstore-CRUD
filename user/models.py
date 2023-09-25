from core import db
from passlib.hash import pbkdf2_sha256


class User(db.Model):
    """
    Represents a user in the system.
    Attributes: all fields mentioned below id, username, ..
     """
    __tablename__ = "user"

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255))
    email = db.Column(db.String)
    is_superuser = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    location = db.Column(db.String)
    phone = db.Column(db.BigInteger)
    firstname = db.Column(db.String(50))
    lastname = db.Column(db.String(50))

    @property
    def to_dict(self):
        """
        Convert the User object to a dictionary.
        Returns:
            dict: A dictionary representation of the User object.
        """
        return {"id": self.id, "firstname": self.firstname, "lastname": self.lastname, "username": self.username,
                "email": self.email, "is_superuser": self.is_superuser,
                "location": self.location, "phone": self.phone}

    def __init__(self, **kwargs):
        self.password = self.pass_hashing(kwargs.pop("password"))
        self.__dict__.update(kwargs)

    def pass_hashing(self, password):
        """
        Hash a password using PBKDF2-SHA256.
        Args:
            password (str): The password to be hashed.
        Returns:
            str: The hashed password.
        """
        return pbkdf2_sha256.hash(password)

    def verify_pass(self, raw_pass):
        """
        Verify a raw password against the hashed password.
        Args:
            raw_pass (str): The raw (unhashed) password to be verified.
        Returns:
            bool: True if the password matches, False otherwise.
        """
        return pbkdf2_sha256.verify(raw_pass, self.password)
