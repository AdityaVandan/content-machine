#!/usr/bin/env python3

"""
Complete system test for Content Machine
"""

import requests
import json
import time

def test_system():
    """Test all system components"""
    base_url = "http://localhost:8000"
    
    print("🚀 Content Machine System Test")
    print("=" * 50)
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Frontend Access
    print("\n2. Testing Frontend Access...")
    try:
        response = requests.get(base_url)
        if "Content Machine" in response.text:
            print("   ✅ Frontend accessible")
        else:
            print("   ❌ Frontend not loading properly")
    except Exception as e:
        print(f"   ❌ Frontend error: {e}")
    
    # Test 3: API Status
    print("\n3. Testing API Status...")
    try:
        response = requests.get(f"{base_url}/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ API Status: {len(status['agents'])} agents, {len(status['platforms'])} platforms")
        else:
            print(f"   ❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status error: {e}")
    
    # Test 4: Platform Info
    print("\n4. Testing Platform Info...")
    try:
        response = requests.get(f"{base_url}/platforms")
        if response.status_code == 200:
            platforms = response.json()["platforms"]
            print(f"   ✅ Platforms available: {[p['name'] for p in platforms]}")
        else:
            print(f"   ❌ Platforms endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Platforms error: {e}")
    
    # Test 5: Content Types
    print("\n5. Testing Content Types...")
    try:
        response = requests.get(f"{base_url}/content-types")
        if response.status_code == 200:
            types = response.json()["content_types"]
            print(f"   ✅ Content types: {[t['name'] for t in types]}")
        else:
            print(f"   ❌ Content types endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Content types error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Content Machine System Test Complete!")
    print("\n📋 Access Points:")
    print(f"   • Frontend: {base_url}")
    print(f"   • API Docs: {base_url}/docs")
    print(f"   • Health: {base_url}/health")
    print(f"   • Status: {base_url}/status")
    
    print("\n🔧 Next Steps:")
    print("   1. Add OPENROUTER_API_KEY to .env for AI content generation")
    print("   2. Add platform API keys for actual publishing")
    print("   3. Start Celery worker: celery -A src.scheduler.tasks worker --loglevel=info")
    print("   4. Create content via web interface or API")

if __name__ == "__main__":
    test_system()
