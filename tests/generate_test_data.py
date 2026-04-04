#!/usr/bin/env python3
"""
Test Data Generator - Creates fake news data for testing pipeline
Run this BEFORE starting producer to test with controlled data
"""

import json
import sys
import time
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Test with local Kafka
KAFKA_SERVERS = ['localhost:9092']
TOPIC = 'news-events'

def create_test_messages():
    """Generate 20 test messages across all 7 endpoints"""
    
    messages = []
    
    # 1. Search News (5 messages)
    for i in range(5):
        messages.append({
            'timestamp': datetime.utcnow().isoformat(),
            'endpoint': 'search_news',
            'source': 'test_generator',
            'layer': 'speed',
            'data': {
                'news': [
                    {
                        'title': f'Test Article {i+1} - India Economy Update',
                        'url': f'https://example.com/article-{i+1}',
                        'publish_date': '2025-10-02',
                        'author': 'Test Author',
                        'text': f'This is test content for article {i+1}. ' * 20
                    }
                    for _ in range(3)
                ]
            }
        })
    
    # 2. Top News (3 messages)
    for i in range(3):
        messages.append({
            'timestamp': datetime.utcnow().isoformat(),
            'endpoint': 'top_news',
            'source': 'test_generator',
            'layer': 'speed',
            'data': {
                'top_news': [
                    {
                        'news': [
                            {'title': f'Cluster {i+1} Article {j+1}'}
                            for j in range(3)
                        ]
                    }
                    for _ in range(2)
                ]
            }
        })
    
    # 3. Extract News (3 messages)
    for i in range(3):
        messages.append({
            'timestamp': datetime.utcnow().isoformat(),
            'endpoint': 'extract_news',
            'source': 'test_generator',
            'layer': 'speed',
            'data': {
                'title': f'Extracted Article {i+1}',
                'author': f'Author {i+1}',
                'text': f'Full extracted content for article {i+1}. ' * 50,
                'url': f'https://example.com/extracted-{i+1}'
            }
        })
    
    # 4. Search Sources (3 messages)
    for i in range(3):
        messages.append({
            'timestamp': datetime.utcnow().isoformat(),
            'endpoint': 'search_news_sources',
            'source': 'test_generator',
            'layer': 'speed',
            'data': {
                'news_sources': [
                    {
                        'name': f'Test Source {j+1}',
                        'url': f'https://source{j+1}.com'
                    }
                    for j in range(5)
                ]
            }
        })
    
    # 5. Geo Coordinates (2 messages)
    cities = [
        {'name': 'Mumbai, India', 'lat': 19.0760, 'lon': 72.8777},
        {'name': 'Delhi, India', 'lat': 28.7041, 'lon': 77.1025}
    ]
    for city in cities:
        messages.append({
            'timestamp': datetime.utcnow().isoformat(),
            'endpoint': 'geo_coordinates',
            'source': 'test_generator',
            'layer': 'speed',
            'data': {
                'searched_location': city['name'],
                'latitude': city['lat'],
                'longitude': city['lon'],
                'city': city['name'].split(',')[0],
                'country': 'India'
            }
        })
    
    # 6. RSS Feed (2 messages)
    for i in range(2):
        messages.append({
            'timestamp': datetime.utcnow().isoformat(),
            'endpoint': 'feed_rss',
            'source': 'test_generator',
            'layer': 'speed',
            'data': {
                'source_url': f'https://example{i+1}.com',
                'content_length': 5000 + i*1000,
                'preview': f'<rss>Test RSS content {i+1}...</rss>'
            }
        })
    
    # 7. Extract Links (2 messages)
    for i in range(2):
        messages.append({
            'timestamp': datetime.utcnow().isoformat(),
            'endpoint': 'extract_news_links',
            'source': 'test_generator',
            'layer': 'speed',
            'data': {
                'extracted_urls': [
                    f'https://news{j+1}.com/article-{i+1}'
                    for j in range(3)
                ],
                'count': 3
            }
        })
    
    return messages


def send_test_data():
    """Send test data to Kafka"""
    
    print("="*60)
    print("TEST DATA GENERATOR")
    print("="*60)
    
    # Create producer
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            acks='all'
        )
        print(f"✓ Connected to Kafka: {KAFKA_SERVERS}")
    except Exception as e:
        print(f"✗ Kafka connection failed: {e}")
        print("\nMake sure Kafka is running:")
        print("  docker-compose up -d kafka")
        sys.exit(1)
    
    # Generate messages
    messages = create_test_messages()
    print(f"\n✓ Generated {len(messages)} test messages")
    
    # Send messages
    print("\nSending to Kafka...")
    print("-"*60)
    
    sent_count = 0
    endpoint_counts = {}
    
    for msg in messages:
        try:
            future = producer.send(TOPIC, value=msg)
            future.get(timeout=10)
            
            endpoint = msg['endpoint']
            endpoint_counts[endpoint] = endpoint_counts.get(endpoint, 0) + 1
            sent_count += 1
            
            print(f"  ✓ Sent #{sent_count}: {endpoint}")
            time.sleep(0.1)  # Small delay between messages
        
        except Exception as e:
            print(f"  ✗ Failed to send: {e}")
    
    producer.flush()
    producer.close()
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total sent: {sent_count}/{len(messages)}")
    print("\nBy endpoint:")
    for endpoint, count in sorted(endpoint_counts.items()):
        print(f"  {endpoint}: {count}")
    print("="*60)
    print("\nTest data ready! Now start consumers:")
    print("  docker-compose up -d speed-consumer batch-layer")


if __name__ == "__main__":
    send_test_data()