from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
import os
import tempfile
import shutil
import uuid
import json
import pathlib
import base64
import logging
from Bio import Phylo

# ETE3 imports with fallback
try:
    from ete3 import Tree, TreeStyle, NodeStyle, faces, AttrFace
    HAS_ETE3 = True
    logger = logging.getLogger(__name__)
    logger.info("ETE3 successfully imported")
except ImportError as e:
    HAS_ETE3 = False
    logger = logging.getLogger(__name__)
    logger.warning(f"ETE3 not available: {e}")

from ..models.phylo import (
    PhyloNodeData, TreeData, NodeMutation,
    ETESearchRequest, ETESearchResponse, ETESearchResult
)

router = APIRouter(prefix="/api/phylo", tags=["phylo"])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.get("/status", response_model=Dict[str, Any])
async def get_phylo_status():
    """Get phylo API status and capabilities"""
    capabilities = {
        "upload": True,
        "basic_parsing": True,
        "ete3_available": HAS_ETE3,
        "rerooting": HAS_ETE3,
        "annotation": HAS_ETE3,
        "comparison": HAS_ETE3,
        "analysis": HAS_ETE3,
        "pattern_search": HAS_ETE3,
        "image_rendering": HAS_ETE3
    }
    
    if HAS_ETE3:
        try:
            # Test ETE3 functionality
            test_tree = Tree("(A:1,B:1);")
            capabilities["ete3_test"] = "passed"
        except Exception as e:
            capabilities["ete3_test"] = f"failed: {str(e)}"
    
    return {
        "success": True,
        "phylo_api_version": "2.0",
        "capabilities": capabilities,
        "ete3_available": HAS_ETE3
    }

@router.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {"message": "Phylo router is working!"}

@router.post("/ete-search", response_model=ETESearchResponse)
async def ete_phylogenetic_search(request: ETESearchRequest):
    """Advanced phylogenetic search using ETE toolkit"""
    if not HAS_ETE3:
        return ETESearchResponse(
            success=False,
            query=request.query,
            search_type=request.search_type,
            results=[],
            total_results=0,
            message="ETE3 toolkit not available. Please install: conda install -c etetoolkit ete3"
        )
    
    try:
        logger.info(f"ETE phylogenetic search: {request.search_type} for '{request.query}'")
        
        # Basic implementation - you can expand this
        results = []
        
        return ETESearchResponse(
            success=True,
            query=request.query,
            search_type=request.search_type,
            results=results,
            total_results=len(results),
            message=f"Found {len(results)} results (basic implementation)"
        )
        
    except Exception as e:
        logger.error(f"ETE search error: {str(e)}", exc_info=True)
        return ETESearchResponse(
            success=False,
            query=request.query,
            search_type=request.search_type,
            results=[],
            total_results=0,
            message=f"Search failed: {str(e)}"
        )
