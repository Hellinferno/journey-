import requests
import json
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ZohoConnector:
    def __init__(self, auth_token=None, organization_id=None, client_id=None, client_secret=None):
        # Zoho API Endpoint (India Data Center)
        self.base_url = "https://www.zohoapis.in/books/v3"
        self.auth_url = "https://accounts.zoho.in/oauth/v2/token"
        self.org_id = organization_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = auth_token
        self.refresh_token = None
        self.token_expiry = None
        
        if auth_token:
            self.headers = {
                "Authorization": f"Zoho-oauthtoken {auth_token}",
                "Content-Type": "application/json"
            }
        else:
            self.headers = {"Content-Type": "application/json"}

    def exchange_code_for_token(self, grant_code, redirect_uri="http://www.zoho.com/books"):
        """
        Exchange authorization code for access token and refresh token.
        This is Step 2 of the OAuth flow.
        
        Args:
            grant_code: The authorization code from Step 1
            redirect_uri: Must match the redirect URI used in Step 1
            
        Returns:
            dict with access_token, refresh_token, and expires_in
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("client_id and client_secret are required for token exchange")
        
        payload = {
            "code": grant_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        
        try:
            response = requests.post(self.auth_url, data=payload)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                expires_in = token_data.get("expires_in_sec", 3600)
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                
                # Update headers with new token
                self.headers["Authorization"] = f"Zoho-oauthtoken {self.access_token}"
                
                logger.info("✅ Successfully exchanged code for access token")
                return {
                    "status": "success",
                    "access_token": self.access_token,
                    "refresh_token": self.refresh_token,
                    "expires_at": self.token_expiry.isoformat()
                }
            else:
                error_msg = response.json().get("error", "Unknown error")
                logger.error(f"❌ Token exchange failed: {error_msg}")
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            logger.error(f"❌ Token exchange error: {e}")
            return {"status": "error", "message": str(e)}

    def refresh_access_token(self):
        """
        Refresh the access token using the refresh token.
        Call this when the access token expires.
        
        Returns:
            dict with new access_token and expires_in
        """
        if not self.refresh_token:
            raise ValueError("refresh_token is required to refresh access token")
        
        if not self.client_id or not self.client_secret:
            raise ValueError("client_id and client_secret are required for token refresh")
        
        payload = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }
        
        try:
            response = requests.post(self.auth_url, data=payload)
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                expires_in = token_data.get("expires_in_sec", 3600)
                self.token_expiry = datetime.now() + timedelta(seconds=expires_in)
                
                # Update headers with new token
                self.headers["Authorization"] = f"Zoho-oauthtoken {self.access_token}"
                
                logger.info("✅ Successfully refreshed access token")
                return {
                    "status": "success",
                    "access_token": self.access_token,
                    "expires_at": self.token_expiry.isoformat()
                }
            else:
                error_msg = response.json().get("error", "Unknown error")
                logger.error(f"❌ Token refresh failed: {error_msg}")
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            logger.error(f"❌ Token refresh error: {e}")
            return {"status": "error", "message": str(e)}

    def is_token_expired(self):
        """Check if the access token has expired"""
        if not self.token_expiry:
            return True
        return datetime.now() >= self.token_expiry

    def ensure_valid_token(self):
        """Automatically refresh token if expired"""
        if self.is_token_expired() and self.refresh_token:
            logger.info("Token expired, refreshing...")
            return self.refresh_access_token()
        return {"status": "success", "message": "Token is valid"}

    def create_bill(self, invoice_data):
        """Pushes a Micro-CFO invoice to Zoho Books as a 'Bill'"""
        # Ensure token is valid before making API call
        self.ensure_valid_token()
        
        # 1. Map Micro-CFO data to Zoho Schema
        # We use the invoice ID to create a unique bill number
        bill_number = f"INV-{invoice_data.get('_id', '000')[-6:]}"
        
        payload = {
            "vendor_name": invoice_data.get('vendor', 'Unknown Vendor'),
            "bill_number": bill_number,
            "date": invoice_data.get('date', '2024-01-01'),
            "total": invoice_data.get('amount', 0),
            "gst_treatment": "business_gst" if invoice_data.get('gstin') else "business_none",
            "gst_no": invoice_data.get('gstin', ""),
            "line_items": [
                {
                    "name": f"{invoice_data.get('category', 'Expense')} - {invoice_data.get('item', 'Item')}",
                    "rate": invoice_data.get('amount', 0),
                    "quantity": 1,
                    "account_name": "General Expenses"  # You can map this dynamically later
                }
            ]
        }

        # 2. Send to Zoho
        url = f"{self.base_url}/bills?organization_id={self.org_id}"
        
        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(payload))
            
            if response.status_code == 201:
                logger.info(f"✅ Zoho Bill Created: {bill_number}")
                return {
                    "status": "success",
                    "id": response.json().get('bill', {}).get('bill_id'),
                    "message": "Bill created in Zoho Books"
                }
            else:
                error_msg = response.json().get('message', 'Unknown Error')
                logger.error(f"❌ Zoho Error: {error_msg}")
                return {"status": "error", "msg": error_msg}
                
        except Exception as e:
            logger.error(f"❌ Connection Error: {e}")
            return {"status": "error", "msg": str(e)}
