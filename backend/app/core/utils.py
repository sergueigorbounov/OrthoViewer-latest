import json
import os
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status

from .config import get_settings

settings = get_settings()


def load_json_data(filepath: str) -> Dict[str, Any]:
    """Load data from a JSON file.
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Dictionary containing the JSON data
        
    Raises:
        HTTPException: If the file is not found or cannot be parsed
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {filepath}"
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing JSON file: {filepath}"
        )


def load_mock_data(filename: str) -> Dict[str, Any]:
    """Load mock data from a JSON file in the mock_data directory.
    
    Args:
        filename: Name of the JSON file in the mock_data directory
        
    Returns:
        Dictionary containing the mock data
        
    Raises:
        HTTPException: If the file is not found or cannot be parsed
    """
    filepath = os.path.join(settings.MOCK_DATA_DIR, filename)
    return load_json_data(filepath)


def save_json_data(data: Dict[str, Any], filepath: str) -> None:
    """Save data to a JSON file.
    
    Args:
        data: Dictionary containing the data to save
        filepath: Path where to save the JSON file
        
    Raises:
        HTTPException: If the file cannot be saved
    """
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving JSON file: {str(e)}"
        )


def ensure_directory_exists(directory: str) -> None:
    """Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory: Path to the directory
    """
    os.makedirs(directory, exist_ok=True)