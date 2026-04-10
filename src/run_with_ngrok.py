#!/usr/bin/env python3
"""
Run Flask app with ngrok tunneling
"""
import os
import sys
from pyngrok import ngrok

# Set your ngrok auth token
ngrok.set_auth_token("38hdQIU3gpeqZPPBhL3rYTOsmia_4XqcUJsBxT3iLQv8vsnRX")

# Import and run the Flask app
from atlan_api_server import app

if __name__ == '__main__':
    # Open a tunnel to the Flask app
    public_url = ngrok.connect(5000, "http")
    print(f"\n{'='*60}")
    print(f"🌐 Your app is now publicly accessible at:")
    print(f"   {public_url}")
    print(f"{'='*60}\n")
    
    # Run the Flask app
    app.run(debug=True, use_reloader=False)
