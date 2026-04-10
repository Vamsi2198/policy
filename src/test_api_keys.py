#!/usr/bin/env python3
"""
Test API key detection fix
"""
import os

def test_api_key_detection():
    """Test the updated API key detection logic"""
    print("🧪 Testing API Key Detection")
    print("=" * 40)
    
    # Check current environment
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"ANTHROPIC_API_KEY: {'✅ SET' if anthropic_key else '❌ NOT SET'}")
    print(f"OPENAI_API_KEY: {'✅ SET' if openai_key else '❌ NOT SET'}")
    
    # Simulate the new logic
    use_llm = bool(anthropic_key or openai_key)
    
    if anthropic_key:
        mode = "Claude (Anthropic)"
    elif openai_key:
        mode = "OpenAI (GPT)"
    else:
        mode = "Local/Template"
    
    print(f"\nDetected Mode: {mode}")
    print(f"use_llm: {use_llm}")
    
    # Show what message would be displayed
    print("\n📋 Message that would be shown:")
    if anthropic_key:
        print("✅ ANTHROPIC_API_KEY detected - using Claude mode")
    elif openai_key:
        print("✅ OPENAI_API_KEY detected - using OpenAI mode")
    else:
        print("⚠️  No API keys set - using local/template mode")
        print("   For best results: export ANTHROPIC_API_KEY='your-key' or OPENAI_API_KEY='your-key'")

if __name__ == "__main__":
    test_api_key_detection()