#!/usr/bin/env python3
"""
AI Setup script for Concierto image analysis.
Helps configure OpenAI API key for intelligent image understanding.
"""

import os
import sys
from pathlib import Path

def setup_ai_analysis():
    """Interactive setup for AI image analysis"""
    
    print("🤖 Concierto AI Image Analysis Setup")
    print("=" * 40)
    print()
    
    # Check if API key is already set
    existing_key = os.getenv('OPENAI_API_KEY')
    if existing_key:
        print(f"✅ OpenAI API key is already configured")
        print(f"   Key: {existing_key[:8]}...{existing_key[-4:] if len(existing_key) > 12 else 'short'}")
        
        response = input("\nDo you want to update it? (y/N): ").strip().lower()
        if response != 'y':
            print("Keeping existing API key.")
            return test_api_key(existing_key)
    
    print("To enable AI image analysis, you need an OpenAI API key.")
    print()
    print("🔑 How to get an API key:")
    print("1. Go to: https://platform.openai.com/api-keys")
    print("2. Sign in or create an account")
    print("3. Click 'Create new secret key'")
    print("4. Copy the key (starts with 'sk-')")
    print()
    
    # Get API key from user
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("⚠️ No API key provided. AI analysis will be disabled.")
        print("   You can still use the dashboard with basic filename-based tagging.")
        return False
    
    # Validate key format
    if not api_key.startswith('sk-'):
        print("❌ Invalid API key format. Keys should start with 'sk-'")
        return False
    
    # Set environment variable for current session
    os.environ['OPENAI_API_KEY'] = api_key
    
    # Save to .env file for persistence
    env_file = Path('.env')
    try:
        # Read existing .env file
        env_content = ""
        if env_file.exists():
            env_content = env_file.read_text()
        
        # Remove existing OPENAI_API_KEY line
        lines = env_content.split('\n')
        lines = [line for line in lines if not line.startswith('OPENAI_API_KEY=')]
        
        # Add new API key
        lines.append(f'OPENAI_API_KEY={api_key}')
        
        # Write back to file
        env_file.write_text('\n'.join(lines))
        
        print("✅ API key saved to .env file")
        
    except Exception as e:
        print(f"⚠️ Could not save to .env file: {e}")
        print("   You'll need to set OPENAI_API_KEY manually each session")
    
    # Test the API key
    return test_api_key(api_key)

def test_api_key(api_key):
    """Test if the API key works"""
    print("\n🧪 Testing API key...")
    
    try:
        import aiohttp
        import asyncio
        import json
        
        async def test_api():
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Simple test request
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 5
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return True, "API key is valid"
                    else:
                        error_text = await response.text()
                        return False, f"API error: {response.status} - {error_text}"
        
        # Run test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            success, message = loop.run_until_complete(test_api())
            if success:
                print("✅ API key is working!")
                print("🎉 AI image analysis is now enabled")
                return True
            else:
                print(f"❌ API key test failed: {message}")
                return False
        finally:
            loop.close()
            
    except ImportError:
        print("⚠️ aiohttp not installed. Cannot test API key.")
        print("   Install with: pip install aiohttp")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def show_usage():
    """Show how to use the AI features"""
    print("\n🚀 How to use AI Image Analysis:")
    print("=" * 35)
    print()
    print("1. Start the server:")
    print("   python3 simple_server.py")
    print()
    print("2. Add images to content/images/")
    print()
    print("3. Click 'Scan for New Content' in the dashboard")
    print()
    print("4. See AI-powered:")
    print("   • Intelligent descriptions")
    print("   • Auto-generated tags (marked with 🤖)")
    print("   • Creative insights")
    print("   • Technical analysis")
    print()
    print("💡 The AI will analyze:")
    print("   • What's in the image")
    print("   • Visual style and mood")
    print("   • Design principles used")
    print("   • Potential use cases")
    print("   • Relevant tags for creative work")

def main():
    """Main setup function"""
    try:
        success = setup_ai_analysis()
        
        if success:
            show_usage()
        else:
            print("\n💡 Don't worry! The dashboard still works without AI.")
            print("   It will use filename-based tagging instead.")
        
        print(f"\n🎼 Start the dashboard with: python3 simple_server.py")
        
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()