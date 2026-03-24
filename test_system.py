#!/usr/bin/env python3

"""
Test script for Content Machine system
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.models import ContentInput, Platform, ContentType
from src.core.pipeline import ContentPipeline

def test_content_pipeline():
    """Test the content creation pipeline"""
    print("🚀 Testing Content Machine Pipeline")
    print("=" * 50)
    
    # Create test input
    content_input = ContentInput(
        topic="Microservices Architecture Best Practices",
        keywords=["microservices", "architecture", "scalability", "docker"],
        target_platforms=[Platform.TWITTER, Platform.LINKEDIN],
        content_type=ContentType.BLOG,
        tone="professional",
        target_audience="tech professionals"
    )
    
    print(f"📝 Topic: {content_input.topic}")
    print(f"🎯 Platforms: {[p.value for p in content_input.target_platforms]}")
    print(f"📊 Content Type: {content_input.content_type.value}")
    print()
    
    # Initialize pipeline
    pipeline = ContentPipeline()
    
    # Test pipeline status
    status = pipeline.get_pipeline_status()
    print("🔧 Pipeline Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    print()
    
    print("✅ System components initialized successfully!")
    print("📋 To create actual content:")
    print("   1. Set OPENROUTER_API_KEY in .env file")
    print("   2. Start Redis server: redis-server")
    print("   3. Start Celery worker: celery -A src.scheduler.tasks worker --loglevel=info")
    print("   4. Use the web interface at http://localhost:8000")
    print("   5. Or use the API endpoints directly")

if __name__ == "__main__":
    test_content_pipeline()
