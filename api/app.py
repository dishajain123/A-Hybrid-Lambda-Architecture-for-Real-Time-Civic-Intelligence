#!/usr/bin/env python3
"""
REST API Service - Serves data to Dashboard
MongoDB (real-time) + MinIO (historical analytics)
"""

from fastapi import FastAPI, HTTPException
import logging
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient, DESCENDING
from minio import Minio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import sys
from pathlib import Path
# Line 1: At top with imports
from routers import geo_routes

# Ensure repo root is on sys.path for local runs and Docker
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.append(str(repo_root))
sys.path.append('/app')
from config.settings import Settings

app = FastAPI(title="News Pipeline API", version="1.0.0")
logger = logging.getLogger("news-pipeline-api")
app.include_router(geo_routes.router)
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connections
mongo_client = MongoClient(Settings.MONGODB_URI)
mongo_db = mongo_client[Settings.MONGODB_DB]
mongo_collection = mongo_db[Settings.MONGODB_COLLECTION]

minio_client = Minio(
    Settings.MINIO_ENDPOINT,
    access_key=Settings.MINIO_ACCESS_KEY,
    secret_key=Settings.MINIO_SECRET_KEY,
    secure=Settings.MINIO_SECURE
)


def _list_gold_objects(endpoint: str) -> List[Any]:
    """List all gold objects for a given endpoint, sorted by last_modified."""
    prefix = f"{endpoint}/"
    objects = list(minio_client.list_objects(Settings.MINIO_GOLD_BUCKET, prefix=prefix, recursive=True))
    if not objects:
        raise HTTPException(status_code=404, detail=f"No gold objects found for endpoint '{endpoint}'")
    return sorted(objects, key=lambda o: o.last_modified)


def _read_gold_object(object_name: str) -> Dict:
    """Read a specific gold object and return its parsed JSON data."""
    logger.info(f"GOLD READ {Settings.MINIO_GOLD_BUCKET}/{object_name}")
    response = minio_client.get_object(Settings.MINIO_GOLD_BUCKET, object_name)
    data = json.loads(response.read().decode('utf-8'))
    response.close()
    response.release_conn()
    return data


def _sentiment_dist(articles: List[Dict]) -> Dict[str, int]:
    dist = {"positive": 0, "neutral": 0, "negative": 0}
    for a in articles:
        s = a.get("sentiment", 0)
        if s > 0.1:
            dist["positive"] += 1
        elif s < -0.1:
            dist["negative"] += 1
        else:
            dist["neutral"] += 1
    return dist


def _avg_sentiment(articles: List[Dict]) -> float:
    sentiments = [a.get("sentiment", 0) for a in articles]
    return round(sum(sentiments) / len(sentiments), 3) if sentiments else 0.0


def _count_field(articles: List[Dict], field: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for a in articles:
        key = a.get(field, "unknown")
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def _top_items(articles: List[Dict], field: str, n: int) -> List[Dict[str, Any]]:
    counts = _count_field(articles, field)
    return [{"name": k, "count": v} for k, v in list(counts.items())[:n]]


def _time_series(articles: List[Dict]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for a in articles:
        date = a.get("publish_date")
        if date:
            try:
                dt = datetime.fromisoformat(date.replace("Z", "+00:00"))
                key = dt.strftime("%Y-%m-%dT%H:00")
                counts[key] = counts.get(key, 0) + 1
            except Exception:
                continue
    return dict(sorted(counts.items()))


def _trending_keywords(articles: List[Dict], n: int = 15) -> List[Dict[str, Any]]:
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "up", "about", "into", "is", "it", "as"
    }
    counts: Dict[str, int] = {}
    for a in articles:
        words = [w.strip(".,!?;:()[]{}") for w in a.get("title", "").lower().split()]
        for word in words:
            if word and len(word) > 3 and word not in stop_words:
                counts[word] = counts.get(word, 0) + 1
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]
    return [{"keyword": k, "count": v} for k, v in sorted_counts]


def _deduplicate_articles(articles: List[Dict]) -> List[Dict]:
    seen = set()
    unique: List[Dict] = []
    for article in articles:
        key = article.get("id") or article.get("url") or (
            article.get("title"), article.get("publish_date")
        )
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(article)
    return unique


