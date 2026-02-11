# Zoho OAuth Setup Guide

This guide walks you through setting up OAuth authentication for Zoho Books integration.

## Prerequisites

1. Zoho Books account (India data center)
2. Zoho API Console credentials (Client ID & Client Secret)

## Step 1: Get Authorization Code (Grant Token)

Visit this URL in your browser (replace `YOUR_CLIENT_ID` with your actual client ID):

```
https://accounts.zoho.in/oauth/v2/auth?client_id=YOUR_CLIENT_ID&response_type=code&scope=ZohoBooks.fullaccess.all&redirect_uri=http://www.zoho.com/books&access_type=offline
```

**Parameters explained:**
- `client_id`: Your Zoho API client ID
- `response_type=code`: Request an authorization code
- `scope=ZohoBooks.fullaccess.all`: Full access to Zoho Books
- `redirect_uri`: Must match what you registered in Zoho API Console
- `access_type=offline`: Get a refresh token for long-term access

After authorizing, you'll be redirected to a URL like:
```
http://www.zoho.com/books?code=1000.58b61e74b9852a29ed74506bba99a835.887f34bdbc531d0228df51daa22618d8
```

Copy the `code` parameter value - this is your **grant token**.

⚠️ **Important**: Grant tokens expire in ~3 minutes and can only be used once!

## Step 2: Exchange Code for Access Token

### Option A: Using the Python Script (Recommended)

1. Add to your `.env` file:
```env
ZOHO_CLIENT_ID=your_client_id
ZOHO_CLIENT_SECRET=your_client_secret
ZOHO_GRANT_CODE=1000.58b61e74b9852a29ed74506bba99a835.887f34bdbc531d0228df51daa22618d8
ZOHO_REDIRECT_URI=http://www.zoho.com/books
```

2. Run the exchange script:
```bash
python scripts/zoho_token_exchange.py
```

3. Copy the output tokens to your `.env` file:
```env
ZOHO_TOKEN=1000.xxxxx.xxxxx
ZOHO_REFRESH_TOKEN=1000.xxxxx.xxxxx
ZOHO_ORGANIZATION_ID=your_org_id
```

### Option B: Using cURL

```bash
curl -X POST "https://accounts.zoho.in/oauth/v2/token" \
  -d "code=YOUR_GRANT_TOKEN_FROM_STEP_1" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=http://www.zoho.com/books" \
  -d "grant_type=authorization_code"
```

Response:
```json
{
  "access_token": "1000.xxxxx.xxxxx",
  "refresh_token": "1000.xxxxx.xxxxx",
  "expires_in_sec": 3600,
  "api_domain": "https://www.zohoapis.in",
  "token_type": "Bearer"
}
```

Copy the `access_token` and paste it into your `.env` file as `ZOHO_TOKEN`.

## Step 3: Get Your Organization ID

```bash
curl -X GET "https://www.zohoapis.in/books/v3/organizations" \
  -H "Authorization: Zoho-oauthtoken YOUR_ACCESS_TOKEN"
```

Copy the `organization_id` from the response.

## Step 4: Use in Your Code

```python
from app.integrations.zoho import ZohoConnector
import os

# Initialize with tokens
connector = ZohoConnector(
    auth_token=os.getenv("ZOHO_TOKEN"),
    organization_id=os.getenv("ZOHO_ORGANIZATION_ID"),
    client_id=os.getenv("ZOHO_CLIENT_ID"),
    client_secret=os.getenv("ZOHO_CLIENT_SECRET")
)

# Set refresh token for automatic token renewal
connector.refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")

# Create a bill - tokens will auto-refresh if expired
result = connector.create_bill(invoice_data)
```

## Token Management

### Access Token
- Valid for 1 hour
- Used for API requests
- Automatically refreshed by `ZohoConnector`

### Refresh Token
- Valid indefinitely (until revoked)
- Used to get new access tokens
- Store securely in `.env` file

### Auto-Refresh
The `ZohoConnector` class automatically refreshes expired tokens:

```python
# This happens automatically before each API call
connector.ensure_valid_token()
```

## Troubleshooting

### "Invalid Code" Error
- Grant codes expire in 3 minutes
- Grant codes can only be used once
- Solution: Get a new grant code from Step 1

### "Invalid Client" Error
- Check your client ID and secret
- Ensure you're using the correct data center (`.in` for India)

### "Invalid Redirect URI" Error
- Redirect URI must exactly match what's registered in Zoho API Console
- Include protocol (`http://` or `https://`)

### Token Expired
- Access tokens expire after 1 hour
- Use the refresh token to get a new access token
- The connector handles this automatically

## Security Best Practices

1. ✅ Store tokens in `.env` file (never commit to git)
2. ✅ Add `.env` to `.gitignore`
3. ✅ Use refresh tokens for long-term access
4. ✅ Rotate tokens periodically
5. ❌ Never hardcode tokens in source code
6. ❌ Never share tokens publicly

## Environment Variables Summary

```env
# Zoho API Credentials
ZOHO_CLIENT_ID=1000.XXXXXXXXXXXXX
ZOHO_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxx

# OAuth Tokens (from token exchange)
ZOHO_TOKEN=1000.xxxxx.xxxxx
ZOHO_REFRESH_TOKEN=1000.xxxxx.xxxxx

# Zoho Books Configuration
ZOHO_ORGANIZATION_ID=123456789
ZOHO_REDIRECT_URI=http://www.zoho.com/books
```
