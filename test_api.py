#!/usr/bin/env python3
"""
Test OpenAI API connection
"""

import os
import asyncio
import aiohttp
from pathlib import Path

async def test_api():
    # Load .env file
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ No API key found in .env file")
        return
    
    print(f"✅ API Key found: {api_key[:10]}...{api_key[-4:]}")
    print("\n🧪 Testing OpenAI API connection...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test with a simple chat completion
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 10
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("✅ API Connection successful!")
                    print(f"Response: {result['choices'][0]['message']['content']}")
                else:
                    error_text = await response.text()
                    print(f"❌ API Error: {error_text}")
                    
                    # Common error explanations
                    if response.status == 401:
                        print("\n💡 Error 401: Invalid API key. Please check your key.")
                    elif response.status == 429:
                        print("\n💡 Error 429: Rate limit exceeded or quota issue.")
                    elif response.status == 404:
                        print("\n💡 Error 404: Model not found. Try 'gpt-4-vision-preview' or 'gpt-4o'")
                    
    except asyncio.TimeoutError:
        print("❌ Request timed out (30 seconds)")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api())