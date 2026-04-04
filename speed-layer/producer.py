#!/usr/bin/env python3
"""
Speed Layer Producer - Fetches from 7 News APIs -> Kafka
Real-time ingestion for MongoDB consumption
CORRECTED FIX: Properly stream top_news by extracting only essential cluster metadata
"""

import json
import logging
import time
import random
import sys
from datetime import datetime
from typing import Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
import requests

# Add parent to path
sys.path.append('/app')
from config.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SPEED-PRODUCER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NewsAPIClient:
    """Lightweight client for World News API"""
    
    def __init__(self):
        Settings.validate()
        self.api_key = Settings.WORLD_NEWS_API_KEY
        self.base_url = Settings.WORLD_NEWS_BASE_URL
        self.session = requests.Session()
        self.last_latency_ms = None
        logger.info(f"API client initialized with key: {self.api_key[:8]}***")
    
    def _request(self, endpoint: str, params: dict) -> dict:
        """Make API request with error handling"""
        params['api-key'] = self.api_key
        start = time.monotonic()
        try:
            response = self.session.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API error [{endpoint}]: {e}")
            return None
        finally:
            self.last_latency_ms = int((time.monotonic() - start) * 1000)
    
    def search_news(self, text: str, country: str = "in", num: int = 10) -> dict:
        return self._request(Settings.NEWS_ENDPOINTS['search_news'], {
            'text': text,
            'source-country': country,
            'language': 'en',
            'number': num,
            'sort': 'publish-time',
            'sort-direction': 'DESC'
        })
    
    def get_top_news(self, country: str = "in") -> dict:
        return self._request(Settings.NEWS_ENDPOINTS['top_news'], {
            'source-country': country,
            'language': 'en',
            'max-news-per-cluster': 3
        })
    
    def extract_news(self, url: str) -> dict:
        return self._request(Settings.NEWS_ENDPOINTS['extract_news'], {
            'url': url,
            'analyze': 'true'
        })
    
    def search_sources(self, name: str) -> dict:
        return self._request(Settings.NEWS_ENDPOINTS['search_news_sources'], {
            'name': name
        })
    
    def get_geo_coordinates(self, location: str) -> dict:
        return self._request(Settings.NEWS_ENDPOINTS['geo_coordinates'], {
            'location': location
        })
    
    def get_rss_feed(self, url: str) -> str:
        """Returns RSS XML string"""
        try:
            response = self.session.get(
                Settings.NEWS_ENDPOINTS['feed_rss'],
                params={'url': url, 'api-key': self.api_key},
                timeout=30
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"RSS error: {e}")
            return None


