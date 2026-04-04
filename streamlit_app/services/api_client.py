"""
API Client for communicating with FastAPI backend
Handles all backend data fetching with proper error handling
"""

import requests
import streamlit as st
from typing import Dict, List, Optional, Any
from utils.constants import API_BASE_URL
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """Client for FastAPI backend communication"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Streamlit-Frontend/1.0'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """Make HTTP request to backend with error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to {url}")
            st.error(f"❌ Cannot connect to backend at {self.base_url}. Please check if the API is running.")
            return None
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout connecting to {url}")
            st.error("⏱️ Backend request timed out. Please try again.")
            return None
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {url}")
            st.error(f"❌ Backend error: {e.response.status_code} - {e.response.text}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            st.error(f"❌ Unexpected error: {str(e)}")
            return None
            
        except ValueError as e:
            logger.error(f"Invalid JSON response from {url}: {str(e)}")
            st.error("❌ Invalid response from backend. Please check API data format.")
            return None
    
    def health_check(self) -> bool:
        """Check if API is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_endpoint_articles(self, endpoint: str, limit: int = 50, **kwargs) -> Optional[List[Dict]]:
        """
        Fetch articles from any backend endpoint
        
        Supported endpoints:
        - search_news: Full-text search with filtering
        - top_news: Featured/trending articles
        - geo_coordinates: Geocoded location data
        - extract_news: Detailed article extraction
        - feed_rss: RSS feed data
        
        Args:
            endpoint: API endpoint name
            limit: Maximum number of results
            **kwargs: Additional query parameters (category, sentiment_min, etc.)
        
        Returns:
            List of articles/data or None if error
        """
        # Geo endpoints live under /geo
        if endpoint == "geo_coordinates":
            return self.get_geo_coordinates(limit=limit, min_articles=kwargs.get("min_articles"))

        params = {'limit': limit, **kwargs}
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        data = self._make_request(f"/api/live/by-endpoint/{endpoint}", params=params)
        
        if data is None:
            return []
        
        # Prefer normalized articles when possible
        if isinstance(data, dict) and 'data' in data:
            normalized = self._normalize_endpoint_data(endpoint, data)
            if normalized:
                return normalized
            if isinstance(data['data'], list):
                return data['data']
        
        # Handle different response structures
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if 'articles' in data:
                return data['articles']
            elif 'results' in data:
                return data['results']
            elif 'locations' in data:
                return data['locations']
            else:
                return data
        
        return []
    
    def get_geo_coordinates(self, limit: int = 500, min_articles: Optional[int] = None) -> Optional[List[Dict]]:
        """
        Fetch geocoded location data from backend
        
        Returns:
            List of location objects with structure:
            {
                'city': str,
                'latitude': float,
                'longitude': float,
                'region': str,
                'country': str,
                'article_count': int,
                'avg_sentiment': float
            }
        """
        params = {'limit': limit, 'min_articles': min_articles}
        params = {k: v for k, v in params.items() if v is not None}
        data = self._make_request("/geo/coordinates", params=params)
        
        if data is None:
            return []
        
        # Handle response structure
        if isinstance(data, list):
            # Already in correct format
            return data
        elif isinstance(data, dict):
            # Extract from nested structure
            if 'locations' in data:
                return data['locations']
            elif 'data' in data:
                return data['data']
            elif 'geo_data' in data:
                return data['geo_data']
        
        logger.warning(f"Unexpected geo_coordinates response structure: {type(data)}")
        return []
    
    def search_news(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        sentiment_min: Optional[float] = None,
        sentiment_max: Optional[float] = None,
        limit: int = 50
    ) -> Optional[Dict]:
        """
        Search news articles with filters
        
        Returns:
            Dict with structure:
            {
                'articles': List[Dict],
                'total_count': int,
                'sentiment_distribution': Dict,
                'category_breakdown': Dict
            }
        """
        # Backend supports q + limit for live search
        params = {'q': query, 'limit': limit}
        params = {k: v for k, v in params.items() if v is not None}
        return self._make_request("/api/live/search", params=params)
    
    def get_top_news(self, category: str = "all", limit: int = 20) -> Optional[Dict]:
        """
        Get featured/top news articles
        
        Args:
            category: 'all', 'positive', 'negative', or specific category
            limit: Number of articles
        
        Returns:
            Dict with featured articles and metadata
        """
        params = {'limit': limit}
        return self._make_request("/api/live/by-endpoint/top_news", params=params)
    
    def get_article_details(self, article_id: str) -> Optional[Dict]:
        """Get detailed information for a specific article"""
        articles = self.get_endpoint_articles("extract_news", limit=200)
        for article in articles or []:
            if article.get("id") == article_id or article.get("url") == article_id:
                return article
        return None
    
    def get_metrics_summary(self) -> Optional[Dict]:
        """
        Get aggregated metrics across all data
        
        Returns:
            Dict with summary statistics
        """
        return self._make_request("/metrics/summary")

    def get_analytics_data(self, endpoint: str) -> Optional[Dict]:
        """
        Get historical analytics data (gold layer) for a given endpoint.

        Returns:
            Aggregated analytics payload (data field) or None if error
        """
        response = self._make_request(f"/api/analytics/{endpoint}")
        if not response:
            return None
        return response.get("data")

    def get_analytics_history(
        self,
        endpoint: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Optional[Dict]:
        """Get full analytics response including object history."""
        params = {"start_date": start_date, "end_date": end_date}
        params = {k: v for k, v in params.items() if v is not None}
        return self._make_request(f"/api/analytics/{endpoint}", params=params)

    def read_object(self, bucket: str, path: str) -> Optional[Dict]:
        """Read specific object from MinIO via API."""
        return self._make_request(f"/api/batch/read/{bucket}/{path}")

    def _normalize_endpoint_data(self, endpoint: str, response: Optional[Dict]) -> List[Dict]:
        """
        Normalize API response into a list of article-like dicts.

        - Extracts payloads from nested 'data' field
        - Handles different endpoint structures
        - Returns fresh data ordered by ingestion/publish time
        """
        if not response or 'data' not in response:
            return []

        documents = response.get('data', [])
        normalized: List[Dict] = []

        for doc in documents:
            payload = doc.get('data', {}) if isinstance(doc, dict) else doc
            timestamp = doc.get('timestamp') if isinstance(doc, dict) else None

            if endpoint == "search_news":
                if isinstance(payload, dict):
                    articles = payload.get('news', [])
                    if isinstance(articles, list):
                        for article in articles:
                            if isinstance(article, dict):
                                if timestamp and 'ingestion_time' not in article:
                                    article['ingestion_time'] = timestamp
                                normalized.append(article)

            elif endpoint == "top_news":
                if isinstance(payload, dict):
                    articles = (
                        payload.get('articles') or
                        payload.get('top_news') or
                        payload.get('news') or []
                    )

                    if isinstance(articles, list):
                        for article in articles:
                            if isinstance(article, dict):
                                if timestamp and 'ingestion_time' not in article:
                                    article['ingestion_time'] = timestamp
                                normalized.append(article)
                    elif payload.get('title'):
                        if timestamp and 'ingestion_time' not in payload:
                            payload['ingestion_time'] = timestamp
                        normalized.append(payload)

            elif endpoint == "extract_news":
                if isinstance(payload, dict) and payload:
                    if timestamp and 'ingestion_time' not in payload:
                        payload['ingestion_time'] = timestamp
                    normalized.append(payload)

            elif endpoint == "extract_news_links":
                if isinstance(payload, dict) and payload:
                    if timestamp and 'ingestion_time' not in payload:
                        payload['ingestion_time'] = timestamp
                    normalized.append(payload)

            elif endpoint == "feed_rss":
                if isinstance(payload, dict) and payload:
                    if timestamp and 'ingestion_time' not in payload:
                        payload['ingestion_time'] = timestamp
                    normalized.append(payload)

            elif endpoint == "geo_coordinates":
                if isinstance(payload, dict) and payload:
                    if timestamp and 'ingestion_time' not in payload:
                        payload['ingestion_time'] = timestamp
                    normalized.append(payload)
            else:
                if isinstance(payload, dict) and payload:
                    if timestamp and 'ingestion_time' not in payload:
                        payload['ingestion_time'] = timestamp
                    normalized.append(payload)

        normalized.sort(
            key=lambda x: x.get('ingestion_time') or x.get('publish_date') or '',
            reverse=True
        )

        return normalized


# Singleton instance
_client_instance = None


def get_client() -> APIClient:
    """Get or create singleton APIClient instance"""
    global _client_instance
    
    if _client_instance is None:
        _client_instance = APIClient()
        
        # Show connection status in sidebar
        if not _client_instance.health_check():
            st.sidebar.warning(f"⚠️ Backend connection issue: {API_BASE_URL}")
        else:
            st.sidebar.success(f"✅ Connected to backend")
    
    return _client_instance


def reset_client():
    """Reset the client instance (useful for testing)"""
    global _client_instance
    _client_instance = None
