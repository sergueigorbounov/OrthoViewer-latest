from pydantic import BaseModel, field_validator

class Example(BaseModel):
    """Example model for demonstration purposes."""
    id: int
    name: str
    value: int
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('name must not be empty')
        return v
    
    @field_validator('value')
    @classmethod
    def value_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('value must be positive or zero')
        return v
    
    def double_value(self) -> int:
        """Return the value doubled."""
        return self.value * 2