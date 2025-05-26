from fastapi import APIRouter, HTTPException, status
from typing import List

from app.models.user import User, UserCreate, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])
service = UserService()


@router.get("/", response_model=List[User])
async def get_users():
    """Get all users"""
    return service.get_all_users()


@router.get("/{username}", response_model=User)
async def get_user(username: str):
    """Get user by username"""
    user = service.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} not found"
        )
    return user


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """Create a new user"""
    return service.create_user(user_data)


@router.patch("/{username}", response_model=User)
async def update_user(username: str, user_data: UserUpdate):
    """Update user details"""
    updated_user = service.update_user(username, user_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} not found"
        )
    return updated_user


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(username: str):
    """Delete a user"""
    success = service.delete_user(username)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} not found"
        )
    return None