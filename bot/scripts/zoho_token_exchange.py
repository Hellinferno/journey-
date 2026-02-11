"""
Zoho OAuth Token Exchange Script

This script helps you exchange your authorization code (grant token) for an access token.

Usage:
    python scripts/zoho_token_exchange.py

Make sure to set these environment variables in your .env file:
    ZOHO_CLIENT_ID=your_client_id
    ZOHO_CLIENT_SECRET=your_client_secret
    ZOHO_GRANT_CODE=your_grant_code_from_step_1
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.integrations.zoho import ZohoConnector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    # Get credentials from environment
    client_id = os.getenv("ZOHO_CLIENT_ID")
    client_secret = os.getenv("ZOHO_CLIENT_SECRET")
    grant_code = os.getenv("ZOHO_GRANT_CODE")
    redirect_uri = os.getenv("ZOHO_REDIRECT_URI", "http://www.zoho.com/books")
    
    # Validate inputs
    if not client_id:
        print("❌ Error: ZOHO_CLIENT_ID not found in .env file")
        return
    
    if not client_secret:
        print("❌ Error: ZOHO_CLIENT_SECRET not found in .env file")
        return
    
    if not grant_code:
        print("❌ Error: ZOHO_GRANT_CODE not found in .env file")
        print("\nTo get your grant code:")
        print("1. Go to: https://accounts.zoho.in/oauth/v2/auth")
        print(f"2. Add these parameters: ?client_id={client_id}&response_type=code&scope=ZohoBooks.fullaccess.all&redirect_uri={redirect_uri}&access_type=offline")
        print("3. Copy the 'code' parameter from the redirect URL")
        print("4. Add it to your .env file as ZOHO_GRANT_CODE=your_code")
        return
    
    print("🔄 Exchanging authorization code for access token...")
    print(f"Client ID: {client_id[:10]}...")
    print(f"Grant Code: {grant_code[:20]}...")
    
    # Initialize connector
    connector = ZohoConnector(
        client_id=client_id,
        client_secret=client_secret
    )
    
    # Exchange code for token
    result = connector.exchange_code_for_token(grant_code, redirect_uri)
    
    if result["status"] == "success":
        print("\n✅ Token exchange successful!")
        print("\n📋 Add these to your .env file:")
        print(f"ZOHO_TOKEN={result['access_token']}")
        print(f"ZOHO_REFRESH_TOKEN={result['refresh_token']}")
        print(f"\n⏰ Token expires at: {result['expires_at']}")
        print("\n💡 The refresh token can be used to get new access tokens when they expire.")
        print("\nNote: ZOHO_TOKEN is your access token (expires in 1 hour)")
        print("      ZOHO_REFRESH_TOKEN is used to get new access tokens automatically")
    else:
        print(f"\n❌ Token exchange failed: {result.get('message', 'Unknown error')}")
        print("\nCommon issues:")
        print("- Grant code already used (they expire after first use)")
        print("- Grant code expired (valid for ~3 minutes)")
        print("- Redirect URI mismatch")
        print("- Invalid client credentials")

if __name__ == "__main__":
    main()
