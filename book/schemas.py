from pydantic import BaseModel


class BookValidator(BaseModel):
    name: str
    author: str
    price: int
    quantity: int
