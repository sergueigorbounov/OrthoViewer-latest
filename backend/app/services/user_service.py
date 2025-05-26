from typing import List, Optional, Dict
from app.models.user import User, UserCreate, UserUpdate


class UserService:
    """Service for managing users"""
    
    def __init__(self):
        """Initialize with an in-memory user store for demonstration"""
        self.users: Dict[str, User] = {}
        self.next_id = 1
    
    def get_all_users(self) -> List[User]:
        """Get all users"""
        return list(self.users.values())
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return self.users.get(username)
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        if user_data.username in self.users:
            raise ValueError(f"User with username {user_data.username} already exists")
        
        # Create new user
        user = User(
            id=self.next_id,
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name
        )
        
        # Save user
        self.users[user_data.username] = user
        self.next_id += 1
        
        return user
    
    def update_user(self, username: str, user_data: UserUpdate) -> Optional[User]:
        """Update an existing user"""
        user = self.users.get(username)
        if not user:
            return None
        
        # Update fields if provided
        if user_data.email is not None:
            user.email = user_data.email
        
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        # Save updated user
        self.users[username] = user
        
        return user
    
    def delete_user(self, username: str) -> bool:
        """Delete a user"""
        if username not in self.users:
            return False
        
        del self.users[username]
        return True