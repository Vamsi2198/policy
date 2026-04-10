#!/usr/bin/env python3
"""
Start secure public tunnels for local services using ngrok.
- Exposes Flask (port 5000)
- Exposes Streamlit (port 8501) if running

Usage:
    python start_ngrok.py

Optional: set NGROK_AUTHTOKEN for stable tunnels
    PowerShell:
        setx NGROK_AUTHTOKEN "<your-token>"
"""
import os
import time
from pathlib import Path
from pyngrok import ngrok

SCRIPT_DIR = Path(__file__).parent
OUTPUT_FILE = SCRIPT_DIR / "public_urls.txt"

# Read optional authtoken
token = os.getenv("NGROK_AUTHTOKEN")
if token:
    try:
        ngrok.set_auth_token(token)
    except Exception as e:
        print(f"[WARN] Failed to set auth token: {e}")
else:
    print("[INFO] NGROK_AUTHTOKEN not set. Running without account (limited).")

print("\n⚡ Starting public tunnels via ngrok...\n")

urls = {}

def open_tunnel(port: int, name: str):
    try:
        tunnel = ngrok.connect(addr=f"http://localhost:{port}", bind_tls=True)
        public_url = tunnel.public_url
        urls[name] = public_url
        print(f"[SUCCESS] {name} ({port}) → {public_url}")
    except Exception as e:
        print(f"[ERROR] Could not open tunnel for {name} on port {port}: {e}")

# Flask (5000)
open_tunnel(5000, "Flask")

# Streamlit (8501)
open_tunnel(8501, "Streamlit")

# Write URLs to file for easy sharing
try:
    OUTPUT_FILE.write_text("\n".join([f"{k}: {v}" for k, v in urls.items()]))
    print(f"\n[INFO] URLs saved to: {OUTPUT_FILE}")
except Exception as e:
    print(f"[WARN] Could not write URLs file: {e}")

if urls:
    print("\nShare these links with anyone (works from anywhere):")
    for k, v in urls.items():
        print(f"  • {k}: {v}")
else:
    print("\n[ERROR] No tunnels opened. Check internet access or ngrok setup.")

print("\n[INFO] Keeping tunnels alive. Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n[INFO] Stopping tunnels...")
    try:
        ngrok.kill()
    except Exception:
        pass
