import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

class Settings:
    """Centralized configuration for the entire pipeline"""
    
    # ============ KAFKA CONFIGURATION ============
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')
    KAFKA_TOPIC = 'news-events'  # Single unified topic
    
    KAFKA_PRODUCER_CONFIG = {
        'bootstrap_servers': KAFKA_BOOTSTRAP_SERVERS.split(','),    #list of kafka servers
        'acks': 'all', 
        'retries': 3,
        'max_in_flight_requests_per_connection': 1,
        'compression_type': 'gzip',  
        'batch_size': 16384,
        'linger_ms': 10
    }

    # Keep producer/consumer and broker aligned on message size limits (bytes)
    KAFKA_MAX_REQUEST_SIZE = int(os.getenv('KAFKA_MAX_REQUEST_SIZE', '5242880'))
    
    KAFKA_CONSUMER_CONFIG = {
        'bootstrap_servers': KAFKA_BOOTSTRAP_SERVERS.split(','),
        'auto_offset_reset': 'earliest',
        'enable_auto_commit': True,
        'group_id': 'speed-layer-consumer',
        'max_poll_records': 500,
        'session_timeout_ms': 10000
    }
    
    # ============ NEWS API CONFIGURATION ============
    WORLD_NEWS_API_KEY = os.getenv('WORLD_NEWS_API_KEY')
    WORLD_NEWS_BASE_URL = 'https://api.worldnewsapi.com'
    
    # 7 API Endpoints
    NEWS_ENDPOINTS = {
        'search_news': f'{WORLD_NEWS_BASE_URL}/search-news',
        'top_news': f'{WORLD_NEWS_BASE_URL}/top-news',
        'extract_news': f'{WORLD_NEWS_BASE_URL}/extract-news',
        'search_news_sources': f'{WORLD_NEWS_BASE_URL}/search-news-sources',
        'geo_coordinates': f'{WORLD_NEWS_BASE_URL}/geo-coordinates',
        'feed_rss': f'{WORLD_NEWS_BASE_URL}/feed.rss',
        'extract_news_links': f'{WORLD_NEWS_BASE_URL}/search-news'  # Reuse search
    }
    
    # API Rate Limiting
    PRODUCER_FETCH_INTERVAL_SECONDS = int(os.getenv('FETCH_INTERVAL_SECONDS', '180'))  # 3 min
    API_REQUEST_DELAY_SECONDS = 2
    
    # India-focused queries
    SEARCH_QUERIES = [
        'India news today', 'Modi latest', 'Indian economy',
        'Mumbai Delhi news', 'India politics', 'Bollywood news',
        'Cricket India', 'India startups', 'Indian business'
    ]
    
    INDIAN_CITIES = [
        'Mumbai, India', 'Delhi, India', 'Bangalore, India',
        'Chennai, India', 'Kolkata, India', 'Hyderabad, India'
    ]
    
    NEWS_SOURCES = [
        'Times of India', 'Hindu', 'Indian Express', 
        'NDTV', 'News18', 'Economic Times'
    ]
    
    # ============ MONGODB CONFIGURATION (SPEED LAYER) ============
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://admin:password123@mongodb:27017/news_analytics?authSource=admin')
    MONGODB_DB = 'news_analytics'
    MONGODB_COLLECTION = 'realtime_news'
    MONGODB_TTL_HOURS = 48  # Auto-delete after 48 hours
    
    # ============ MINIO CONFIGURATION (BATCH LAYER) ============
    MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'minio:9000')
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'admin')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'password123')
    MINIO_SECURE = False
    
    # Lakehouse buckets
    MINIO_BRONZE_BUCKET = 'bronze-raw'
    MINIO_SILVER_BUCKET = 'silver-cleaned'
    MINIO_GOLD_BUCKET = 'gold-analytics'
    
    # ============ FLINK CONFIGURATION ============
    FLINK_WINDOW_SIZE_MINUTES = 5
    FLINK_CHECKPOINT_INTERVAL_MS = 60000  # 1 minute
    
    # ============ API SERVICE CONFIGURATION ============
    API_HOST = '0.0.0.0'
    API_PORT = 8000
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    
    # ============ LOGGING ============
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Validate required environment variables"""
        if not cls.WORLD_NEWS_API_KEY:
            raise ValueError("WORLD_NEWS_API_KEY not set in environment")
        
        if cls.WORLD_NEWS_API_KEY == 'dummy_key':
            raise ValueError("Invalid WORLD_NEWS_API_KEY - please set real API key")
        
        return True
    
    @classmethod
    def get_all_buckets(cls) -> List[str]:
        """Get all MinIO bucket names"""
        return [cls.MINIO_BRONZE_BUCKET, cls.MINIO_SILVER_BUCKET, cls.MINIO_GOLD_BUCKET]

if __name__ == "__main__":
    Settings.validate()
    print("Configuration validated successfully!")
    print(f"Kafka: {Settings.KAFKA_BOOTSTRAP_SERVERS}")
    print(f"MongoDB: {Settings.MONGODB_URI}")
    print(f"MinIO: {Settings.MINIO_ENDPOINT}")
