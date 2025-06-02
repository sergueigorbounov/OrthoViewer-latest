"""
🔧 API Dependencies - Dependency Injection
==========================================

FastAPI dependency injection for service layer.
Provides clean separation between layers.
"""

from typing import Generator
import logging

# Service layer imports (will be created)
try:
    from app.services.biological.species_service import SpeciesService
    from app.services.biological.gene_service import GeneService
    from app.services.biological.orthogroup_service import OrthogroupService
    from app.services.analytics.dashboard_service import DashboardService
except ImportError:
    # Temporary fallback for development
    SpeciesService = None
    GeneService = None
    OrthogroupService = None
    DashboardService = None

# Repository layer imports (will be created)
try:
    from app.repositories.file.species_repository import FileSpeciesRepository
    from app.repositories.file.gene_repository import FileGeneRepository
    from app.repositories.file.orthogroup_repository import FileOrthogroupRepository
    from app.repositories.cache.cache_repository import CacheRepository
except ImportError:
    # Temporary fallback for development
    FileSpeciesRepository = None
    FileGeneRepository = None
    FileOrthogroupRepository = None
    CacheRepository = None

logger = logging.getLogger(__name__)

# ==========================================
# REPOSITORY DEPENDENCIES
# ==========================================

def get_cache_repository() -> CacheRepository:
    """🗄️ Get cache repository instance"""
    if CacheRepository is None:
        logger.warning("CacheRepository not available, using mock")
        return None
    return CacheRepository()

def get_species_repository() -> FileSpeciesRepository:
    """🌱 Get species repository instance"""
    if FileSpeciesRepository is None:
        logger.warning("FileSpeciesRepository not available, using mock")
        return None
    return FileSpeciesRepository()

def get_gene_repository() -> FileGeneRepository:
    """🧬 Get gene repository instance"""
    if FileGeneRepository is None:
        logger.warning("FileGeneRepository not available, using mock")
        return None
    return FileGeneRepository()

def get_orthogroup_repository() -> FileOrthogroupRepository:
    """🌐 Get orthogroup repository instance"""
    if FileOrthogroupRepository is None:
        logger.warning("FileOrthogroupRepository not available, using mock")
        return None
    return FileOrthogroupRepository()

# ==========================================
# SERVICE DEPENDENCIES
# ==========================================

def get_species_service(
    species_repo: FileSpeciesRepository = get_species_repository(),
    cache_repo: CacheRepository = get_cache_repository()
) -> SpeciesService:
    """🌱 Get species service with injected repositories"""
    if SpeciesService is None:
        logger.warning("SpeciesService not available, using mock")
        return None
    return SpeciesService(species_repo=species_repo, cache_repo=cache_repo)

def get_gene_service(
    gene_repo: FileGeneRepository = get_gene_repository(),
    cache_repo: CacheRepository = get_cache_repository()
) -> GeneService:
    """🧬 Get gene service with injected repositories"""
    if GeneService is None:
        logger.warning("GeneService not available, using mock")
        return None
    return GeneService(gene_repo=gene_repo, cache_repo=cache_repo)

def get_orthogroup_service(
    orthogroup_repo: FileOrthogroupRepository = get_orthogroup_repository(),
    cache_repo: CacheRepository = get_cache_repository()
) -> OrthogroupService:
    """🌐 Get orthogroup service with injected repositories"""
    if OrthogroupService is None:
        logger.warning("OrthogroupService not available, using mock")
        return None
    return OrthogroupService(orthogroup_repo=orthogroup_repo, cache_repo=cache_repo)

def get_dashboard_service(
    species_service: SpeciesService = get_species_service(),
    gene_service: GeneService = get_gene_service(),
    orthogroup_service: OrthogroupService = get_orthogroup_service(),
    cache_repo: CacheRepository = get_cache_repository()
) -> DashboardService:
    """📊 Get dashboard service with injected dependencies"""
    if DashboardService is None:
        logger.warning("DashboardService not available, using mock")
        return None
    return DashboardService(
        species_service=species_service,
        gene_service=gene_service,
        orthogroup_service=orthogroup_service,
        cache_repo=cache_repo
    )

# ==========================================
# DATABASE DEPENDENCIES (Future)
# ==========================================

def get_database_session() -> Generator:
    """🗃️ Get database session (for future SQL implementation)"""
    # Future implementation for SQL database
    # db = SessionLocal()
    # try:
    #     yield db
    # finally:
    #     db.close()
    yield None

# ==========================================
# CONFIGURATION DEPENDENCIES
# ==========================================

def get_app_settings():
    """⚙️ Get application settings"""
    # Future implementation for configuration management
    return {
        "data_path": "app/data",
        "cache_ttl": 3600,
        "max_query_limit": 1000,
        "performance_targets": {
            "gene_search": 50,  # ms
            "species_lookup": 10,  # ms
            "orthogroup_retrieval": 100,  # ms
            "dashboard_load": 200  # ms
        }
    }

# ==========================================
# HEALTH CHECK DEPENDENCIES
# ==========================================

def check_service_health() -> dict:
    """🏥 Check health of all services"""
    health_status = {
        "api_layer": "healthy",
        "service_layer": "healthy",
        "data_access_layer": "healthy",
        "cache": "healthy"
    }
    
    try:
        # Test each service
        species_service = get_species_service()
        gene_service = get_gene_service()
        orthogroup_service = get_orthogroup_service()
        dashboard_service = get_dashboard_service()
        
        # Update status based on service availability
        if species_service is None:
            health_status["service_layer"] = "degraded"
        if gene_service is None:
            health_status["service_layer"] = "degraded"
        if orthogroup_service is None:
            health_status["service_layer"] = "degraded"
        if dashboard_service is None:
            health_status["service_layer"] = "degraded"
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        health_status["api_layer"] = "unhealthy"
    
    return health_status 