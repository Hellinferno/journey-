"""
Example: Integrating Zoho Books with Micro-CFO Bot

This example shows how to automatically push compliant invoices to Zoho Books.
"""

import os
from dotenv import load_dotenv
from app.integrations.zoho import ZohoConnector

# Load environment variables
load_dotenv()

def setup_zoho_connector():
    """Initialize Zoho connector with credentials from .env"""
    connector = ZohoConnector(
        auth_token=os.getenv("ZOHO_TOKEN"),
        organization_id=os.getenv("ZOHO_ORGANIZATION_ID"),
        client_id=os.getenv("ZOHO_CLIENT_ID"),
        client_secret=os.getenv("ZOHO_CLIENT_SECRET")
    )
    
    # Set refresh token for automatic renewal
    connector.refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
    
    return connector

def push_invoice_to_zoho(invoice_data):
    """
    Push a Micro-CFO invoice to Zoho Books as a Bill
    
    Args:
        invoice_data: Dict with invoice details from Convex
        
    Returns:
        Result dict with status and message
    """
    connector = setup_zoho_connector()
    
    # The connector automatically refreshes expired tokens
    result = connector.create_bill(invoice_data)
    
    return result

# Example usage in your bot workflow
if __name__ == "__main__":
    # Sample invoice data from Micro-CFO
    sample_invoice = {
        "_id": "abc123def456",
        "vendor": "Office Supplies Ltd",
        "amount": 5000.00,
        "gstin": "29ABCDE1234F1Z5",
        "category": "Office Expenses",
        "item": "Stationery",
        "date": "2024-01-15"
    }
    
    # Push to Zoho Books
    result = push_invoice_to_zoho(sample_invoice)
    
    if result["status"] == "success":
        print(f"✅ Bill created in Zoho Books: {result['id']}")
    else:
        print(f"❌ Failed to create bill: {result['msg']}")

# Integration with bot.py
"""
Add this to your bot.py after compliance check:

from app.integrations.zoho import ZohoConnector

async def handle_invoice(update, context):
    # ... existing invoice processing ...
    
    # After compliance check, if invoice is compliant:
    if compliance_result.get("itc_eligible"):
        # Push to Zoho Books
        zoho_result = push_invoice_to_zoho(invoice_data)
        
        if zoho_result["status"] == "success":
            await update.message.reply_text(
                "✅ Invoice synced to Zoho Books!"
            )
"""
