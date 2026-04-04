#!/usr/bin/env python3
"""
Pipeline Verification Script
Checks all components of the news pipeline are working correctly
"""

import sys
import json
import time
import requests
from kafka import KafkaConsumer, KafkaAdminClient
from pymongo import MongoClient
from minio import Minio

# Configuration
KAFKA_SERVERS = ['localhost:9092']
MONGODB_URI = 'mongodb://admin:password123@localhost:27017/news_analytics?authSource=admin'
MINIO_ENDPOINT = 'localhost:9000'
API_BASE_URL = 'http://localhost:8000'
DASHBOARD_URL = 'http://localhost:3000'


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.END} {msg}")


def print_error(msg):
    print(f"{Colors.RED}✗{Colors.END} {msg}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.END} {msg}")


def check_kafka():
    """Verify Kafka connection and topics"""
    print_section("1. KAFKA CHECK")
    
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_SERVERS)
        topics = admin_client.list_topics()
        
        if 'news-events' in topics:
            print_success(f"Kafka connected - Topic 'news-events' exists")
            
            # Check message count
            consumer = KafkaConsumer(
                'news-events',
                bootstrap_servers=KAFKA_SERVERS,
                auto_offset_reset='earliest',
                enable_auto_commit=False,
                consumer_timeout_ms=5000
            )
            
            msg_count = 0
            for _ in consumer:
                msg_count += 1
            
            print_success(f"Total messages in topic: {msg_count}")
            consumer.close()
            
            return True
        else:
            print_error("Topic 'news-events' not found")
            print(f"Available topics: {topics}")
            return False
    
    except Exception as e:
        print_error(f"Kafka connection failed: {e}")
        return False


def check_mongodb():
    """Verify MongoDB connection and data"""
    print_section("2. MONGODB CHECK (Speed Layer)")
    
    try:
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        db = client['news_analytics']
        collection = db['realtime_news']
        
        # Test connection
        client.admin.command('ping')
        print_success("MongoDB connected")
        
        # Check document count
        total_docs = collection.count_documents({})
        print_success(f"Total documents: {total_docs}")
        
        if total_docs > 0:
            # Check by endpoint
            pipeline = [
                {'$group': {'_id': '$endpoint', 'count': {'$sum': 1}}}
            ]
            by_endpoint = {doc['_id']: doc['count'] 
                          for doc in collection.aggregate(pipeline)}
            
            print_success("Documents by endpoint:")
            for endpoint, count in sorted(by_endpoint.items()):
                print(f"  - {endpoint}: {count}")
            
            # Show sample document
            sample = collection.find_one({}, {'_id': 0, 'timestamp': 1, 'endpoint': 1})
            print_success(f"Latest document: {sample}")
            
            return True
        else:
            print_warning("No documents in MongoDB yet")
            print("  Run: python3 tests/test_producer.py")
            return False
    
    except Exception as e:
        print_error(f"MongoDB connection failed: {e}")
        return False


def check_minio():
    """Verify MinIO and batch layer data"""
    print_section("3. MINIO CHECK (Batch Layer)")
    
    try:
        client = Minio(
            MINIO_ENDPOINT,
            access_key='admin',
            secret_key='password123',
            secure=False
        )
        
        buckets = ['bronze-raw', 'silver-cleaned', 'gold-analytics']
        all_exist = True
        
        for bucket in buckets:
            if client.bucket_exists(bucket):
                objects = list(client.list_objects(bucket, recursive=True))
                object_count = len(objects)
                
                if object_count > 0:
                    print_success(f"{bucket}: {object_count} objects")
                    
                    # Show sample objects
                    for obj in objects[:3]:
                        print(f"  - {obj.object_name} ({obj.size} bytes)")
                else:
                    print_warning(f"{bucket}: exists but empty")
                    if bucket == 'gold-analytics':
                        print("  Wait 5 minutes for batch window to flush")
            else:
                print_error(f"{bucket}: does not exist")
                all_exist = False
        
        return all_exist
    
    except Exception as e:
        print_error(f"MinIO connection failed: {e}")
        return False


