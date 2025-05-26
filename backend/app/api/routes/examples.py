from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.example import Example

router = APIRouter(prefix="/api/examples", tags=["examples"])

# Mock database for examples
examples_db = {
    1: Example(id=1, name="Example One", value=10),
    2: Example(id=2, name="Example Two", value=20),
}
next_id = 3

@router.get("/{example_id}", response_model=Example)
async def get_example(example_id: int):
    """Get a specific example by ID."""
    if example_id not in examples_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Example with ID {example_id} not found"
        )
    return examples_db[example_id]

@router.get("/", response_model=List[Example])
async def get_examples():
    """Get all examples."""
    return list(examples_db.values())

@router.post("/", response_model=Example, status_code=status.HTTP_201_CREATED)
async def create_example(example: Example):
    """Create a new example."""
    global next_id
    new_example = Example(id=next_id, name=example.name, value=example.value)
    examples_db[next_id] = new_example
    next_id += 1
    return new_example