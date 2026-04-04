#!/usr/bin/env python3
"""
Speed Layer Consumer - Kafka -> MongoDB
100ms latency for real-time dashboard updates
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from kafka import KafkaConsumer
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError

sys.path.append('/app')
from config.settings import Settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - SPEED-CONSUMER - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MongoDBHandler:
    """Handles MongoDB operations for real-time storage"""
    
    def __init__(self):
        self.client = MongoClient(Settings.MONGODB_URI)
        self.db = self.client[Settings.MONGODB_DB]
        self.collection = self.db[Settings.MONGODB_COLLECTION]
        
        # Create TTL index (auto-delete after 48 hours)
        self.collection.create_index(
            'created_at',
            expireAfterSeconds=Settings.MONGODB_TTL_HOURS * 3600
        )
        
        # Create indexes for fast queries
        self.collection.create_index([('endpoint', ASCENDING)])
        self.collection.create_index([('timestamp', ASCENDING)])
        
        logger.info(f"MongoDB connected: {Settings.MONGODB_DB}.{Settings.MONGODB_COLLECTION}")
        logger.info(f"TTL enabled: {Settings.MONGODB_TTL_HOURS} hours")
    
    def insert_news(self, message: dict) -> bool:
        """Insert news document with metadata"""
        try:
            # Extract key fields
            data = message.get('data', {})
            endpoint = message.get('endpoint', 'unknown')
            
            # Build document
            document = {
                'endpoint': endpoint,
                'timestamp': message.get('timestamp'),
                'created_at': datetime.utcnow(),
                'source': message.get('source', 'unknown'),
                'layer': message.get('layer', 'speed'),
                'data': data,
                'metadata': self._extract_metadata(endpoint, data)
            }
            
            result = self.collection.insert_one(document)
            
            logger.info(f"✓ MongoDB insert [{endpoint}] - ID: {result.inserted_id}")
            return True
        
        except PyMongoError as e:
            logger.error(f"✗ MongoDB insert failed: {e}")
            return False
    
    def _extract_metadata(self, endpoint: str, data: dict) -> dict:
        """Extract searchable metadata from news data"""
        metadata = {'endpoint': endpoint}
        
        # Extract based on endpoint type
        if endpoint == 'search_news':
            if isinstance(data, dict) and 'news' in data:
                articles = data['news']
                if articles:
                    metadata['article_count'] = len(articles)
                    metadata['sample_title'] = articles[0].get('title', '')[:100]
        
        elif endpoint == 'top_news':
            if isinstance(data, dict):
                if 'top_news' in data:
                    clusters = data['top_news']
                    metadata['cluster_count'] = len(clusters)
                else:
                    metadata['cluster_id'] = data.get('cluster_id')
                    metadata['cluster_title'] = data.get('cluster_title', '')[:100]
                    metadata['article_count'] = data.get('article_count')
        
        elif endpoint == 'extract_news':
            metadata['title'] = data.get('title', '')[:100]
            metadata['author'] = data.get('author', '')
        
        elif endpoint == 'geo_coordinates':
            metadata['location'] = data.get('searched_location', '')
            metadata['latitude'] = data.get('latitude')
            metadata['longitude'] = data.get('longitude')
        
        elif endpoint == 'feed_rss':
            metadata['source_url'] = data.get('source_url', '')
            metadata['content_length'] = data.get('content_length', 0)
        
        return metadata
    
    def get_stats(self) -> dict:
        """Get collection statistics"""
        try:
            total = self.collection.count_documents({})
            
            # Count by endpoint
            pipeline = [
                {'$group': {'_id': '$endpoint', 'count': {'$sum': 1}}}
            ]
            by_endpoint = {doc['_id']: doc['count'] 
                          for doc in self.collection.aggregate(pipeline)}
            
            # Recent articles (last hour)
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            recent = self.collection.count_documents({
                'created_at': {'$gte': one_hour_ago}
            })
            
            return {
                'total_documents': total,
                'by_endpoint': by_endpoint,
                'recent_1h': recent
            }
        except Exception as e:
            logger.error(f"Stats error: {e}")
            return {}


class SpeedLayerConsumer:
    """Consumes from Kafka and writes to MongoDB"""
    
    def __init__(self):
        self.consumer = KafkaConsumer(
            Settings.KAFKA_TOPIC,
            **Settings.KAFKA_CONSUMER_CONFIG,
            max_partition_fetch_bytes=Settings.KAFKA_MAX_REQUEST_SIZE,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        self.mongo_handler = MongoDBHandler()
        self.stats = {
            'processed': 0,
            'errors': 0,
            'by_endpoint': {}
        }
        
        logger.info(f"Speed Layer Consumer ready - Topic: {Settings.KAFKA_TOPIC}")
    
    def process_message(self, message) -> bool:
        """Process single Kafka message"""
        if not message.value:
            return False
        
        try:
            data = message.value
            endpoint = data.get('endpoint', 'unknown')
            
            # Insert to MongoDB
            success = self.mongo_handler.insert_news(data)
            
            if success:
                self.stats['processed'] += 1
                self.stats['by_endpoint'][endpoint] = \
                    self.stats['by_endpoint'].get(endpoint, 0) + 1
                return True
            else:
                self.stats['errors'] += 1
                return False
        
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            self.stats['errors'] += 1
            return False
    
    def print_stats(self):
        """Print processing statistics"""
        mongo_stats = self.mongo_handler.get_stats()
        
        logger.info("\n" + "="*60)
        logger.info("SPEED LAYER STATISTICS")
        logger.info("="*60)
        logger.info(f"Processed: {self.stats['processed']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"MongoDB Total Docs: {mongo_stats.get('total_documents', 0)}")
        logger.info(f"Recent (1h): {mongo_stats.get('recent_1h', 0)}")
        logger.info("\nBy Endpoint:")
        for endpoint, count in self.stats['by_endpoint'].items():
            logger.info(f"  {endpoint}: {count}")
        logger.info("="*60 + "\n")
    
    def start(self):
        """Main consumption loop"""
        logger.info("="*60)
        logger.info("SPEED LAYER CONSUMER STARTED")
        logger.info("Kafka → MongoDB (Real-time)")
        logger.info("="*60)
        
        # Test MongoDB
        try:
            self.mongo_handler.get_stats()
            logger.info("✓ MongoDB connection verified")
        except Exception as e:
            logger.error(f"✗ MongoDB connection failed: {e}")
            return
        
        # Test Kafka
        try:
            topics = self.consumer.topics()
            logger.info(f"✓ Kafka connected - Available topics: {list(topics)}")
        except Exception as e:
            logger.error(f"✗ Kafka connection failed: {e}")
            return
        
        message_count = 0
        
        try:
            logger.info("Listening for messages...")
            
            for message in self.consumer:
                self.process_message(message)
                
                message_count += 1
                
                # Print stats every 10 messages
                if message_count % 10 == 0:
                    self.print_stats()
        
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            self.close()
    
    def close(self):
        """Cleanup"""
        logger.info("Shutting down consumer...")
        self.print_stats()
        self.consumer.close()
        self.mongo_handler.client.close()
        logger.info("Shutdown complete")


if __name__ == "__main__":
    consumer = SpeedLayerConsumer()
    consumer.start()