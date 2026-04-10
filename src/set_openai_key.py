#!/usr/bin/env python3
"""
Set OpenAI API key and test AI Control Plane
"""
import os

# Set the OpenAI API key from environment variable
openai_key = os.getenv("OPENAI_API_KEY")
if openai_key:
    os.environ["OPENAI_API_KEY"] = openai_key
    print("✅ OpenAI API key has been set from environment variable!")
    print(f"Key preview: {openai_key[:20]}...")
else:
    print("❌ OPENAI_API_KEY environment variable not set!")
    print("Please set the OPENAI_API_KEY environment variable first.")

# Test the key detection
print("\n🧪 Testing API key detection:")
anthropic_key = os.getenv('ANTHROPIC_API_KEY')
openai_key = os.getenv('OPENAI_API_KEY')

print(f"ANTHROPIC_API_KEY: {'✅ SET' if anthropic_key else '❌ NOT SET'}")
print(f"OPENAI_API_KEY: {'✅ SET' if openai_key else '❌ NOT SET'}")

if openai_key:
    print(f"\n🎯 AI Control Plane will now use OpenAI mode!")
    print(f"Key length: {len(openai_key)} characters")
    print(f"Starts with: {openai_key[:10]}...")