def _aggregate_articles(payloads: List[Dict]) -> Dict:
    articles: List[Dict] = []
    endpoint = None
    for payload in payloads:
        endpoint = endpoint or payload.get("endpoint")
        if isinstance(payload.get("articles"), list):
            articles.extend(payload.get("articles", []))
        if payload.get("article"):
            articles.append(payload["article"])

    articles = _deduplicate_articles(articles)
    sorted_articles = sorted(
        articles,
        key=lambda x: (x.get("publish_date", ""), abs(x.get("sentiment", 0))),
        reverse=True
    )

    latest = sorted_articles[:20]
    top_positive = sorted(
        [a for a in articles if a.get("sentiment", 0) > 0.3],
        key=lambda x: x.get("sentiment", 0),
        reverse=True
    )[:10]
    top_negative = sorted(
        [a for a in articles if a.get("sentiment", 0) < -0.3],
        key=lambda x: x.get("sentiment", 0)
    )[:10]

    metrics = {
        "endpoint": endpoint,
        "total_articles": len(articles),
        "sentiment_distribution": _sentiment_dist(articles),
        "avg_sentiment": _avg_sentiment(articles),
        "category_breakdown": _count_field(articles, "category"),
        "top_authors": _top_items(articles, "author", 10),
        "source_countries": _count_field(articles, "source_country"),
        "top_sources": _top_items(articles, "source", 10),
        "languages": _count_field(articles, "language"),
        "time_series": _time_series(articles),
        "trending_keywords": _trending_keywords(articles, 15),
        "articles_with_sentiment": sum(1 for a in articles if a.get("sentiment", 0) != 0),
        "articles_with_images": sum(1 for a in articles if a.get("image")),
        "articles_with_video": sum(1 for a in articles if a.get("video"))
    }

    return {
        "layer": "gold",
        "endpoint": endpoint,
        "data_type": "articles",
        "metrics": metrics,
        "articles": sorted_articles,
        "article_count": len(sorted_articles),
        "featured": {
            "latest": latest,
            "most_positive": top_positive,
            "most_negative": top_negative,
            "trending": sorted_articles[:15]
        },
        "data_quality": {
            "articles_with_urls": sum(1 for a in articles if a.get("url")),
            "articles_with_authors": sum(1 for a in articles if a.get("author") != "Unknown"),
            "articles_with_images": sum(1 for a in articles if a.get("image")),
            "articles_with_known_sources": sum(1 for a in articles if a.get("source") != "Unknown"),
            "unique_sources": len(set(a.get("source") for a in articles if a.get("source"))),
            "completeness_score": round(
                sum(1 for a in articles if a.get("title")) / len(articles), 2
            ) if articles else 0.0,
            "date_range": {
                "earliest": min(
                    (a.get("publish_date") for a in articles if a.get("publish_date")),
                    default=None
                ),
                "latest": max(
                    (a.get("publish_date") for a in articles if a.get("publish_date")),
                    default=None
                )
            }
        }
    }


def _aggregate_urls(payloads: List[Dict]) -> Dict:
    urls: List[str] = []
    domains: List[str] = []
    endpoint = None
    for payload in payloads:
        endpoint = endpoint or payload.get("endpoint")
        urls.extend(payload.get("urls", []) or [])
        domains.extend(payload.get("domains", []) or [])
    unique_urls = list(dict.fromkeys(urls))
    unique_domains = list(dict.fromkeys(domains))
    return {
        "layer": "gold",
        "endpoint": endpoint,
        "data_type": "urls",
        "metrics": {
            "endpoint": endpoint,
            "total_articles": len(unique_urls),
            "sentiment_distribution": {"positive": 0, "neutral": len(unique_urls), "negative": 0},
            "category_breakdown": {"url_extraction": len(unique_urls)},
            "top_sources": [{"name": d, "count": 1} for d in unique_domains[:10]]
        },
        "urls": unique_urls,
        "domains": unique_domains,
        "data_quality": {
            "total_urls": len(unique_urls),
            "unique_domains": len(unique_domains),
            "valid_urls": len([u for u in unique_urls if isinstance(u, str) and u.startswith("http")])
        }
    }


