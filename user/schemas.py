from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
import re


class UserValidator(BaseModel):
    firstname: str = Field(
        min_length=3, max_length=20, pattern=r"^[a-zA-Z]+$", description="Alphabetic characters only"
    )
    lastname: str = Field(
        min_length=3, max_length=20, pattern=r"^[a-zA-Z]+$", description="Alphabetic characters only"
    )
    username: str = Field(
        min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_-]+$",
        description="Alphanumeric characters, underscores, and dashes allowed"
    )
    password: str = Field(
        min_length=8, max_length=20,
        description="Min 8 characters, at least 1 upper, 1 lower, 1 numeric, 1 special char"
    )
    email: EmailStr
    location: str = Field(
        min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_-]+$",
        description="Alphanumeric characters, underscores, and dashes allowed"
    )
    phone: int = Field(
        gt=0, lt=10000000000, description="10-digit phone number"
    )
    admin_key: Optional[str] = Field(
        None, description="Optional string value (max 20 characters)"
    )

    @field_validator("password")
    def validate_password(cls, value):
        # Validated password using custom logic
        if not (
                any(char.isupper() for char in value) and
                any(char.islower() for char in value) and
                any(char.isdigit() for char in value) and
                any(char in "@$!%*?&" for char in value) and
                len(value) >= 8 and len(value) <= 20
        ):
            raise ValueError("Password must meet the specified criteria")
        return value
