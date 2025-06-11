"""
🧬 OrthoViewer2 Main Application - Clean 3-Layer Architecture
============================================================

Clean architecture with clear separation of concerns:
- API Layer: HTTP routes and request handling  
- Service Layer: Business logic and orchestration
- Data Access Layer: Data persistence and retrieval

Performance Requirements:
- GeneID search: < 50ms
- Species lookup: < 10ms  
- Orthogroup retrieval: < 100ms
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================================
# API LAYER - ROUTE IMPORTS
# ==========================================
try:
    from app.api.routes.health import router as health_router
    from app.api.routes.species import router as species_router
    from app.api.routes.genes import router as genes_router, gene_router
    from app.api.routes.orthogroups import router as orthogroups_router, orthogroup_router
    from app.api.routes.dashboard import router as dashboard_router
    from app.api.routes.examples import router as examples_router
    from app.api.routes.upload import router as upload_router
    from app.api.routes.users import router as users_router
    # Add orthologue router
    from app.api.orthologue import router as orthologue_router
    # Import load_mock_data for test compatibility
    from app.api.biological_routes import load_mock_data
    # Make it available at module level for tests
    __all__ = ['app', 'load_mock_data']
except ImportError as e:
    logging.warning(f"Some routes not available: {e}")
    # Create minimal routers for missing routes
    from fastapi import APIRouter
    health_router = APIRouter()
    species_router = APIRouter()
    genes_router = APIRouter()
    gene_router = APIRouter()
    orthogroups_router = APIRouter()
    orthogroup_router = APIRouter()
    dashboard_router = APIRouter()
    orthologue_router = APIRouter()
    examples_router = APIRouter()
    upload_router = APIRouter()
    users_router = APIRouter()
    
    # Create a mock load_mock_data function for fallback
    def load_mock_data(filename: str):
        return {}
    __all__ = ['app', 'load_mock_data']

# ==========================================
# FASTAPI APPLICATION SETUP
# ==========================================

app = FastAPI(
    title="OrthoViewer2 API",
    description="🧬 Bioinformatics visualization platform with 3-layer architecture",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:4173"  # Vite preview port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# API LAYER - ROUTE REGISTRATION  
# ==========================================

# Health and system routes
app.include_router(health_router)

# Core biological data routes
app.include_router(species_router)
app.include_router(genes_router) 
app.include_router(gene_router)  # Singular gene routes for test compatibility
app.include_router(orthogroups_router)
app.include_router(orthogroup_router)
app.include_router(dashboard_router)

# Add orthologue routes
app.include_router(orthologue_router)

# Add examples routes
app.include_router(examples_router)

# Add upload routes
app.include_router(upload_router)

# Add users routes
app.include_router(users_router)

# ==========================================
# CORE ENDPOINTS
# ==========================================

@app.get("/")
async def root():
    """🏠 Root endpoint - API welcome message"""
    return {
        "message": "🧬 OrthoViewer2 API - 3-Layer Architecture",
        "version": "2.0.0",
        "documentation": "/api/docs",
        "health": "/health",
        "architecture": {
            "api_layer": "FastAPI routes for HTTP handling",
            "service_layer": "Business logic and orchestration",
            "data_access_layer": "Data repositories and persistence"
        },
        "performance_targets": {
            "gene_search": "< 50ms",
            "species_lookup": "< 10ms",
            "orthogroup_retrieval": "< 100ms"
        }
    }

@app.get("/status")
async def status():
    """⚡ System status endpoint"""
    return {"status": "running", "version": "2.0.0", "architecture": "3-layer"}

@app.get("/api/status")
async def api_status():
    """⚡ API status endpoint"""
    return {"status": "running", "version": "2.0.0", "architecture": "3-layer"}

@app.get("/examples")
async def examples():
    """📚 Available example datasets"""
    return {
        "examples": [
            {"id": "arabidopsis", "name": "Arabidopsis thaliana", "type": "model_plant"},
            {"id": "rice", "name": "Oryza sativa", "type": "crop_plant"},
            {"id": "maize", "name": "Zea mays", "type": "crop_plant"}
        ]
    }

# ==========================================
# GLOBAL ERROR HANDLING
# ==========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Global HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status": "error"}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler for unexpected errors"""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status": "error"}
    )

# ==========================================
# APPLICATION LIFECYCLE
# ==========================================

@app.on_event("startup")
async def startup_event():
    """🚀 Application startup tasks"""
    logger.info("🧬 OrthoViewer2 API starting up...")
    logger.info("✅ 3-Layer Architecture initialized")
    logger.info("📡 API Layer: Routes registered")
    logger.info("⚙️ Service Layer: Business logic ready")
    logger.info("💾 Data Access Layer: Repositories available")

@app.on_event("shutdown")
async def shutdown_event():
    """🛑 Application shutdown tasks"""
    logger.info("🧬 OrthoViewer2 API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003) 