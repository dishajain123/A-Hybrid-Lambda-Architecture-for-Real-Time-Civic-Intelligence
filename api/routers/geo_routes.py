"""
Geo Coordinates Router for News Pipeline API
Place this file at: news-realtime-pipeline/api/routers/geo_routes.py

This router handles all geographic/location-based endpoints.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from pymongo import MongoClient
import logging
import sys
from pathlib import Path

# Add repo root to path to import settings (local + Docker)
repo_root = Path(__file__).resolve().parents[2]
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))
sys.path.append('/app')
from config.settings import Settings

logger = logging.getLogger("geo-routes")

# Create router
router = APIRouter(
    prefix="/geo",
    tags=["Geography"],
    responses={404: {"description": "Not found"}}
)

# Database connection
mongo_client = MongoClient(Settings.MONGODB_URI)
mongo_db = mongo_client[Settings.MONGODB_DB]
mongo_collection = mongo_db[Settings.MONGODB_COLLECTION]


# ========================================
# PYDANTIC MODELS
# ========================================

class GeoCoordinate(BaseModel):
    """Schema for geocoded location data"""
    city: str
    latitude: float
    longitude: float
    region: Optional[str] = ""
    country: str = "India"
    article_count: int = 0
    avg_sentiment: float = 0.0
    
    class Config:
        schema_extra = {
            "example": {
                "city": "Mumbai",
                "latitude": 19.0760,
                "longitude": 72.8777,
                "region": "Maharashtra",
                "country": "India",
                "article_count": 45,
                "avg_sentiment": 0.15
            }
        }


# ========================================
# ENDPOINTS
# ========================================

@router.get("/coordinates", response_model=List[GeoCoordinate])
async def get_geo_coordinates(
    limit: int = Query(500, ge=1, le=1000, description="Maximum number of locations to return"),
    min_articles: int = Query(1, ge=1, description="Minimum number of articles per location")
):
    """
    Get geocoded location data with article counts and sentiment
    
    This endpoint aggregates news articles by location and returns:
    - City name and coordinates
    - Number of articles mentioning that location
    - Average sentiment score for that location
    
    Args:
        limit: Maximum number of locations to return (1-1000)
        min_articles: Only return locations with at least this many articles
    
    Returns:
        List of geocoded locations sorted by article count (descending)
    
    Example:
        GET /geo/coordinates?limit=10&min_articles=5
    """
    try:
        # MongoDB aggregation pipeline
        pipeline = [
            # Filter geo_coordinates records with valid coordinates (nested in data)
            {
                "$match": {
                    "endpoint": "geo_coordinates",
                    "data.latitude": {"$exists": True, "$ne": None},
                    "data.longitude": {"$exists": True, "$ne": None}
                }
            },
            # Normalize fields for grouping
            {
                "$project": {
                    "latitude": "$data.latitude",
                    "longitude": "$data.longitude",
                    "region": "$data.region",
                    "country": "$data.country",
                    "city": {
                        "$ifNull": [
                            "$data.city",
                            {
                                "$ifNull": [
                                    "$data.searched_location",
                                    "$metadata.location"
                                ]
                            }
                        ]
                    },
                    "sentiment": {"$ifNull": ["$data.sentiment", 0]}
                }
            },
            # Drop records without city after normalization
            {
                "$match": {
                    "city": {"$ne": None}
                }
            },
            # Group by city and calculate statistics
            {
                "$group": {
                    "_id": "$city",
                    "latitude": {"$first": "$latitude"},
                    "longitude": {"$first": "$longitude"},
                    "region": {"$first": "$region"},
                    "country": {"$first": "$country"},
                    "article_count": {"$sum": 1},
                    "avg_sentiment": {"$avg": "$sentiment"}
                }
            },
            # Filter by minimum article count
            {
                "$match": {
                    "article_count": {"$gte": min_articles}
                }
            },
            # Sort by article count (most active locations first)
            {
                "$sort": {"article_count": -1}
            },
            # Limit results
            {
                "$limit": limit
            },
            # Format output to match schema
            {
                "$project": {
                    "_id": 0,
                    "city": "$_id",
                    "latitude": 1,
                    "longitude": 1,
                    "region": {"$ifNull": ["$region", ""]},
                    "country": {"$ifNull": ["$country", "India"]},
                    "article_count": 1,
                    "avg_sentiment": {"$round": ["$avg_sentiment", 2]}
                }
            }
        ]
        
        # Execute aggregation
        results = list(mongo_collection.aggregate(pipeline))
        
        logger.info(f"Geo coordinates query returned {len(results)} locations")
        return results
        
    except Exception as e:
        logger.error(f"Error fetching geo coordinates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch geo coordinates: {str(e)}"
        )


@router.get("/cities", response_model=List[str])
async def get_cities(
    limit: int = Query(100, ge=1, le=500)
):
    """
    Get list of unique cities with news coverage
    
    Args:
        limit: Maximum number of cities to return
    
    Returns:
        List of city names sorted alphabetically
    """
    try:
        cities = mongo_collection.distinct("data.city", {
            "data.city": {"$exists": True, "$ne": None}
        })
        
        # Sort and limit
        cities = sorted(cities)[:limit]
        
        logger.info(f"Returned {len(cities)} unique cities")
        return cities
        
    except Exception as e:
        logger.error(f"Error fetching cities: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regions", response_model=List[str])
async def get_regions(
    limit: int = Query(50, ge=1, le=200)
):
    """
    Get list of unique regions/states with news coverage
    
    Args:
        limit: Maximum number of regions to return
    
    Returns:
        List of region names sorted alphabetically
    """
    try:
        regions = mongo_collection.distinct("data.region", {
            "data.region": {"$exists": True, "$ne": None}
        })
        
        # Sort and limit
        regions = sorted(regions)[:limit]
        
        logger.info(f"Returned {len(regions)} unique regions")
        return regions
        
    except Exception as e:
        logger.error(f"Error fetching regions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_geo_stats():
    """
    Get geographic coverage statistics
    
    Returns:
        Summary statistics about geographic coverage
    """
    try:
        total_articles = mongo_collection.count_documents({})
        geocoded_articles = mongo_collection.count_documents({
            "endpoint": "geo_coordinates",
            "data.latitude": {"$exists": True, "$ne": None},
            "data.longitude": {"$exists": True, "$ne": None}
        })
        
        unique_cities = len(mongo_collection.distinct("data.city", {
            "data.city": {"$exists": True, "$ne": None}
        }))
        
        unique_regions = len(mongo_collection.distinct("data.region", {
            "data.region": {"$exists": True, "$ne": None}
        }))
        
        geocoding_rate = (geocoded_articles / total_articles * 100) if total_articles > 0 else 0
        
        stats = {
            "total_articles": total_articles,
            "geocoded_articles": geocoded_articles,
            "geocoding_rate_percent": round(geocoding_rate, 2),
            "unique_cities": unique_cities,
            "unique_regions": unique_regions
        }
        
        logger.info(f"Geo stats: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error fetching geo stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========================================
# HEALTH CHECK
# ========================================

@router.get("/health")
async def health_check():
    """Check if geo router is healthy"""
    try:
        # Test MongoDB connection
        mongo_db.command("ping")
        return {
            "status": "healthy",
            "service": "geo_routes",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "geo_routes",
            "database": "disconnected",
            "error": str(e)
        }