def check_api():
    """Verify API endpoints"""
    print_section("4. API CHECK")
    
    endpoints_to_test = [
        ('Health', '/'),
        ('Realtime Stats', '/api/realtime/stats'),
        ('Analytics Summary', '/api/analytics/summary'),
        ('Latest News', '/api/realtime/latest?limit=5'),
    ]
    
    all_working = True
    
    for name, endpoint in endpoints_to_test:
        try:
            url = f"{API_BASE_URL}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"{name}: {url}")
                
                # Show key metrics
                if endpoint == '/api/realtime/stats':
                    print(f"  Total docs: {data.get('total_documents', 0)}")
                    print(f"  Last hour: {data.get('last_hour', 0)}")
                elif endpoint == '/api/analytics/summary':
                    speed = data.get('speed_layer', {})
                    batch = data.get('batch_layer', {})
                    print(f"  Speed layer: {speed.get('total_documents', 0)} docs")
                    print(f"  Batch layer: Bronze={batch.get('bronze_objects', 0)}, "
                          f"Silver={batch.get('silver_objects', 0)}, "
                          f"Gold={batch.get('gold_objects', 0)}")
            else:
                print_error(f"{name}: HTTP {response.status_code}")
                all_working = False
        
        except requests.exceptions.ConnectionError:
            print_error(f"{name}: Cannot connect to {API_BASE_URL}")
            all_working = False
        except Exception as e:
            print_error(f"{name}: {e}")
            all_working = False
    
    return all_working


def check_dashboard():
    """Verify dashboard is accessible"""
    print_section("5. DASHBOARD CHECK")
    
    try:
        response = requests.get(DASHBOARD_URL, timeout=5)
        
        if response.status_code == 200:
            print_success(f"Dashboard accessible at {DASHBOARD_URL}")
            return True
        else:
            print_error(f"Dashboard returned HTTP {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print_error(f"Dashboard not accessible at {DASHBOARD_URL}")
        print("  Check: docker-compose ps dashboard")
        return False
    except Exception as e:
        print_error(f"Dashboard check failed: {e}")
        return False


def check_kafka_ui():
    """Verify Kafka UI is accessible"""
    print_section("6. KAFKA UI CHECK")
    
    try:
        response = requests.get('http://localhost:8080', timeout=5)
        
        if response.status_code == 200:
            print_success("Kafka UI accessible at http://localhost:8080")
            return True
        else:
            print_error(f"Kafka UI returned HTTP {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print_error("Kafka UI not accessible at http://localhost:8080")
        print("  Check: docker-compose ps kafka-ui")
        print("  Try: docker-compose restart kafka-ui")
        return False
    except Exception as e:
        print_error(f"Kafka UI check failed: {e}")
        return False


def run_all_checks():
    """Run all verification checks"""
    print(f"\n{Colors.BOLD}NEWS PIPELINE VERIFICATION{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}")
    
    results = {
        'Kafka': check_kafka(),
        'MongoDB': check_mongodb(),
        'MinIO': check_minio(),
        'API': check_api(),
        'Dashboard': check_dashboard(),
        'Kafka UI': check_kafka_ui(),
    }
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    passed = sum(results.values())
    total = len(results)
    
    for component, status in results.items():
        if status:
            print_success(f"{component}: PASSED")
        else:
            print_error(f"{component}: FAILED")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} checks passed{Colors.END}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}All checks passed! Pipeline is healthy.{Colors.END}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}Some checks failed. Review errors above.{Colors.END}\n")
        print("Troubleshooting:")
        print("  1. Check services: docker-compose ps")
        print("  2. View logs: docker-compose logs <service-name>")
        print("  3. Restart services: docker-compose restart")
        print("  4. Send test data: python3 tests/test_producer.py")
        return 1


if __name__ == "__main__":
    exit_code = run_all_checks()
    sys.exit(exit_code)