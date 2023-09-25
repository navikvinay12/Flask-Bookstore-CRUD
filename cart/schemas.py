from pydantic import BaseModel


class CartValidator(BaseModel):
    book_id: int
    quantity: int
