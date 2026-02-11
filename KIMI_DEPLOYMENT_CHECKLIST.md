# Kimi K2.5 Deployment Checklist

## Required Environment Variables in Railway

You must set these 4 variables in Railway Dashboard → Variables tab:

### 1. TELEGRAM_TOKEN
```
Your Telegram bot token from @BotFather
```

### 2. NVIDIA_API_KEY
```
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
```

### 3. GOOGLE_API_KEY
```
Your Google API key (for embeddings only)
```

### 4. CONVEX_URL
```
Your Convex deployment URL
```

## Common Deployment Issues

### Issue 1: Missing Environment Variables

**Error:**
```
ValueError: Missing required environment variable: NVIDIA_API_KEY
ValueError: Missing required environment variable: GOOGLE_API_KEY
ValueError: Missing TELEGRAM_TOKEN environment variable
```

**Solution:**
1. Go to Railway Dashboard → Your Service → Variables tab
2. Verify ALL 4 variables are set
3. Check for typos in variable names (case-sensitive!)
4. Redeploy after adding variables

### Issue 2: Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'google'
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
- This should be fixed automatically by requirements.txt
- If persists, check Railway build logs for pip install errors

### Issue 3: NVIDIA API Errors

**Error:**
```
requests.exceptions.HTTPError: 401 Unauthorized
requests.exceptions.HTTPError: 403 Forbidden
```

**Solution:**
- Verify NVIDIA_API_KEY is correct
- Check if API key has access to Kimi K2.5 model
- Ensure no extra spaces in the API key value

### Issue 4: Image Processing Errors

**Error:**
```
TypeError: expected str, bytes or os.PathLike object, not NoneType
PIL.UnidentifiedImageError: cannot identify image file
```

**Solution:**
- This is usually a temporary file handling issue
- Check Railway logs for specific error details
- May need to adjust image format detection

## Verification Steps

After deployment, check Railway logs for these success indicators:

### 1. Startup Success
```
✅ TELEGRAM_TOKEN loaded: 8314910661...
✅ CONVEX_URL loaded: https://woozy-chihuahua-345.convex.cloud
INFO - Starting Micro-CFO Bot...
```

### 2. Bot Running
```
INFO - Application started
INFO - Bot is running
```

### 3. No Import Errors
```
# Should NOT see:
❌ ModuleNotFoundError
❌ ImportError
```

## Testing the Bot

Once deployed:

1. **Send /start to your bot**
   - Should receive welcome message
   - If no response, check Railway logs

2. **Send an invoice image**
   - Bot should reply "📸 Analyzing Invoice..."
   - Should receive analysis results
   - If fails, check Railway logs for API errors

## Debugging Commands

### Check Railway Logs
```bash
# In Railway Dashboard
Deployments → Latest Deployment → View Logs
```

### Look for these log entries:
- `📤 Sending to Kimi K2.5...` - Invoice analysis started
- `📥 Parsed: {...}` - JSON response received
- `✅ Analysis Complete` - Processing successful
- `❌ Analysis Error:` - Processing failed (check error details)

## Environment Variable Format

Ensure variables are set exactly like this in Railway:

| Variable Name | Example Value |
|---------------|---------------|
| TELEGRAM_TOKEN | `8314910661:AAGftziNkhHlqzvgE5w_RZnJvv4sn9uaPFw` |
| NVIDIA_API_KEY | `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` |
| GOOGLE_API_KEY | `AIzaSyD5pK1x7VxVO-xGbG29iO0zBF39AWamDp4` |
| CONVEX_URL | `https://woozy-chihuahua-345.convex.cloud` |

**Important:**
- No quotes around values
- No extra spaces
- Exact case-sensitive names

## If Bot Still Not Working

1. **Check Railway Service Status**
   - Should show "Active" (green)
   - If "Crashed" (red), check logs for error

2. **Verify Root Directory**
   - Settings → Root Directory → Should be `bot`
   - If not set, bot won't find files

3. **Check Build Logs**
   - Should show "Successfully installed" for all packages
   - If build fails, check requirements.txt

4. **Share Railway Logs**
   - Copy the full error message from Railway logs
   - Share with developer for debugging

## Quick Fix: Restart Service

Sometimes Railway needs a fresh restart:

1. Railway Dashboard → Your Service
2. Settings → Restart Service
3. Wait for deployment to complete
4. Test bot again

---

**Need Help?** Share the Railway deployment logs showing the specific error message.
