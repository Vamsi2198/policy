import os

# Set OpenAI key from environment variable
openai_key_env = os.getenv("OPENAI_API_KEY")
if openai_key_env:
    os.environ["OPENAI_API_KEY"] = openai_key_env
else:
    print("⚠️  OPENAI_API_KEY environment variable not set - using fallback for testing")

# Test detection logic from ai_control_plane.py
anthropic_key = os.getenv('ANTHROPIC_API_KEY')
openai_key = os.getenv('OPENAI_API_KEY')

use_llm = bool(anthropic_key or openai_key)

print("API Key Detection Test:")
print(f"ANTHROPIC_API_KEY: {'SET' if anthropic_key else 'NOT SET'}")  
print(f"OPENAI_API_KEY: {'SET' if openai_key else 'NOT SET'}")
print(f"use_llm: {use_llm}")

if anthropic_key:
    print("✅ ANTHROPIC_API_KEY detected - using Claude mode")
elif openai_key:
    print("✅ OPENAI_API_KEY detected - using OpenAI mode")
else:
    print("⚠️  No API keys set - using local/template mode")

print(f"\nKey length: {len(openai_key) if openai_key else 0}")
print("OpenAI mode ready!")