from typing import List, Dict, Any, Optional, Type, TypeVar, Generic
from pydantic import BaseModel
from fastapi import HTTPException, status

from app.core.utils import load_mock_data

# Define a generic type variable for Pydantic models
T = TypeVar('T', bound=BaseModel)


class MockRepository(Generic[T]):
    """Generic repository for accessing mock data.
    
    This repository provides a generic interface for CRUD operations on mock data.
    It is designed to work with Pydantic models and mock JSON data.
    """
    
    def __init__(self, model_class: Type[T], data_filename: str, id_field: str = "id"):
        """Initialize the repository.
        
        Args:
            model_class: Pydantic model class for the entities
            data_filename: Name of the JSON file containing the mock data
            id_field: Name of the field used as identifier (default: "id")
        """
        self.model_class = model_class
        self.data_filename = data_filename
        self.id_field = id_field
        self.data_key = data_filename.split('.')[0]  # Assuming filename is singular of collection
    
    def get_all(self) -> List[T]:
        """Get all entities.
        
        Returns:
            List of entities
        """
        data = load_mock_data(self.data_filename)
        return [self.model_class(**item) for item in data.get(self.data_key, [])]
    
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get an entity by ID.
        
        Args:
            entity_id: ID of the entity to retrieve
            
        Returns:
            Entity if found, None otherwise
        """
        all_entities = self.get_all()
        for entity in all_entities:
            if getattr(entity, self.id_field) == entity_id:
                return entity
        return None
    
    def filter(self, **kwargs) -> List[T]:
        """Filter entities by attributes.
        
        Args:
            **kwargs: Attributes to filter on
            
        Returns:
            List of filtered entities
        """
        all_entities = self.get_all()
        result = all_entities
        
        for key, value in kwargs.items():
            result = [entity for entity in result if getattr(entity, key, None) == value]
        
        return result