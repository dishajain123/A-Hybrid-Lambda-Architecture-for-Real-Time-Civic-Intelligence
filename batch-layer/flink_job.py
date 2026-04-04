#!/usr/bin/env python3
"""
Flink Job - Bronze → Silver → Gold ETL Pipeline
Fixed validation issues for all endpoint types
"""

import json
import logging
import sys
import threading
import time
import uuid
from datetime import datetime
from io import BytesIO
from collections import Counter, defaultdict
from urllib.parse import urlparse
from kafka import KafkaConsumer
from minio import Minio
from minio.error import S3Error

sys.path.append('/app')
from config.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - FLINK - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MinIOLakehouse:
    """MinIO data lake handler"""
    
    def __init__(self):
        self.client = Minio(
            Settings.MINIO_ENDPOINT,
            access_key=Settings.MINIO_ACCESS_KEY,
            secret_key=Settings.MINIO_SECRET_KEY,
            secure=Settings.MINIO_SECURE
        )
        self._ensure_buckets()
        logger.info("MinIO lakehouse initialized")
    
    def _ensure_buckets(self):
        """Create buckets if missing"""
        for bucket in Settings.get_all_buckets():
            try:
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                    logger.info(f"Created bucket: {bucket}")
            except S3Error as e:
                logger.error(f"Bucket error: {e}")
    
    def write_json(self, bucket: str, path: str, data: dict) -> bool:
        """Write JSON to MinIO"""
        try:
            json_bytes = json.dumps(data, indent=2).encode('utf-8')
            self.client.put_object(
                bucket, path, BytesIO(json_bytes), len(json_bytes),
                content_type='application/json'
            )
            return True
        except Exception as e:
            logger.error(f"Write error: {e}")
            return False