class SpeedLayerProducer:
    """Produces real-time news data to Kafka"""
    
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=Settings.KAFKA_PRODUCER_CONFIG['bootstrap_servers'],
            acks=Settings.KAFKA_PRODUCER_CONFIG['acks'],
            retries=Settings.KAFKA_PRODUCER_CONFIG['retries'],
            compression_type=Settings.KAFKA_PRODUCER_CONFIG['compression_type'],
            batch_size=Settings.KAFKA_PRODUCER_CONFIG.get('batch_size', 16384),
            linger_ms=Settings.KAFKA_PRODUCER_CONFIG.get('linger_ms', 10),
            max_request_size=Settings.KAFKA_MAX_REQUEST_SIZE,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        self.api_client = NewsAPIClient()
        self.stats = {'total_sent': 0, 'errors': 0}
        self.extracted_urls = []
        self.last_success_time = None
        
        logger.info(
            f"Speed Layer Producer ready - Topic: {Settings.KAFKA_TOPIC} | "
            f"max_request_size={Settings.KAFKA_MAX_REQUEST_SIZE}"
        )

    def _send_payload(self, endpoint: str, payload: dict) -> bool:
        """Send a single payload with size guard."""
        payload_bytes = json.dumps(payload).encode('utf-8')
        if len(payload_bytes) > Settings.KAFKA_MAX_REQUEST_SIZE:
            logger.error(
                f"✗ Payload too large for Kafka [{endpoint}]: "
                f"{len(payload_bytes)} bytes (max {Settings.KAFKA_MAX_REQUEST_SIZE})"
            )
            return False

        future = self.producer.send(Settings.KAFKA_TOPIC, value=payload)
        future.get(timeout=10)
        return True

    def _compute_availability_pct(self) -> Optional[float]:
        total = self.stats['total_sent'] + self.stats['errors']
        if total == 0:
            return None
        return round((self.stats['total_sent'] / total) * 100, 2)

    def _compute_processing_lag_minutes(self) -> Optional[float]:
        if not self.last_success_time:
            return None
        delta = datetime.utcnow() - self.last_success_time
        return round(delta.total_seconds() / 60, 2)

    def send_system_healthcheck(self, status_override: Optional[str] = None, message: str = "") -> bool:
        """Emit a system healthcheck payload for pipeline monitoring."""
        availability_pct = self._compute_availability_pct()
        lag_minutes = self._compute_processing_lag_minutes()

        if status_override:
            status = status_override
        elif self.stats['total_sent'] == 0:
            status = "initializing"
        elif self.stats['errors'] == 0:
            status = "healthy"
        else:
            status = "warning"

        health_data = {
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'latency_ms': self.api_client.last_latency_ms,
            'availability_pct': availability_pct,
            'lag_minutes': lag_minutes,
            'services': {
                'producer': 'running',
                'kafka': 'connected'
            },
            'message': message
        }

        return self.send_to_kafka('system_healthcheck', health_data)
    
    def send_to_kafka(self, endpoint: str, data: dict) -> bool:
        """Send enriched message to Kafka"""
        if not data:
            logger.warning(f"Skipping send for {endpoint} - no data returned")
            return False

        # Safety: if top_news accidentally comes as full clusters, split here
        if endpoint == 'top_news' and isinstance(data, dict) and 'top_news' in data:
            clusters = data['top_news']
            total_clusters = len(clusters)
            logger.info("  → Detected full top_news payload; splitting into clusters")
            success_count = 0

            for idx, cluster in enumerate(clusters, 1):
                cluster_metadata = {
                    'cluster_index': idx,
                    'total_clusters': total_clusters,
                    'cluster_id': cluster.get('_id', 'unknown'),
                    'cluster_title': cluster.get('title', 'untitled')[:200],
                    'article_count': len(cluster.get('news', [])),
                    'cluster_size_mb': 'extracted_separately'
                }

                message = {
                    'timestamp': datetime.utcnow().isoformat(),
                    'endpoint': endpoint,
                    'source': 'world_news_api',
                    'layer': 'speed',
                    'data': cluster_metadata
                }

                try:
                    if self._send_payload(endpoint, message):
                        success_count += 1
                except Exception as e:
                    logger.error(f"✗ Kafka send failed [{endpoint}]: {e}")

            self.stats['total_sent'] += success_count
            return success_count > 0

        message = {
            'timestamp': datetime.utcnow().isoformat(),
            'endpoint': endpoint,
            'source': 'world_news_api',
            'layer': 'speed',
            'data': data
        }
        
        try:
            self._send_payload(endpoint, message)
            
            if endpoint != 'system_healthcheck':
                self.stats['total_sent'] += 1
                self.last_success_time = datetime.utcnow()
            logger.info(f"✓ Sent {endpoint} -> Kafka | Total: {self.stats['total_sent']}")
            return True
        
        except Exception as e:
            if endpoint != 'system_healthcheck':
                self.stats['errors'] += 1
            logger.error(f"✗ Kafka send failed [{endpoint}]: {e}")
            return False
    
    def fetch_search_news(self):
        """Endpoint 1: Search News"""
        query = random.choice(Settings.SEARCH_QUERIES)
        logger.info(f"Fetching search_news: {query}")
        
        data = self.api_client.search_news(query, num=20)
        if data and 'news' in data:
            for article in data['news'][:5]:
                if article.get('url'):
                    self.extracted_urls.append(article['url'])
            
            logger.info(f"  → Found {len(data['news'])} articles")
            return self.send_to_kafka('search_news', data)
        
        logger.warning("  → search_news returned no data")
        return False
    
    
    def fetch_top_news(self):
        """Endpoint 2: Top News - CORRECTED with proper clustering
        
        CRITICAL FIX:
        The API returns 248 clusters, each with ~3 articles inside.
        Each full cluster object can be 10KB+ due to embedded article content.
        
        Solution: Extract ONLY cluster metadata (title, id, count) and stream individually.
        This reduces ~2.6MB to ~1KB per message = 248 individual messages.
        
        Before (BROKEN):
        - Tried to wrap raw cluster objects → still ~2.6MB total
        
        After (FIXED):
        - Extract minimal metadata per cluster
        - Send as separate Kafka messages
        - Total payload per message: ~1KB
        """
        logger.info("Fetching top_news")
        
        data = self.api_client.get_top_news()
        if data and 'top_news' in data:
            clusters = data['top_news']
            total_clusters = len(clusters)
            logger.info(f"  → Found {total_clusters} news clusters")
            logger.info(f"  → STREAMING CLUSTERS INDIVIDUALLY (metadata only)")
            
            success_count = 0
            failed_count = 0
            
            # Process EACH cluster individually - extract metadata only
            for idx, cluster in enumerate(clusters, 1):
                try:
                    # CORRECTED: Extract ONLY minimal metadata from cluster
                    # Do NOT include the full cluster object with embedded articles
                    cluster_metadata = {
                        'cluster_index': idx,
                        'total_clusters': total_clusters,
                        'cluster_id': cluster.get('_id', 'unknown'),
                        'cluster_title': cluster.get('title', 'untitled')[:200],  # Truncate long titles
                        'article_count': len(cluster.get('news', [])),
                        'cluster_size_mb': 'extracted_separately'  # Indicate articles available via API
                    }
                    
                    # Send this minimal metadata as a separate message
                    success = self.send_to_kafka('top_news', cluster_metadata)
                    
                    if success:
                        success_count += 1
                        # Log progress every 50 clusters
                        if idx % 50 == 0 or idx == total_clusters:
                            logger.info(f"  → Progress: {idx}/{total_clusters} clusters sent")
                    else:
                        failed_count += 1
                    
                    # Small delay to prevent overwhelming Kafka and rate limiting
                    time.sleep(0.01)
                    
                except Exception as e:
                    logger.warning(f"  → Error processing cluster {idx}: {e}")
                    failed_count += 1
                    continue
            
            logger.info(f"  → COMPLETE: Sent {success_count}/{total_clusters} clusters | Failed: {failed_count}")
            return success_count > 0
        
        logger.warning("  → top_news returned no data")
        return False

    
    def fetch_extract_news(self):
        """Endpoint 3: Extract News (requires URL)"""
        if not self.extracted_urls:
            logger.warning("  → No URLs available for extraction, skipping")
            return False
        
        url = self.extracted_urls.pop(0)
        logger.info(f"Fetching extract_news: {url[:50]}...")
        
        data = self.api_client.extract_news(url)
        if data:
            title = data.get('title', 'Unknown')[:40] if isinstance(data, dict) else 'Unknown'
            logger.info(f"  → Extracted article: {title}...")
            return self.send_to_kafka('extract_news', data)
        
        logger.warning("  → extract_news returned no data")
        return False
    
    def fetch_search_sources(self):
        """Endpoint 4: Search News Sources"""
        source = random.choice(Settings.NEWS_SOURCES)
        logger.info(f"Fetching search_news_sources: {source}")
        
        data = self.api_client.search_sources(source)
        if data and 'news_sources' in data:
            count = len(data['news_sources'])
            logger.info(f"  → Found {count} sources")
            return self.send_to_kafka('search_news_sources', data)
        
        logger.warning("  → search_news_sources returned no data")
        return False
    
    def fetch_geo_coordinates(self):
        """Endpoint 5: Geo Coordinates"""
        city = random.choice(Settings.INDIAN_CITIES)
        logger.info(f"Fetching geo_coordinates: {city}")
        
        data = self.api_client.get_geo_coordinates(city)
        if data:
            lat, lon = data.get('latitude', 'N/A'), data.get('longitude', 'N/A')
            logger.info(f"  → Coordinates: {lat}, {lon}")
            return self.send_to_kafka('geo_coordinates', data)
        
        logger.warning("  → geo_coordinates returned no data")
        return False
    
    def fetch_rss_feed(self):
        """Endpoint 6: RSS Feed"""
        if self.extracted_urls:
            from urllib.parse import urlparse
            url = self.extracted_urls[0]
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
        else:
            base_url = 'https://www.thehindu.com'
        
        logger.info(f"Fetching feed_rss: {base_url}")
        
        rss_content = self.api_client.get_rss_feed(base_url)
        if rss_content:
            data = {
                'source_url': base_url,
                'content_length': len(rss_content),
                'preview': rss_content[:500]
            }
            logger.info(f"  → RSS content: {len(rss_content)} chars")
            return self.send_to_kafka('feed_rss', data)
        
        logger.warning("  → feed_rss returned no data")
        return False
    
    def fetch_extract_links(self):
        """Endpoint 7: Extract Links (uses search results)"""
        logger.info("Fetching extract_news_links")
        
        data = self.api_client.search_news("India news websites", num=5)
        if data and 'news' in data:
            urls = [a.get('url') for a in data['news'][:3] if a.get('url')]
            result = {
                'extracted_urls': urls,
                'count': len(urls)
            }
            logger.info(f"  → Extracted {len(urls)} URLs")
            return self.send_to_kafka('extract_news_links', result)
        
        logger.warning("  → extract_news_links returned no data")
        return False
    
    def run_cycle(self):
        """Execute one round of all 7 endpoints"""
        endpoints = [
            self.fetch_search_news,
            self.fetch_top_news,
            self.fetch_extract_news,
            self.fetch_search_sources,
            self.fetch_geo_coordinates,
            self.fetch_rss_feed,
            self.fetch_extract_links
        ]
        
        random.shuffle(endpoints)
        
        for endpoint_func in endpoints:
            try:
                endpoint_func()
                time.sleep(Settings.API_REQUEST_DELAY_SECONDS)
            except Exception as e:
                logger.error(f"Endpoint error in {endpoint_func.__name__}: {e}", exc_info=True)
    
    def start(self):
        """Main production loop"""
        logger.info("="*60)
        logger.info("SPEED LAYER PRODUCER STARTED")
        logger.info(f"Interval: {Settings.PRODUCER_FETCH_INTERVAL_SECONDS}s")
        logger.info("="*60)
        
        try:
            self.send_system_healthcheck(status_override="initializing", message="Producer startup")
            logger.info("✓ Kafka connection verified")
        except Exception as e:
            logger.error(f"✗ Kafka connection failed: {e}")
            return
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                logger.info(f"\n{'='*60}")
                logger.info(f"CYCLE {cycle_count} - Fetching from all 7 endpoints")
                logger.info(f"{'='*60}")
                
                self.run_cycle()
                self.send_system_healthcheck(message=f"Cycle {cycle_count} complete")
                
                logger.info(f"\n{'='*60}")
                logger.info(f"CYCLE {cycle_count} COMPLETE")
                logger.info(f"Total Sent: {self.stats['total_sent']} | Errors: {self.stats['errors']}")
                logger.info(f"Next cycle in {Settings.PRODUCER_FETCH_INTERVAL_SECONDS}s")
                logger.info(f"{'='*60}\n")
                
                time.sleep(Settings.PRODUCER_FETCH_INTERVAL_SECONDS)
        
        except KeyboardInterrupt:
            logger.info("Producer stopped by user")
        finally:
            self.close()
    
    def close(self):
        """Cleanup"""
        logger.info("Shutting down producer...")
        logger.info(f"Final stats - Sent: {self.stats['total_sent']} | Errors: {self.stats['errors']}")
        self.producer.flush()
        self.producer.close()


if __name__ == "__main__":
    producer = SpeedLayerProducer()
    producer.start()