def _aggregate_rss(payloads: List[Dict]) -> Dict:
    entries: List[Dict] = []
    endpoint = None
    for payload in payloads:
        endpoint = endpoint or payload.get("endpoint")
        rss_data = payload.get("rss_data")
        if rss_data:
            entries.append(rss_data)
    latest = entries[-1] if entries else {}
    return {
        "layer": "gold",
        "endpoint": endpoint,
        "data_type": "rss_feed",
        "metrics": {
            "endpoint": endpoint,
            "total_articles": len(entries),
            "sentiment_distribution": {"positive": 0, "neutral": len(entries), "negative": 0},
            "category_breakdown": {"rss_feed": len(entries)},
            "top_sources": [{"name": e.get("domain", "Unknown"), "count": 1} for e in entries[:10]]
        },
        "rss_entries": entries,
        "rss_data": latest,
        "data_quality": {
            "has_content": any(e.get("content_length", 0) > 0 for e in entries),
            "content_size_kb": round(sum(e.get("content_length", 0) for e in entries) / 1024, 2) if entries else 0
        }
    }


def _aggregate_healthcheck(payloads: List[Dict]) -> Dict:
    endpoint = None
    history: List[Dict] = []
    for payload in payloads:
        endpoint = endpoint or payload.get("endpoint")
        if payload.get("health_data"):
            history.append(payload.get("health_data"))
        else:
            history.append(payload)
    latest = history[-1] if history else {}
    aggregated = {
        "layer": "gold",
        "endpoint": endpoint,
        "data_type": "healthcheck",
        "metrics": {
            "endpoint": endpoint,
            "total_articles": len(history),
            "sentiment_distribution": {"positive": 0, "neutral": len(history), "negative": 0},
            "category_breakdown": {"system_health": len(history)},
            "top_sources": [{"name": "System Monitor", "count": 1}]
        },
        "history": history,
        "latest": latest
    }
    if isinstance(latest, dict):
        aggregated.update(latest)
    return aggregated


def _aggregate_geolocation(payloads: List[Dict]) -> Dict:
    endpoint = None
    locations: List[Dict] = []
    for payload in payloads:
        endpoint = endpoint or payload.get("endpoint")
        if payload.get("location_data"):
            locations.append(payload.get("location_data"))
    return {
        "layer": "gold",
        "endpoint": endpoint,
        "data_type": "geolocation",
        "metrics": {
            "endpoint": endpoint,
            "total_articles": len(locations),
            "sentiment_distribution": {"positive": 0, "neutral": len(locations), "negative": 0},
            "category_breakdown": {"geolocation": len(locations)},
            "top_sources": [{"name": "Geo API", "count": 1}]
        },
        "locations": locations
    }


def _aggregate_gold_payloads(payloads: List[Dict]) -> Dict:
    data_type = payloads[0].get("data_type", "unknown") if payloads else "unknown"
    if data_type in {"articles", "single_article"}:
        return _aggregate_articles(payloads)
    if data_type == "urls":
        return _aggregate_urls(payloads)
    if data_type == "rss_feed":
        return _aggregate_rss(payloads)
    if data_type == "healthcheck":
        return _aggregate_healthcheck(payloads)
    if data_type == "geolocation":
        return _aggregate_geolocation(payloads)
    return {
        "layer": "gold",
        "data_type": data_type,
        "history": payloads
    }


