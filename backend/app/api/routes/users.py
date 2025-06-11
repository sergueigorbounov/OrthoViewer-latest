from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional

router = APIRouter(prefix="/api/users", tags=["users"])

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None

class User(BaseModel):
    username: str
    email: str
    full_name: str

# Simple in-memory user storage for testing
users_db: Dict[str, User] = {}

@router.post("/", response_model=User, status_code=201)
async def create_user(user: UserCreate):
    """Create a new user."""
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    new_user = User(**user.dict())
    users_db[user.username] = new_user
    return new_user

@router.get("/{username}", response_model=User)
async def get_user(username: str):
    """Get a user by username."""
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return users_db[username]

@router.patch("/{username}", response_model=User)
async def update_user(username: str, user_update: UserUpdate):
    """Update a user."""
    if username not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    stored_user = users_db[username]
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(stored_user, field, value)
    
    return stored_user

@router.delete("/{username}")
async def delete_user(username: str):
    """Delete a user."""
    if username in users_db:
        del users_db[username]
    
    return {"message": "User deleted"} 