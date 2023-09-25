from pydantic import (BaseModel, FieldValidationInfo, ValidationError, field_validator)


class BookValidator(BaseModel):
    name: str
    author: str
    price: int
    quantity: int


class BookUpdate(BaseModel):
    name: str
    author: str
    price: int
    quantity: int