@app.get("/")
def root():
    """Health check"""
    return {
        "status": "healthy",
        "service": "news-pipeline-api",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/live/latest")
def get_latest_news(limit: int = 50):
    """Get latest news from MongoDB (live layer)"""
    try:
        documents = list(
            mongo_collection
            .find({}, {'_id': 0})
            .sort('created_at', DESCENDING)
            .limit(limit)
        )
        
        return {
            "count": len(documents),
            "data": documents
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/live/by-endpoint/{endpoint}")
def get_by_endpoint(endpoint: str, limit: int = 20):
    """Get news by specific endpoint"""
    try:
        documents = list(
            mongo_collection
            .find({'endpoint': endpoint}, {'_id': 0})
            .sort('created_at', DESCENDING)
            .limit(limit)
        )
        
        return {
            "endpoint": endpoint,
            "count": len(documents),
            "data": documents
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/live/stats")
def get_realtime_stats():
    """Get live statistics from MongoDB"""
    try:
        total = mongo_collection.count_documents({})
        
        # By endpoint
        pipeline = [
            {'$group': {'_id': '$endpoint', 'count': {'$sum': 1}}}
        ]
        by_endpoint = {
            doc['_id']: doc['count']
            for doc in mongo_collection.aggregate(pipeline)
        }
        
        # Last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        last_hour = mongo_collection.count_documents({
            'created_at': {'$gte': one_hour_ago}
        })
        
        # Last 24 hours
        one_day_ago = datetime.utcnow() - timedelta(hours=24)
        last_24h = mongo_collection.count_documents({
            'created_at': {'$gte': one_day_ago}
        })
        
        return {
            "total_documents": total,
            "last_hour": last_hour,
            "last_24_hours": last_24h,
            "by_endpoint": by_endpoint
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch/buckets")
def get_minio_buckets():
    """List MinIO buckets (batch layer)"""
    try:
        buckets = minio_client.list_buckets()
        return {
            "buckets": [
                {
                    "name": b.name,
                    "created": b.creation_date.isoformat()
                }
                for b in buckets
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch/objects/{bucket}")
def get_bucket_objects(bucket: str, prefix: str = "", limit: int = 20):
    """List objects in MinIO bucket"""
    try:
        objects = minio_client.list_objects(
            bucket,
            prefix=prefix,
            recursive=True
        )
        
        results = []
        for obj in objects:
            results.append({
                "key": obj.object_name,
                "size": obj.size,
                "last_modified": obj.last_modified.isoformat()
            })
            
            if len(results) >= limit:
                break
        
        return {
            "bucket": bucket,
            "count": len(results),
            "objects": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch/read/{bucket}/{path:path}")
def read_object(bucket: str, path: str):
    """Read specific object from MinIO"""
    try:
        logger.info(f"MINIO READ {bucket}/{path}")
        response = minio_client.get_object(bucket, path)
        data = json.loads(response.read().decode('utf-8'))
        response.close()
        response.release_conn()
        
        return {
            "bucket": bucket,
            "path": path,
            "data": data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/summary")
def get_analytics_summary():
    """Get MinIO gold analytics summary (historical only)"""
    try:
        gold_count = sum(1 for _ in minio_client.list_objects(
            Settings.MINIO_GOLD_BUCKET, recursive=True
        ))

        return {
            "gold_layer": {
                "gold_objects": gold_count,
                "storage": "minio",
                "retention": "permanent"
            },
            "note": "Historical analytics only (GOLD layer)"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/{endpoint}")
def get_analytics_history(endpoint: str, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """Get aggregated historical analytics from all gold objects."""
    try:
        def _parse_date(value: str):
            try:
                return datetime.fromisoformat(value).date()
            except Exception:
                raise HTTPException(status_code=400, detail=f"Invalid date format: {value}")

        start = _parse_date(start_date) if start_date else None
        end = _parse_date(end_date) if end_date else None

        objects = _list_gold_objects(endpoint)
        if start or end:
            filtered = []
            for obj in objects:
                obj_date = obj.last_modified.date()
                if start and obj_date < start:
                    continue
                if end and obj_date > end:
                    continue
                filtered.append(obj)
            objects = filtered
            if not objects:
                raise HTTPException(status_code=404, detail="No gold objects found for selected date range")

        payloads = [_read_gold_object(obj.object_name) for obj in objects]
        aggregated = _aggregate_gold_payloads(payloads)
        if objects:
            aggregated["last_modified"] = objects[-1].last_modified.isoformat()
            aggregated["latest_object"] = objects[-1].object_name
        if payloads and isinstance(payloads[-1], dict) and payloads[-1].get("analytics_time"):
            aggregated["analytics_time"] = payloads[-1].get("analytics_time")
        history = [
            {
                "object": obj.object_name,
                "last_modified": obj.last_modified.isoformat()
            }
            for obj in objects
        ]
        return {
            "endpoint": endpoint,
            "bucket": Settings.MINIO_GOLD_BUCKET,
            "objects": history,
            "data": aggregated
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/live/search")
def search_news(q: str, limit: int = 20):
    """Search news in MongoDB (live layer)"""
    try:
        # Text search in metadata
        query = {
            '$or': [
                {'metadata.sample_title': {'$regex': q, '$options': 'i'}},
                {'metadata.title': {'$regex': q, '$options': 'i'}},
                {'metadata.location': {'$regex': q, '$options': 'i'}}
            ]
        }
        
        documents = list(
            mongo_collection
            .find(query, {'_id': 0})
            .sort('created_at', DESCENDING)
            .limit(limit)
        )
        
        return {
            "query": q,
            "count": len(documents),
            "results": documents
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=Settings.API_HOST,
        port=Settings.API_PORT,
        log_level="info"
    )
