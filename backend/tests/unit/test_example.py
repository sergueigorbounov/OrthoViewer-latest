import pytest
from app.models.example import Example

def test_example_creation():
    """Test that an Example can be created with proper attributes."""
    example = Example(id=1, name="Test Example", value=42)
    assert example.id == 1
    assert example.name == "Test Example"
    assert example.value == 42

def test_example_validation():
    """Test validation rules for Example model."""
    # Name must not be empty
    with pytest.raises(ValueError):
        Example(id=1, name="", value=42)
    
    # Value must be positive
    with pytest.raises(ValueError):
        Example(id=1, name="Test", value=-1)

@pytest.mark.parametrize("value,expected", [
    (10, 20),
    (0, 0),
    (100, 200),
])
def test_example_double_value(value, expected):
    """Test the double_value method of Example."""
    example = Example(id=1, name="Test", value=value)
    assert example.double_value() == expected