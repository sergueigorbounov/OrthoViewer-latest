from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@router.get("/status")
@router.get("/api/status")
async def status_check():
    """Status check endpoint."""
    return {"status": "running"}