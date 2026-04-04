#!/usr/bin/env python3
"""
Comprehensive MinIO Bronze → Silver → Gold Verification
Validates all endpoints across all layers with proper structure checking
"""

import json
import subprocess
from pathlib import Path
from collections import defaultdict
import sys

def run_docker_cmd(cmd):
    """Run docker command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error running command: {e}")
        return ""

def setup_minio_client():
    """Setup MinIO client alias"""
    print("Setting up MinIO client...")
    cmd = 'docker exec minio mc alias set myminio http://localhost:9000 admin password123'
    run_docker_cmd(cmd)

def list_all_files(bucket):
    """Get all files from bucket with their paths, sorted by name"""
    cmd = f'docker exec minio mc ls myminio/{bucket} --recursive'
    output = run_docker_cmd(cmd)
    
    if not output:
        return []
    
    files = []
    for line in output.split('\n'):
        if '.json' in line and line.strip():
            parts = line.split()
            for i, part in enumerate(parts):
                if '.json' in part:
                    files.append(part)
                    break
    
    # Sort files by name (which includes timestamp)
    files.sort()
    return files

def download_file(bucket, file_path):
    """Download and parse JSON file from MinIO"""
    cmd = f'docker exec minio mc cat myminio/{bucket}/{file_path}'
    content = run_docker_cmd(cmd)
    
    if content and content.startswith('{'):
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            print(f"    JSON decode error for {file_path}: {e}")
            return None
    return None

def analyze_files_by_endpoint(bucket):
    """Group files by endpoint and analyze"""
    files = list_all_files(bucket)
    
    endpoint_files = defaultdict(list)
    
    for file_path in files:
        parts = file_path.split('/')
        if len(parts) >= 1:
            endpoint = parts[0]
            endpoint_files[endpoint].append(file_path)
    
    return endpoint_files

def validate_bronze_structure(data, endpoint):
    """Validate Bronze layer structure"""
    errors = []
    
    if data.get('layer') != 'bronze':
        errors.append(f"Wrong layer: {data.get('layer')}")
    
    if data.get('endpoint') != endpoint:
        errors.append(f"Endpoint mismatch: expected {endpoint}, got {data.get('endpoint')}")
    
    if 'ingestion_time' not in data:
        errors.append("Missing ingestion_time")
    
    if 'raw_message' not in data:
        errors.append("Missing raw_message")
    else:
        rm = data['raw_message']
        if 'data' not in rm:
            errors.append("Missing data in raw_message")
        if 'timestamp' not in rm:
            errors.append("Missing timestamp in raw_message")
    
    return errors

def validate_silver_structure(data, endpoint):
    """Validate Silver layer structure"""
    errors = []
    
    if data.get('layer') != 'silver':
        errors.append(f"Wrong layer: {data.get('layer')}")
    
    if data.get('endpoint') != endpoint:
        errors.append(f"Endpoint mismatch: expected {endpoint}, got {data.get('endpoint')}")
    
    if 'processed_time' not in data:
        errors.append("Missing processed_time")
    
    if 'cleaned_data' not in data:
        errors.append("Missing cleaned_data")
    else:
        cd = data['cleaned_data']
        
        # Check type field
        data_type = cd.get('type', 'unknown')
        
        if data_type == 'articles':
            if 'articles' not in cd:
                errors.append("Missing articles array for article-type endpoint")
            else:
                articles = cd['articles']
                if articles:
                    sample = articles[0]
                    required_fields = ['id', 'title', 'summary', 'url', 'source', 'category', 'sentiment']
                    for field in required_fields:
                        if field not in sample:
                            errors.append(f"Article missing field: {field}")
        
        elif data_type == 'urls':
            if 'urls' not in cd:
                errors.append("Missing urls array")
        
        elif data_type == 'rss_feed':
            if 'source_url' not in cd:
                errors.append("Missing source_url")
        
        elif data_type == 'geolocation':
            if 'latitude' not in cd or 'longitude' not in cd:
                errors.append("Missing coordinates")
    
    return errors

def validate_gold_structure(data, endpoint):
    """Validate Gold layer structure - handles different data types"""
    errors = []
    
    if data.get('layer') != 'gold':
        errors.append(f"Wrong layer: {data.get('layer')}")
    
    if data.get('endpoint') != endpoint:
        errors.append(f"Endpoint mismatch: expected {endpoint}, got {data.get('endpoint')}")
    
    if 'analytics_time' not in data:
        errors.append("Missing analytics_time")
    
    # Check metrics (required for ALL endpoints)
    if 'metrics' not in data:
        errors.append("Missing metrics")
    else:
        m = data['metrics']
        required_metrics = ['total_articles', 'sentiment_distribution', 'category_breakdown', 'top_sources']
        for metric in required_metrics:
            if metric not in m:
                errors.append(f"Missing metric: {metric}")
    
    # Check data_quality (required for ALL endpoints)
    if 'data_quality' not in data:
        errors.append("Missing data_quality section")
    
    # Type-specific validation
    data_type = data.get('data_type', 'unknown')
    
    if data_type == 'articles':
        if 'articles' not in data:
            errors.append("Missing articles array for article-type endpoint")
        if 'featured' not in data:
            errors.append("Missing featured section for article-type endpoint")
    
    elif data_type == 'urls':
        if 'urls' not in data:
            errors.append("Missing urls array")
        if 'domains' not in data:
            errors.append("Missing domains array")
    
    elif data_type == 'rss_feed':
        if 'rss_data' not in data:
            errors.append("Missing rss_data section")
    
    elif data_type == 'geolocation':
        if 'location_data' not in data:
            errors.append("Missing location_data section")
    
    elif data_type == 'news_sources':
        if 'sources' not in data:
            errors.append("Missing sources array")
    
    return errors

def analyze_endpoint_files(bucket, endpoint, files):
    """Analyze all files for a specific endpoint"""
    print(f"\n  Endpoint: {endpoint}")
    print(f"  Files: {len(files)}")
    
    if not files:
        print(f"    No files found")
        return None
    
    # Get the latest file (last in sorted list)
    latest_file = files[-1]
    data = download_file(bucket, latest_file)
    
    if not data:
        print(f"    Failed to download {latest_file}")
        return None
    
    # Validate based on layer
    if bucket == 'bronze-raw':
        errors = validate_bronze_structure(data, endpoint)
    elif bucket == 'silver-cleaned':
        errors = validate_silver_structure(data, endpoint)
    elif bucket == 'gold-analytics':
        errors = validate_gold_structure(data, endpoint)
    else:
        errors = ["Unknown bucket"]
    
    if errors:
        print(f"    Validation errors:")
        for error in errors:
            print(f"      - {error}")
        return {'valid': False, 'errors': errors, 'data': data}
    else:
        print(f"    ✓ Valid structure")
        
        # Print useful stats
        if bucket == 'silver-cleaned' and 'cleaned_data' in data:
            cd = data['cleaned_data']
            data_type = cd.get('type', 'unknown')
            print(f"    Data type: {data_type}")
            
            if 'articles' in cd:
                print(f"    Articles: {len(cd['articles'])}")
            elif 'urls' in cd:
                print(f"    URLs: {len(cd['urls'])}")
        
        if bucket == 'gold-analytics':
            data_type = data.get('data_type', 'unknown')
            print(f"    Data type: {data_type}")
            
            if 'metrics' in data:
                m = data['metrics']
                print(f"    Total articles: {m.get('total_articles', 0)}")
            
            if data_type == 'articles' and 'articles' in data:
                print(f"    Article records: {len(data['articles'])}")
                unknown = sum(1 for a in data['articles'] if a.get('source') == 'Unknown')
                if unknown > 0:
                    print(f"    Unknown sources: {unknown}/{len(data['articles'])}")
        
        return {'valid': True, 'errors': [], 'data': data}

def save_sample_files(results):
    """Save sample files for each endpoint"""
    output_dir = Path('minio_verification_detailed')
    output_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*60)
    print("Saving Sample Files...")
    print("="*60)
    
    for layer, endpoints in results.items():
        layer_dir = output_dir / layer
        layer_dir.mkdir(exist_ok=True)
        
        for endpoint, result in endpoints.items():
            if result and result.get('data'):
                filename = f"{endpoint}.json"
                filepath = layer_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(result['data'], f, indent=2)
                
                print(f"  Saved: {filepath}")

def main():
    print("="*60)
    print("MinIO Data Layer Verification")
    print("Validating Bronze → Silver → Gold Pipeline")
    print("="*60)
    
    setup_minio_client()
    
    buckets = {
        'bronze-raw': 'Bronze (Raw Data)',
        'silver-cleaned': 'Silver (Cleaned Data)',
        'gold-analytics': 'Gold (Analytics)'
    }
    
    all_results = {}
    summary = {
        'total_endpoints': set(),
        'valid_bronze': 0,
        'valid_silver': 0,
        'valid_gold': 0,
        'errors': []
    }
    
    # Analyze each bucket
    for bucket, bucket_name in buckets.items():
        print("\n" + "="*60)
        print(f"Analyzing {bucket_name} ({bucket})")
        print("="*60)
        
        endpoint_files = analyze_files_by_endpoint(bucket)
        
        if not endpoint_files:
            print(f"  No files found in {bucket}")
            summary['errors'].append(f"No files in {bucket}")
            continue
        
        print(f"  Found {len(endpoint_files)} endpoints")
        
        layer_results = {}
        
        for endpoint, files in sorted(endpoint_files.items()):
            result = analyze_endpoint_files(bucket, endpoint, files)
            layer_results[endpoint] = result
            
            summary['total_endpoints'].add(endpoint)
            
            if result and result['valid']:
                if bucket == 'bronze-raw':
                    summary['valid_bronze'] += 1
                elif bucket == 'silver-cleaned':
                    summary['valid_silver'] += 1
                elif bucket == 'gold-analytics':
                    summary['valid_gold'] += 1
        
        all_results[bucket] = layer_results
    
    # Final Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    total_endpoints = len(summary['total_endpoints'])
    print(f"\nTotal Unique Endpoints: {total_endpoints}")
    print(f"  Endpoints: {', '.join(sorted(summary['total_endpoints']))}")
    
    print(f"\nLayer Validation:")
    print(f"  Bronze:  {summary['valid_bronze']}/{total_endpoints} valid")
    print(f"  Silver:  {summary['valid_silver']}/{total_endpoints} valid")
    print(f"  Gold:    {summary['valid_gold']}/{total_endpoints} valid")
    
    # Detailed endpoint breakdown
    print("\n" + "="*60)
    print("Endpoint-by-Endpoint Breakdown")
    print("="*60)
    
    for endpoint in sorted(summary['total_endpoints']):
        print(f"\n{endpoint}:")
        
        for bucket, bucket_name in buckets.items():
            if bucket in all_results and endpoint in all_results[bucket]:
                result = all_results[bucket][endpoint]
                if result:
                    status = "✓ VALID" if result['valid'] else "✗ INVALID"
                    print(f"  {bucket_name}: {status}")
                    if not result['valid']:
                        for error in result['errors'][:3]:
                            print(f"    - {error}")
                else:
                    print(f"  {bucket_name}: NO DATA")
            else:
                print(f"  {bucket_name}: NOT FOUND")
    
    # Save samples
    save_sample_files(all_results)
    
    # Final verdict
    print("\n" + "="*60)
    
    if summary['valid_bronze'] == summary['valid_silver'] == summary['valid_gold'] == total_endpoints:
        print("✓ SUCCESS: All endpoints validated across all 3 layers!")
        print("\nYour pipeline is working correctly.")
        print("\nSample files saved to: ./minio_verification_detailed/")
        print("  - bronze-raw/")
        print("  - silver-cleaned/")
        print("  - gold-analytics/")
    else:
        print("✗ ISSUES DETECTED: Some endpoints have validation errors")
        print("\nTroubleshooting:")
        print("  1. Check Flink logs: docker logs batch-layer --tail 100")
        print("  2. Check Producer logs: docker logs speed-producer --tail 100")
        print("  3. Review saved samples in: ./minio_verification_detailed/")
        print("  4. Verify flink_job.py is deployed correctly")
    
    print("="*60)
    
    return 0 if summary['valid_bronze'] == summary['valid_silver'] == summary['valid_gold'] == total_endpoints else 1

if __name__ == "__main__":
    sys.exit(main())