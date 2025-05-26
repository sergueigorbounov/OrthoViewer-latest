from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model with common fields"""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    """Model for creating a new user"""
    username: str = Field(..., min_length=3, max_length=50)


class UserUpdate(BaseModel):
    """Model for updating a user (all fields optional)"""
    email: EmailStr | None = None
    full_name: str | None = Field(None, min_length=1, max_length=100)


class User(UserBase):
    """Complete user model with all fields"""
    id: int
    username: str

    class Config:
        from_attributes = True