class DataProcessor:
    """Process data through Bronze → Silver → Gold layers"""
    
    DOMAIN_MAPPING = {
        'news18.com': 'News18',
        'timesnownews.com': 'Times Now',
        'latestly.com': 'Latestly',
        'republicworld.com': 'Republic World',
        'thehindu.com': 'The Hindu',
        'ndtv.com': 'NDTV',
        'indiatoday.in': 'India Today',
        'economictimes.indiatimes.com': 'Economic Times',
        'timesofindia.indiatimes.com': 'Times of India',
        'socialnews.xyz': 'Social News XYZ',
        'kalingatv.com': 'Kalinga TV',
        'telanganatoday.com': 'Telangana Today',
        'ibtimes.co.in': 'IBTimes India',
        'tribuneindia.com': 'Tribune India',
        'scroll.in': 'Scroll.in',
        'zeenews.india.com': 'Zee News',
        'news.abplive.com': 'ABP Live',
        'hindustantimes.com': 'Hindustan Times',
        'indianexpress.com': 'Indian Express',
        'business-standard.com': 'Business Standard',
        'livemint.com': 'Mint',
        'firstpost.com': 'Firstpost',
        'thequint.com': 'The Quint',
        'deccanherald.com': 'Deccan Herald'
    }
    
    def process_bronze(self, raw_message: dict) -> dict:
        """Bronze: Store raw data with metadata"""
        return {
            'layer': 'bronze',
            'ingestion_time': datetime.utcnow().isoformat(),
            'endpoint': raw_message.get('endpoint', 'unknown'),
            'source_api': raw_message.get('source', 'world_news_api'),
            'raw_message': raw_message
        }
    
    def process_silver(self, bronze_data: dict) -> dict:
        """Silver: Extract, clean, normalize data by endpoint type"""
        raw_msg = bronze_data.get('raw_message', {})
        endpoint = raw_msg.get('endpoint', 'unknown')
        data = raw_msg.get('data', {})
        
        # Route to appropriate extractor
        if endpoint == 'search_news':
            cleaned = self._extract_search_news(data)
        elif endpoint == 'top_news':
            cleaned = self._extract_top_news(data)
        elif endpoint == 'extract_news':
            cleaned = self._extract_extract_news(data)
        elif endpoint == 'extract_news_links':
            cleaned = self._extract_extract_news_links(data)
        elif endpoint == 'feed_rss':
            cleaned = self._extract_feed_rss(data)
        elif endpoint == 'geo_coordinates':
            cleaned = self._extract_geo_coordinates(data)
        elif endpoint == 'system_healthcheck':
            cleaned = self._extract_healthcheck(data)
        else:
            cleaned = {'type': 'unknown', 'raw_data': data}
        
        return {
            'layer': 'silver',
            'processed_time': datetime.utcnow().isoformat(),
            'endpoint': endpoint,
            'source_timestamp': raw_msg.get('timestamp'),
            'cleaned_data': cleaned
        }
    
    def _extract_search_news(self, data: dict) -> dict:
        """Extract articles from search_news endpoint"""
        articles = []
        for article in data.get('news', []):
            cleaned = self._normalize_article(article)
            if cleaned['id'] and cleaned['title']:
                articles.append(cleaned)
        
        return {
            'type': 'articles',
            'articles': self._deduplicate(articles),
            'total_articles': len(articles),
            'metadata': {
                'offset': data.get('offset', 0),
                'available': data.get('available', 0),
                'returned': data.get('number', len(articles))
            }
        }
    
    def _extract_top_news(self, data: dict) -> dict:
        """Extract articles from top_news clusters"""
        articles = []
        clusters = []
        
        for cluster in data.get('top_news', []):
            cluster_info = {
                'cluster_id': cluster.get('cluster_id'),
                'article_count': len(cluster.get('news', []))
            }
            clusters.append(cluster_info)
            
            for article in cluster.get('news', []):
                cleaned = self._normalize_article(article)
                cleaned['cluster_id'] = cluster.get('cluster_id')
                if cleaned['id'] and cleaned['title']:
                    articles.append(cleaned)
        
        return {
            'type': 'articles',
            'articles': self._deduplicate(articles),
            'total_articles': len(articles),
            'clusters': clusters,
            'total_clusters': len(clusters)
        }
    
    def _extract_extract_news(self, data: dict) -> dict:
        """Extract single article from extract_news endpoint"""
        if not data or not isinstance(data, dict):
            return {'type': 'single_article', 'article': None, 'total_articles': 0}
        
        article = self._normalize_article(data)
        
        return {
            'type': 'single_article',
            'article': article if article['id'] and article['title'] else None,
            'total_articles': 1 if article['id'] else 0,
            'extraction_metadata': {
                'entities_count': len(data.get('entities', [])),
                'has_video': bool(data.get('video')),
                'images_count': len(data.get('images', []))
            }
        }
    
    def _extract_extract_news_links(self, data: dict) -> dict:
        """Extract URLs from extract_news_links endpoint"""
        urls = data.get('extracted_urls', [])
        domains = []
        for url in urls:
            try:
                domain = urlparse(url).netloc.replace('www.', '')
                domains.append(domain)
            except:
                pass
        
        return {
            'type': 'urls',
            'urls': urls,
            'total_urls': data.get('count', len(urls)),
            'domains': list(set(domains)),
            'unique_domains': len(set(domains))
        }
    
    def _extract_feed_rss(self, data: dict) -> dict:
        """Extract RSS feed metadata"""
        return {
            'type': 'rss_feed',
            'source_url': data.get('source_url', ''),
            'content_length': data.get('content_length', 0),
            'preview': data.get('preview', '')[:200],
            'domain': urlparse(data.get('source_url', '')).netloc.replace('www.', '')
        }
    
    def _extract_geo_coordinates(self, data: dict) -> dict:
        """Extract geographic coordinates"""
        return {
            'type': 'geolocation',
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'city': data.get('city', 'Unknown'),
            'coordinates': f"{data.get('latitude', 0)},{data.get('longitude', 0)}"
        }
    
    def _extract_healthcheck(self, data: dict) -> dict:
        """Extract system healthcheck data"""
        latency_ms = data.get('latency_ms')
        availability_pct = data.get('availability_pct')
        lag_minutes = data.get('lag_minutes')

        if latency_ms is None:
            latency_ms = data.get('ingestion_latency_ms')
        if availability_pct is None:
            availability_pct = data.get('source_availability_pct')
        if lag_minutes is None:
            lag_minutes = data.get('processing_lag_minutes')

        return {
            'type': 'healthcheck',
            'status': data.get('status', 'unknown'),
            'timestamp': data.get('timestamp'),
            'services': data.get('services', {}),
            'message': data.get('message', ''),
            'latency_ms': latency_ms,
            'availability_pct': availability_pct,
            'lag_minutes': lag_minutes
        }
    
    def _normalize_article(self, article: dict) -> dict:
        """Normalize article structure across all endpoints"""
        return {
            'id': article.get('id'),
            'title': self._clean_text(article.get('title', '')),
            'summary': self._clean_text(article.get('text', '') or article.get('summary', ''))[:500],
            'url': article.get('url', ''),
            'image': article.get('image'),
            'video': article.get('video'),
            'author': self._get_author(article),
            'publish_date': article.get('publish_date'),
            'category': article.get('category') or 'general',
            'sentiment': article.get('sentiment', 0.0),
            'source': self._get_source(article),
            'source_country': article.get('source', {}).get('country') or article.get('source_country') or 'unknown',
            'language': article.get('language', 'en'),
            'cluster_id': article.get('cluster_id')
        }
    
    def _get_author(self, article: dict) -> str:
        """Extract author with fallbacks"""
        if article.get('author') and article['author'] != 'Unknown':
            return article['author']
        
        authors = article.get('authors', [])
        if authors and len(authors) > 0:
            return ', '.join(authors[:3])
        
        return 'Unknown'
    
    def _get_source(self, article: dict) -> str:
        """Extract source with comprehensive fallback"""
        source_title = article.get('source', {}).get('title')
        if source_title and source_title not in ['Unknown', '', None]:
            return source_title
        
        url = article.get('url', '')
        if url:
            source_from_url = self._extract_source_from_url(url)
            if source_from_url and source_from_url != 'Unknown':
                return source_from_url
        
        author = article.get('author', '')
        if author and author != 'Unknown':
            author_lower = author.lower()
            for source_name in self.DOMAIN_MAPPING.values():
                if source_name.lower() in author_lower:
                    return source_name
        
        return 'Unknown'
    
    def _extract_source_from_url(self, url: str) -> str:
        """Extract source name from URL domain"""
        if not url:
            return None
        
        try:
            domain = urlparse(url).netloc.lower().replace('www.', '')
            
            if domain in self.DOMAIN_MAPPING:
                return self.DOMAIN_MAPPING[domain]
            
            parts = domain.split('.')
            if len(parts) >= 2:
                parent_domain = '.'.join(parts[-2:])
                if parent_domain in self.DOMAIN_MAPPING:
                    return self.DOMAIN_MAPPING[parent_domain]
            
            main_part = parts[0] if len(parts) > 0 else domain
            readable_name = main_part.replace('-', ' ').replace('_', ' ').title()
            return readable_name if readable_name else 'Unknown'
            
        except Exception as e:
            logger.error(f"Error extracting source from URL {url}: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text content"""
        if not text:
            return ''
        return ' '.join(text.replace('\x00', '').split()).strip()
    
    def _deduplicate(self, articles: list) -> list:
        """Remove duplicate articles by ID"""
        seen = set()
        unique = []
        for article in articles:
            aid = article.get('id')
            if aid and aid not in seen:
                seen.add(aid)
                unique.append(article)
        return unique
    
    def process_gold(self, silver_data: dict) -> dict:
        """Gold: Dashboard-ready analytics + full content"""
        endpoint = silver_data.get('endpoint')
        cleaned = silver_data.get('cleaned_data', {})
        data_type = cleaned.get('type', 'unknown')
        
        # Route to appropriate Gold processor based on data type
        if data_type == 'articles':
            return self._process_gold_articles(endpoint, cleaned, silver_data)
        elif data_type == 'single_article':
            return self._process_gold_single_article(endpoint, cleaned, silver_data)
        elif data_type == 'urls':
            return self._process_gold_urls(endpoint, cleaned, silver_data)
        elif data_type == 'rss_feed':
            return self._process_gold_rss(endpoint, cleaned, silver_data)
        elif data_type == 'geolocation':
            return self._process_gold_geo(endpoint, cleaned, silver_data)
        elif data_type == 'healthcheck':
            return self._process_gold_healthcheck(endpoint, cleaned, silver_data)
        else:
            return self._process_gold_generic(endpoint, cleaned, silver_data)
    
    def _process_gold_articles(self, endpoint: str, cleaned: dict, silver_data: dict) -> dict:
        """Process article-based endpoints (search_news, top_news)"""
        articles = cleaned.get('articles', [])
        
        if not articles:
            return self._empty_gold_response(endpoint, 'articles')
        
        sorted_articles = sorted(
            articles,
            key=lambda x: (x.get('publish_date', ''), abs(x.get('sentiment', 0))),
            reverse=True
        )
        
        latest = sorted_articles[:20]
        top_positive = sorted([a for a in articles if a.get('sentiment', 0) > 0.3],
                            key=lambda x: x['sentiment'], reverse=True)[:10]
        top_negative = sorted([a for a in articles if a.get('sentiment', 0) < -0.3],
                            key=lambda x: x['sentiment'])[:10]
        
        return {
            'layer': 'gold',
            'analytics_time': datetime.utcnow().isoformat(),
            'endpoint': endpoint,
            'data_type': 'articles',
            'metrics': {
                'endpoint': endpoint,
                'total_articles': len(articles),
                'sentiment_distribution': self._sentiment_dist(articles),
                'avg_sentiment': self._avg_sentiment(articles),
                'category_breakdown': self._count_field(articles, 'category'),
                'top_authors': self._top_items(articles, 'author', 10),
                'source_countries': self._count_field(articles, 'source_country'),
                'top_sources': self._top_items(articles, 'source', 10),
                'languages': self._count_field(articles, 'language'),
                'time_series': self._time_series(articles),
                'trending_keywords': self._trending_keywords(articles, 15),
                'articles_with_sentiment': sum(1 for a in articles if a.get('sentiment', 0) != 0),
                'articles_with_images': sum(1 for a in articles if a.get('image')),
                'articles_with_video': sum(1 for a in articles if a.get('video'))
            },
            'articles': sorted_articles,
            'article_count': len(sorted_articles),
            'featured': {
                'latest': latest,
                'most_positive': top_positive,
                'most_negative': top_negative,
                'trending': sorted_articles[:15]
            },
            'data_quality': {
                'articles_with_urls': sum(1 for a in articles if a.get('url')),
                'articles_with_authors': sum(1 for a in articles if a.get('author') != 'Unknown'),
                'articles_with_images': sum(1 for a in articles if a.get('image')),
                'articles_with_known_sources': sum(1 for a in articles if a.get('source') != 'Unknown'),
                'unique_sources': len(set(a['source'] for a in articles)),
                'completeness_score': self._calculate_completeness(articles),
                'date_range': {
                    'earliest': min((a.get('publish_date') for a in articles if a.get('publish_date')), default=None),
                    'latest': max((a.get('publish_date') for a in articles if a.get('publish_date')), default=None)
                }
            },
            'endpoint_metadata': cleaned.get('metadata', {})
        }
    
    def _process_gold_single_article(self, endpoint: str, cleaned: dict, silver_data: dict) -> dict:
        """Process extract_news endpoint (single article)"""
        article = cleaned.get('article')
        
        if not article:
            return self._empty_gold_response(endpoint, 'single_article')
        
        return {
            'layer': 'gold',
            'analytics_time': datetime.utcnow().isoformat(),
            'endpoint': endpoint,
            'data_type': 'single_article',
            'metrics': {
                'endpoint': endpoint,
                'total_articles': 1,
                'sentiment_distribution': self._sentiment_dist([article]),
                'category_breakdown': {article.get('category', 'general'): 1},
                'top_sources': [{'name': article.get('source', 'Unknown'), 'count': 1}]
            },
            'article': article,
            'data_quality': {
                'has_url': bool(article.get('url')),
                'has_author': article.get('author') != 'Unknown',
                'has_image': bool(article.get('image')),
                'has_video': bool(article.get('video')),
                'has_source': article.get('source') != 'Unknown',
                'completeness_score': self._calculate_completeness([article])
            },
            'extraction_metadata': cleaned.get('extraction_metadata', {})
        }
    
    def _process_gold_urls(self, endpoint: str, cleaned: dict, silver_data: dict) -> dict:
        """Process extract_news_links endpoint"""
        return {
            'layer': 'gold',
            'analytics_time': datetime.utcnow().isoformat(),
            'endpoint': endpoint,
            'data_type': 'urls',
            'metrics': {
                'endpoint': endpoint,
                'total_articles': cleaned.get('total_urls', 0),
                'sentiment_distribution': {'positive': 0, 'neutral': cleaned.get('total_urls', 0), 'negative': 0},
                'category_breakdown': {'url_extraction': cleaned.get('total_urls', 0)},
                'top_sources': [{'name': d, 'count': 1} for d in cleaned.get('domains', [])[:10]]
            },
            'urls': cleaned.get('urls', []),
            'domains': cleaned.get('domains', []),
            'data_quality': {
                'total_urls': cleaned.get('total_urls', 0),
                'unique_domains': cleaned.get('unique_domains', 0),
                'valid_urls': len([u for u in cleaned.get('urls', []) if u.startswith('http')])
            }
        }
    
    def _process_gold_rss(self, endpoint: str, cleaned: dict, silver_data: dict) -> dict:
        """Process feed_rss endpoint"""
        return {
            'layer': 'gold',
            'analytics_time': datetime.utcnow().isoformat(),
            'endpoint': endpoint,
            'data_type': 'rss_feed',
            'metrics': {
                'endpoint': endpoint,
                'total_articles': 1,
                'sentiment_distribution': {'positive': 0, 'neutral': 1, 'negative': 0},
                'category_breakdown': {'rss_feed': 1},
                'top_sources': [{'name': cleaned.get('domain', 'Unknown'), 'count': 1}]
            },
            'rss_data': {
                'source_url': cleaned.get('source_url', ''),
                'domain': cleaned.get('domain', ''),
                'content_length': cleaned.get('content_length', 0),
                'preview': cleaned.get('preview', '')
            },
            'data_quality': {
                'has_content': cleaned.get('content_length', 0) > 0,
                'content_size_kb': round(cleaned.get('content_length', 0) / 1024, 2)
            }
        }
    
    def _process_gold_geo(self, endpoint: str, cleaned: dict, silver_data: dict) -> dict:
        """Process geo_coordinates endpoint"""
        return {
            'layer': 'gold',
            'analytics_time': datetime.utcnow().isoformat(),
            'endpoint': endpoint,
            'data_type': 'geolocation',
            'metrics': {
                'endpoint': endpoint,
                'total_articles': 1,
                'sentiment_distribution': {'positive': 0, 'neutral': 1, 'negative': 0},
                'category_breakdown': {'geolocation': 1},
                'top_sources': [{'name': 'Geo API', 'count': 1}]
            },
            'location_data': {
                'city': cleaned.get('city', 'Unknown'),
                'latitude': cleaned.get('latitude'),
                'longitude': cleaned.get('longitude'),
                'coordinates': cleaned.get('coordinates', '')
            },
            'data_quality': {
                'has_coordinates': bool(cleaned.get('latitude') and cleaned.get('longitude')),
                'has_city': bool(cleaned.get('city') and cleaned.get('city') != 'Unknown')
            }
        }
    
    def _process_gold_healthcheck(self, endpoint: str, cleaned: dict, silver_data: dict) -> dict:
        """Process system_healthcheck endpoint"""
        timestamp = cleaned.get('timestamp') or silver_data.get('source_timestamp') or datetime.utcnow().isoformat()
        return {
            'layer': 'gold',
            'analytics_time': datetime.utcnow().isoformat(),
            'endpoint': endpoint,
            'data_type': 'healthcheck',
            'metrics': {
                'endpoint': endpoint,
                'total_articles': 1,
                'sentiment_distribution': {'positive': 0, 'neutral': 1, 'negative': 0},
                'category_breakdown': {'system_health': 1},
                'top_sources': [{'name': 'System Monitor', 'count': 1}]
            },
            'health_data': {
                'status': cleaned.get('status', 'unknown'),
                'timestamp': timestamp,
                'services': cleaned.get('services', {}),
                'message': cleaned.get('message', ''),
                'latency_ms': cleaned.get('latency_ms'),
                'availability_pct': cleaned.get('availability_pct'),
                'lag_minutes': cleaned.get('lag_minutes')
            },
            'data_quality': {
                'has_status': bool(cleaned.get('status')),
                'has_timestamp': bool(cleaned.get('timestamp')),
                'services_count': len(cleaned.get('services', {}))
            }
        }
    
    def _process_gold_generic(self, endpoint: str, cleaned: dict, silver_data: dict) -> dict:
        """Generic processor for unknown endpoints"""
        return {
            'layer': 'gold',
            'analytics_time': datetime.utcnow().isoformat(),
            'endpoint': endpoint,
            'data_type': 'generic',
            'metrics': {
                'endpoint': endpoint,
                'total_articles': 0,
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'category_breakdown': {},
                'top_sources': []
            },
            'raw_data': cleaned,
            'data_quality': {'processed': True}
        }
    
    def _empty_gold_response(self, endpoint: str, data_type: str) -> dict:
        """Return empty but valid Gold structure"""
        return {
            'layer': 'gold',
            'analytics_time': datetime.utcnow().isoformat(),
            'endpoint': endpoint,
            'data_type': data_type,
            'metrics': {
                'endpoint': endpoint,
                'total_articles': 0,
                'sentiment_distribution': {'positive': 0, 'neutral': 0, 'negative': 0},
                'category_breakdown': {},
                'top_sources': []
            },
            'data_quality': {'no_data': True}
        }
    
    # Analytics helper methods
    def _sentiment_dist(self, articles: list) -> dict:
        dist = {'positive': 0, 'neutral': 0, 'negative': 0}
        for a in articles:
            s = a.get('sentiment', 0)
            if s > 0.1:
                dist['positive'] += 1
            elif s < -0.1:
                dist['negative'] += 1
            else:
                dist['neutral'] += 1
        return dist
    
    def _avg_sentiment(self, articles: list) -> float:
        sentiments = [a.get('sentiment', 0) for a in articles]
        return round(sum(sentiments) / len(sentiments), 3) if sentiments else 0.0
    
    def _count_field(self, articles: list, field: str) -> dict:
        return dict(Counter(a.get(field, 'unknown') for a in articles).most_common())
    
    def _top_items(self, articles: list, field: str, n: int) -> list:
        counter = Counter(a.get(field, 'unknown') for a in articles)
        return [{'name': k, 'count': v} for k, v in counter.most_common(n)]
    
    def _time_series(self, articles: list) -> dict:
        counts = defaultdict(int)
        for a in articles:
            date = a.get('publish_date')
            if date:
                try:
                    dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    counts[dt.strftime('%Y-%m-%dT%H:00')] += 1
                except:
                    pass
        return dict(sorted(counts.items()))
    
    def _trending_keywords(self, articles: list, n: int = 15) -> list:
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'up', 'about', 'into', 'is', 'it', 'as'}
        counts = Counter()
        for a in articles:
            words = [w.strip('.,!?;:()[]{}') for w in a.get('title', '').lower().split()]
            words = [w for w in words if w and len(w) > 3 and w not in stop_words]
            counts.update(words)
        return [{'keyword': k, 'count': v} for k, v in counts.most_common(n)]
    
    def _calculate_completeness(self, articles: list) -> float:
        """Calculate data completeness score (0-100)"""
        if not articles:
            return 0.0
        
        total_score = 0
        for article in articles:
            score = 0
            if article.get('title'): score += 1
            if article.get('summary'): score += 1
            if article.get('url'): score += 1
            if article.get('author') != 'Unknown': score += 1
            if article.get('source') != 'Unknown': score += 1
            if article.get('publish_date'): score += 1
            if article.get('image'): score += 1
            total_score += (score / 7) * 100
        
        return round(total_score / len(articles), 2)


