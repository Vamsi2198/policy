#!/usr/bin/env python3
"""
AI Control Plane with OpenAI API key pre-configured
"""
import os
import sys

# Set the OpenAI API key from environment variable
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("❌ OPENAI_API_KEY environment variable not set!")
    sys.exit(1)

os.environ["OPENAI_API_KEY"] = openai_api_key

print("🔑 OpenAI API key configured!")
print(f"✅ Key preview: {os.environ['OPENAI_API_KEY'][:20]}...")

# Import and run AI Control Plane
from ai_control_plane import run_ai_control_plane

if __name__ == "__main__":
    print("\n🚀 Starting AI Control Plane with OpenAI mode...")
    run_ai_control_plane()