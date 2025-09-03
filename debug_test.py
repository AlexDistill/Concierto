#!/usr/bin/env python3
"""Test script to debug API issues"""

import asyncio
import aiohttp
import os
from pathlib import Path

async def test_openai_api():
    """Test if OpenAI API works with the key"""
    # Load API key from .env
    env_file = Path('.env')
    api_key = None
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('OPENAI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
    
    if not api_key:
        print("❌ No API key found in .env")
        return False
        
    print(f"🔑 API key found: {api_key[:20]}...")
    
    # Test basic API call
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Simple completion test
    payload = {
        "model": "gpt-4o-mini",  # Use a cheaper model for testing
        "messages": [
            {"role": "user", "content": "Say 'API works!'"}
        ],
        "max_tokens": 10
    }
    
    try:
        print("📡 Testing OpenAI API...")
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result['choices'][0]['message']['content']
                    print(f"✅ API Response: {content}")
                    return True
                else:
                    error = await response.text()
                    print(f"❌ API Error {response.status}: {error[:200]}")
                    return False
    except asyncio.TimeoutError:
        print("⏱️ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_image_analysis():
    """Test image analysis with a single image"""
    from image_analyzer import ImageAnalyzer
    
    # Load API key
    env_file = Path('.env')
    api_key = None
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('OPENAI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    break
    
    if not api_key:
        print("❌ No API key for image analysis")
        return
    
    # Find an image to test
    images_dir = Path("content/images")
    if not images_dir.exists():
        print("❌ No images directory")
        return
        
    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
    if not image_files:
        print("❌ No images found")
        return
    
    test_image = image_files[0]
    print(f"🖼️ Testing with image: {test_image.name}")
    
    analyzer = ImageAnalyzer(api_key)
    
    # Test with shorter timeout
    print("🤖 Starting analysis...")
    result = await analyzer.analyze_image(test_image)
    
    if result['success']:
        print("✅ Analysis successful!")
        print(f"   Description: {result['analysis'].get('content_description', 'N/A')[:100]}...")
        print(f"   AI Tags: {result['analysis'].get('ai_tags', [])}")
    else:
        print(f"❌ Analysis failed: {result['error']}")

async def main():
    """Run all tests"""
    print("="*50)
    print("Testing Concierto AI Components")
    print("="*50)
    
    # Test 1: Basic API connectivity
    api_works = await test_openai_api()
    
    # Test 2: Image analysis (only if API works)
    if api_works:
        print("\n" + "="*50)
        print("Testing Image Analysis")
        print("="*50)
        await test_image_analysis()
    else:
        print("\n⚠️ Skipping image analysis test due to API issues")
    
    print("\n" + "="*50)
    print("Tests Complete")
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())