class FlinkJob:
    """Main Flink job with windowing"""
    
    def __init__(self):
        self.consumer = KafkaConsumer(
            Settings.KAFKA_TOPIC,
            bootstrap_servers=Settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
            group_id='flink-job-consumer',
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        self.lakehouse = MinIOLakehouse()
        self.processor = DataProcessor()
        self.window_buffer = []
        self.window_lock = threading.Lock()
        self.running = True
        
        self.stats = {
            'bronze': 0, 'silver': 0, 'gold': 0,
            'articles': 0, 'errors': 0,
            'endpoints': defaultdict(int)
        }
        
        threading.Thread(target=self._auto_flush, daemon=True).start()
        logger.info(f"Flink job started - {Settings.FLINK_WINDOW_SIZE_MINUTES}min windows")
    
    def _auto_flush(self):
        """Auto-flush window every N minutes"""
        while self.running:
            time.sleep(Settings.FLINK_WINDOW_SIZE_MINUTES * 60)
            with self.window_lock:
                if self.window_buffer:
                    logger.info(f"Auto-flush: {len(self.window_buffer)} messages")
                    self._process_window()
    
    def _process_window(self):
        """Process buffered messages through all layers"""
        for msg in self.window_buffer:
            self._process_layers(msg)
        self.window_buffer = []
    
    def _process_layers(self, message: dict):
        """Process through Bronze → Silver → Gold"""
        timestamp = datetime.utcnow()
        endpoint = message.get('endpoint', 'unknown')
        date_path = timestamp.strftime('%Y/%m/%d')
        uid = str(uuid.uuid4())[:8]
        prefix = f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{uid}"
        
        try:
            # Bronze layer
            bronze = self.processor.process_bronze(message)
            bronze_path = f"{endpoint}/{date_path}/{prefix}_bronze.json"
            
            if self.lakehouse.write_json(Settings.MINIO_BRONZE_BUCKET, bronze_path, bronze):
                self.stats['bronze'] += 1
                self.stats['endpoints'][endpoint] += 1
                
                # Silver layer
                silver = self.processor.process_silver(bronze)
                silver_path = f"{endpoint}/{date_path}/{prefix}_silver.json"
                
                cleaned_data = silver.get('cleaned_data', {})
                article_count = cleaned_data.get('total_articles', 0)
                
                if self.lakehouse.write_json(Settings.MINIO_SILVER_BUCKET, silver_path, silver):
                    self.stats['silver'] += 1
                    self.stats['articles'] += article_count
                    
                    # Gold layer
                    gold = self.processor.process_gold(silver)
                    gold_path = f"{endpoint}/{date_path}/{prefix}_gold.json"
                    
                    if self.lakehouse.write_json(Settings.MINIO_GOLD_BUCKET, gold_path, gold):
                        self.stats['gold'] += 1
                        logger.info(f"✓ [{endpoint}] {article_count} items → All layers ({uid})")
        
        except Exception as e:
            logger.error(f"✗ Processing error [{endpoint}]: {e}", exc_info=True)
            self.stats['errors'] += 1
    
    def start(self):
        """Main loop"""
        logger.info("="*70)
        logger.info("FLINK JOB RUNNING - Listening for Kafka messages...")
        logger.info("="*70)
        
        try:
            for message in self.consumer:
                if message.value:
                    endpoint = message.value.get('endpoint', 'unknown')
                    with self.window_lock:
                        self.window_buffer.append(message.value)
                        logger.info(f"Buffered [{endpoint}] - Window size: {len(self.window_buffer)}")
        
        except KeyboardInterrupt:
            logger.info("\nFlink job stopped by user")
        finally:
            self.close()
    
    def close(self):
        """Cleanup and final stats"""
        self.running = False
        with self.window_lock:
            if self.window_buffer:
                logger.info(f"Final flush: {len(self.window_buffer)} messages")
                self._process_window()
        
        logger.info("\n" + "="*70)
        logger.info("FLINK JOB STATISTICS")
        logger.info("="*70)
        logger.info(f"Bronze records: {self.stats['bronze']}")
        logger.info(f"Silver records: {self.stats['silver']}")
        logger.info(f"Gold records:   {self.stats['gold']}")
        logger.info(f"Total items:    {self.stats['articles']}")
        logger.info(f"Errors:         {self.stats['errors']}")
        logger.info("\nEndpoint breakdown:")
        for endpoint, count in sorted(self.stats['endpoints'].items()):
            logger.info(f"  {endpoint}: {count}")
        logger.info("="*70)
        
        self.consumer.close()


if __name__ == "__main__":
    FlinkJob().start()
