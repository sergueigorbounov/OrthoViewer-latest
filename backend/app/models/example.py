from pydantic import BaseModel, validator

class Example(BaseModel):
    """Example model for demonstration purposes."""
    id: int
    name: str
    value: int
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('name must not be empty')
        return v
    
    @validator('value')
    def value_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('value must be positive or zero')
        return v
    
    def double_value(self) -> int:
        """Return the value doubled."""
        return self.value * 2