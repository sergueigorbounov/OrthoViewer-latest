"""
📊 Dashboard Routes - API Layer
==============================

HTTP endpoints for dashboard and analytics data.
Aggregated statistics and visualization data.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
import logging

# Import service layer (will be created)
try:
    from app.services.analytics.dashboard_service import DashboardService
    from app.api.dependencies import get_dashboard_service
except ImportError:
    # Temporary fallback for development
    DashboardService = None
    def get_dashboard_service():
        return None

# Import models
try:
    from app.models.dto.dashboard import DashboardResponse, SystemStats
except ImportError:
    # Temporary fallback
    DashboardResponse = Dict[str, Any]
    SystemStats = Dict[str, Any]

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
logger = logging.getLogger(__name__)

@router.get("/", response_model=DashboardResponse)
async def get_dashboard_overview(
    refresh_cache: bool = Query(False, description="Force refresh cached data"),
    service: DashboardService = Depends(get_dashboard_service)
) -> DashboardResponse:
    """
    📊 Get comprehensive dashboard overview
    
    Performance target: < 200ms
    """
    try:
        if service is None:
            # Temporary mock data
            return {
                "system_stats": {
                    "total_species": 3,
                    "total_genes": 87542,
                    "total_orthogroups": 18780,
                    "last_updated": "2024-01-15T10:30:00Z"
                },
                "species_distribution": {
                    "arabidopsis": 27416,
                    "rice": 35679,
                    "maize": 24447
                },
                "orthogroup_stats": {
                    "avg_genes_per_group": 4.66,
                    "max_genes_per_group": 234,
                    "single_copy_groups": 12450,
                    "multi_copy_groups": 6330
                },
                "recent_activity": [
                    {
                        "action": "data_update",
                        "timestamp": "2024-01-15T10:30:00Z",
                        "details": "Arabidopsis dataset updated"
                    }
                ],
                "performance_metrics": {
                    "avg_query_time": 23.5,
                    "cache_hit_rate": 0.87,
                    "active_users": 12
                }
            }
        
        dashboard = await service.get_dashboard_overview(refresh_cache=refresh_cache)
        return dashboard
        
    except Exception as e:
        logger.error(f"Error getting dashboard overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")

@router.get("/stats", response_model=SystemStats)
async def get_system_statistics(
    service: DashboardService = Depends(get_dashboard_service)
) -> SystemStats:
    """
    📈 Get detailed system statistics
    
    Performance target: < 100ms
    """
    try:
        if service is None:
            # Temporary mock data
            return {
                "species": {
                    "total": 3,
                    "by_type": {
                        "model_organism": 1,
                        "crop_plant": 2
                    }
                },
                "genes": {
                    "total": 87542,
                    "avg_length": 1456,
                    "by_species": {
                        "arabidopsis": 27416,
                        "rice": 35679,
                        "maize": 24447
                    }
                },
                "orthogroups": {
                    "total": 18780,
                    "single_copy": 12450,
                    "multi_copy": 6330,
                    "avg_conservation": 0.78
                },
                "data_quality": {
                    "completeness": 0.95,
                    "consistency": 0.98,
                    "last_validation": "2024-01-15T08:00:00Z"
                }
            }
        
        stats = await service.get_system_statistics()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting system statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system statistics")

@router.get("/species-comparison", response_model=Dict[str, Any])
async def get_species_comparison(
    species_list: Optional[str] = Query(None, description="Comma-separated species IDs"),
    metric: str = Query("gene_count", regex="^(gene_count|orthogroup_count|similarity)$"),
    service: DashboardService = Depends(get_dashboard_service)
) -> Dict[str, Any]:
    """
    🔄 Get species comparison data
    
    Performance target: < 150ms
    """
    try:
        if service is None:
            # Temporary mock data
            species_ids = species_list.split(",") if species_list else ["arabidopsis", "rice", "maize"]
            
            comparison_data = {
                "metric": metric,
                "species": species_ids,
                "data": {}
            }
            
            if metric == "gene_count":
                comparison_data["data"] = {
                    "arabidopsis": 27416,
                    "rice": 35679,
                    "maize": 24447
                }
            elif metric == "orthogroup_count":
                comparison_data["data"] = {
                    "arabidopsis": 16234,
                    "rice": 18456,
                    "maize": 15670
                }
            else:  # similarity
                comparison_data["data"] = {
                    "arabidopsis_rice": 0.75,
                    "arabidopsis_maize": 0.68,
                    "rice_maize": 0.82
                }
            
            return comparison_data
        
        species_ids = species_list.split(",") if species_list else None
        comparison = await service.get_species_comparison(species_ids=species_ids, metric=metric)
        return comparison
        
    except Exception as e:
        logger.error(f"Error getting species comparison: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve species comparison")

@router.get("/gene-families", response_model=List[Dict[str, Any]])
async def get_top_gene_families(
    limit: int = Query(20, ge=1, le=100),
    by_size: bool = Query(True, description="Sort by family size"),
    service: DashboardService = Depends(get_dashboard_service)
) -> List[Dict[str, Any]]:
    """
    👨‍👩‍👧‍👦 Get top gene families
    
    Performance target: < 100ms
    """
    try:
        if service is None:
            # Temporary mock data
            families = [
                {
                    "family_id": "PF00004",
                    "name": "ATPase family",
                    "gene_count": 234,
                    "species_count": 3,
                    "description": "ATP-binding cassette transporter"
                },
                {
                    "family_id": "PF00067",
                    "name": "Cytochrome P450",
                    "gene_count": 198,
                    "species_count": 3,
                    "description": "Cytochrome P450 superfamily"
                },
                {
                    "family_id": "PF00106",
                    "name": "Transcription factor",
                    "gene_count": 167,
                    "species_count": 3,
                    "description": "Transcriptional regulatory protein"
                }
            ]
            
            if by_size:
                families.sort(key=lambda x: x["gene_count"], reverse=True)
            
            return families[:limit]
        
        families = await service.get_top_gene_families(limit=limit, by_size=by_size)
        return families
        
    except Exception as e:
        logger.error(f"Error getting gene families: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve gene families")

@router.get("/search-trends", response_model=Dict[str, Any])
async def get_search_trends(
    days: int = Query(30, ge=1, le=365),
    service: DashboardService = Depends(get_dashboard_service)
) -> Dict[str, Any]:
    """
    📈 Get search trends and usage analytics
    
    Performance target: < 100ms
    """
    try:
        if service is None:
            # Temporary mock data
            return {
                "period_days": days,
                "total_searches": 1245,
                "top_queries": [
                    {"query": "AT1G01010", "count": 87, "type": "gene_id"},
                    {"query": "arabidopsis", "count": 65, "type": "species"},
                    {"query": "NAC", "count": 43, "type": "gene_name"},
                    {"query": "OG0000001", "count": 32, "type": "orthogroup"}
                ],
                "daily_counts": [
                    {"date": "2024-01-15", "searches": 45},
                    {"date": "2024-01-14", "searches": 38},
                    {"date": "2024-01-13", "searches": 52}
                ],
                "search_types": {
                    "gene_search": 0.45,
                    "species_lookup": 0.25,
                    "orthogroup_query": 0.20,
                    "dashboard_view": 0.10
                }
            }
        
        trends = await service.get_search_trends(days=days)
        return trends
        
    except Exception as e:
        logger.error(f"Error getting search trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve search trends")

@router.get("/performance", response_model=Dict[str, Any])
async def get_performance_metrics(
    service: DashboardService = Depends(get_dashboard_service)
) -> Dict[str, Any]:
    """
    ⚡ Get real-time performance metrics
    
    Performance target: < 50ms
    """
    try:
        if service is None:
            # Temporary mock data
            return {
                "response_times": {
                    "gene_search": 23.5,
                    "species_lookup": 8.2,
                    "orthogroup_retrieval": 45.7,
                    "dashboard_load": 156.3
                },
                "throughput": {
                    "requests_per_minute": 45,
                    "concurrent_users": 8
                },
                "cache_performance": {
                    "hit_rate": 0.87,
                    "miss_rate": 0.13,
                    "eviction_rate": 0.02
                },
                "targets_met": {
                    "gene_search": True,
                    "species_lookup": True,
                    "orthogroup_retrieval": True,
                    "dashboard_load": True
                }
            }
        
        metrics = await service.get_performance_metrics()
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve performance metrics")