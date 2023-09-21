from pydantic import (
    BaseModel,
    FieldValidationInfo,
    ValidationError,
    field_validator
)


class UserValidator(BaseModel):
    firstname: str
    lastname: str
    username: str
    password: str
    email: str
    is_superuser: bool = False
    is_verified: bool = False
    location: str
    phone: int

    @field_validator("firstname", "lastname", "username", "password")
    def validate_length(cls, value):
        if len(value) < 4 or len(value) > 20:
            raise ValueError("Field length must be between 4 and 20 characters.")
        return value
