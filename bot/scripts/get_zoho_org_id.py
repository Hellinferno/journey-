"""
Get Zoho Organization ID

This script fetches your Zoho Books organization ID using your access token.

Usage:
    python scripts/get_zoho_org_id.py

Make sure ZOHO_TOKEN is set in your .env file first.
"""

import os
import sys
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_organization_id():
    """Fetch organization ID from Zoho Books API"""
    access_token = os.getenv("ZOHO_TOKEN")
    
    if not access_token:
        print("❌ Error: ZOHO_TOKEN not found in .env file")
        print("\nPlease run the token exchange script first:")
        print("  python scripts/zoho_token_exchange.py")
        return
    
    print("🔍 Fetching your Zoho Books organization(s)...")
    
    url = "https://www.zohoapis.in/books/v3/organizations"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            organizations = data.get("organizations", [])
            
            if not organizations:
                print("❌ No organizations found in your Zoho Books account")
                return
            
            print(f"\n✅ Found {len(organizations)} organization(s):\n")
            
            for org in organizations:
                print(f"Organization Name: {org.get('name')}")
                print(f"Organization ID: {org.get('organization_id')}")
                print(f"Currency: {org.get('currency_code')}")
                print(f"Status: {org.get('account_created_date')}")
                print("-" * 50)
            
            # If only one org, provide direct instruction
            if len(organizations) == 1:
                org_id = organizations[0].get('organization_id')
                print(f"\n📋 Add this to your .env file:")
                print(f"ZOHO_ORG_ID={org_id}")
            else:
                print("\n💡 You have multiple organizations.")
                print("Choose the organization_id you want to use and add it to your .env file:")
                print("ZOHO_ORG_ID=your_chosen_org_id")
                
        elif response.status_code == 401:
            print("❌ Authentication failed. Your access token may be expired.")
            print("\nTry refreshing your token:")
            print("1. Run: python scripts/zoho_token_exchange.py")
            print("2. Update ZOHO_TOKEN in your .env file")
            print("3. Run this script again")
        else:
            error_data = response.json()
            error_msg = error_data.get("message", "Unknown error")
            print(f"❌ API Error: {error_msg}")
            print(f"Status Code: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_organization_id()
