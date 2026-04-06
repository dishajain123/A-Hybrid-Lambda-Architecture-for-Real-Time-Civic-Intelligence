"""
API Client — tries the real FastAPI backend first,
falls back to dummy_data transparently on failure.
"""
import logging
import requests
import streamlit as st
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from utils.constants import API_BASE_URL
except ImportError:
    API_BASE_URL = "http://localhost:8000"

import utils.dummy_data as _dummy


class APIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.session  = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self._online  = None   # None = not yet tested

    # ── Connectivity ──────────────────────────────────────────────────────────
    def health_check(self) -> bool:
        try:
            r = self.session.get(f"{self.base_url}/", timeout=4)
            self._online = r.status_code == 200
        except Exception:
            self._online = False
        return self._online

    def _is_online(self) -> bool:
        if self._online is None:
            self.health_check()
        return self._online

    # ── Low-level request ────────────────────────────────────────────────────
    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        if not self._is_online():
            return None
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            r = self.session.get(url, params=params, timeout=20)
            r.raise_for_status()
            return r.json()
        except Exception as exc:
            logger.warning("Backend request failed (%s): %s", url, exc)
            self._online = False
            return None

    # ── Public API ────────────────────────────────────────────────────────────
    def get_endpoint_articles(self, endpoint: str, limit: int = 50, **kwargs) -> List[Dict]:
        if endpoint == "geo_coordinates":
            return self.get_geo_coordinates(limit=limit)

        data = self._get(f"/api/live/by-endpoint/{endpoint}", {"limit": limit, **kwargs})
        articles = self._extract_articles(endpoint, data)
        if articles:
            return articles[:limit]

        # ── Dummy fallback ──────────────────────────────────────────────────
        if endpoint in ("search_news", "top_news"):
            return _dummy.get_articles(limit=limit, **{k: v for k, v in kwargs.items() if k == "category"})
        if endpoint == "extract_news":
            return _dummy.get_articles(limit=1)
        if endpoint == "feed_rss":
            return []
        return _dummy.get_articles(limit=limit)

    def get_geo_coordinates(self, limit: int = 500, min_articles: int = None) -> List[Dict]:
        params = {"limit": limit}
        if min_articles:
            params["min_articles"] = min_articles
        data = self._get("/geo/coordinates", params)
        if isinstance(data, list) and data:
            return data
        if isinstance(data, dict):
            for key in ("locations", "data", "geo_data"):
                if isinstance(data.get(key), list):
                    return data[key]
        return _dummy.get_geo_data()

    def search_news(self, query=None, category=None,
                    sentiment_min=None, sentiment_max=None, limit=50):
        params = {"q": query, "limit": limit}
        params = {k: v for k, v in params.items() if v is not None}
        data = self._get("/api/live/search", params)
        if data:
            return data
        arts = _dummy.get_articles(
            limit=limit,
            category=category or "",
            sentiment_min=sentiment_min or -1.0,
            sentiment_max=sentiment_max or 1.0,
        )
        if query:
            q = query.lower()
            arts = [a for a in arts
                    if q in a.get("title","").lower() or q in a.get("text","").lower()]
        return {"articles": arts, "total_count": len(arts)}

    def get_top_news(self, category="all", limit=20):
        data = self._get("/api/live/by-endpoint/top_news", {"limit": limit})
        if data:
            return data
        return {"articles": _dummy.get_top_news(limit=limit)}

    def get_article_details(self, article_id: str):
        arts = self.get_endpoint_articles("extract_news", limit=200)
        for a in arts:
            if str(a.get("id")) == str(article_id) or a.get("url") == article_id:
                return a
        return _dummy.get_article_by_id(article_id)

    def get_metrics_summary(self):
        data = self._get("/api/analytics/summary")
        return data if data else _dummy.get_metrics()

    def get_analytics_data(self, endpoint: str):
        data = self._get(f"/api/analytics/{endpoint}")
        return (data or {}).get("data")

    def get_analytics_history(self, endpoint: str, **kwargs):
        data = self._get(f"/api/analytics/{endpoint}", kwargs or None)
        return data

    def read_object(self, bucket: str, path: str):
        return self._get(f"/api/batch/read/{bucket}/{path}")

    # ── Extraction helpers ───────────────────────────────────────────────────
    def _extract_articles(self, endpoint: str, data: Any) -> List[Dict]:
        if not data:
            return []
        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            inner = data.get("data", data)

            if endpoint == "search_news":
                if isinstance(inner, list):
                    result = []
                    for doc in inner:
                        payload = doc.get("data", doc) if isinstance(doc, dict) else doc
                        news = payload.get("news", []) if isinstance(payload, dict) else []
                        result.extend(news if isinstance(news, list) else [])
                    return result
                if isinstance(inner, dict):
                    return inner.get("news", [])

            if endpoint == "top_news":
                if isinstance(inner, list):
                    result = []
                    for doc in inner:
                        payload = doc.get("data", doc) if isinstance(doc, dict) else doc
                        if isinstance(payload, dict):
                            for key in ("articles", "top_news", "news"):
                                if isinstance(payload.get(key), list):
                                    result.extend(payload[key])
                                    break
                    return result
                if isinstance(inner, dict):
                    for key in ("articles", "top_news", "news"):
                        if isinstance(inner.get(key), list):
                            return inner[key]

            for key in ("articles", "news", "results", "locations"):
                if isinstance(data.get(key), list):
                    return data[key]
        return []


# ── Singleton ─────────────────────────────────────────────────────────────────
_client: Optional[APIClient] = None

def get_client() -> APIClient:
    global _client
    if _client is None:
        _client = APIClient()
        online = _client.health_check()
        if online:
            st.sidebar.success("✅ Backend connected", icon="✅")
        else:
            st.sidebar.info("📦 Using local data (backend offline)", icon="ℹ️")
    return _client

def reset_client():
    global _client
    _client = None
