# Deploy Bot to Railway

## 🚀 Quick Deploy

### Option 1: Railway CLI (Recommended)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize Project:**
   ```bash
   cd micro-cfo
   railway init
   ```

4. **Link to Project:**
   - Create new project: **micro-cfo-bot**
   - Select region: **Asia Pacific (Mumbai)**

5. **Add Environment Variables:**
   ```bash
   railway variables set TELEGRAM_TOKEN="8314910661:AAGftziNkhHlqzvgE5w_RZnJvv4sn9uaPFw"
   railway variables set CONVEX_URL="https://woozy-chihuahua-345.convex.cloud"
   railway variables set GOOGLE_API_KEY="AIzaSyD5pK1x7VxVO-xGbG29iO0zBF39AWamDp4"
   ```

6. **Deploy:**
   ```bash
   railway up
   ```

### Option 2: Railway Dashboard (Easy)

1. **Go to:** https://railway.app/new

2. **Deploy from GitHub:**
   - Click "Deploy from GitHub repo"
   - Connect GitHub account
   - Select your repository
   - Select `micro-cfo` directory

3. **Configure Service:**
   - **Name:** micro-cfo-bot
   - **Region:** Asia Pacific (Mumbai)
   - **Start Command:** `python bot.py`
   - **Build Command:** `pip install -r requirements.txt`

4. **Add Environment Variables:**

   Go to Variables tab and add:

   | Variable | Value |
   |----------|-------|
   | `TELEGRAM_TOKEN` | `8314910661:AAGftziNkhHlqzvgE5w_RZnJvv4sn9uaPFw` |
   | `CONVEX_URL` | `https://woozy-chihuahua-345.convex.cloud` |
   | `CONVEX_SITE_URL` | `https://woozy-chihuahua-345.convex.site` |
   | `GOOGLE_API_KEY` | `AIzaSyD5pK1x7VxVO-xGbG29iO0zBF39AWamDp4` |

5. **Deploy:**
   - Click "Deploy"
   - Wait for build to complete
   - Bot will start automatically

### Option 3: One-Click Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

1. Click the button above
2. Connect GitHub
3. Set environment variables
4. Deploy!

## 🔧 Configuration

### Environment Variables

**Required:**
- `TELEGRAM_TOKEN` - Your Telegram bot token
- `CONVEX_URL` - Convex deployment URL
- `GOOGLE_API_KEY` - Google Gemini API key

**Optional:**
- `CONVEX_SITE_URL` - Convex site URL
- `OPENAI_API_KEY` - OpenAI API key (if using)
- `GROQ_API_KEY` - Groq API key (if using)

### Build Configuration

Railway auto-detects Python and uses:
- **Builder:** Nixpacks
- **Python Version:** 3.11 (from `runtime.txt`)
- **Install:** `pip install -r requirements.txt`
- **Start:** `python bot.py` (from `Procfile`)

### Service Type

- **Type:** Worker (not web service)
- **No public URL needed**
- **Runs continuously**
- **Auto-restarts on failure**

## ✅ Post-Deployment

### 1. Verify Deployment

Check Railway Dashboard → Deployments:
- Build status: ✅ Success
- Deploy status: ✅ Running
- Logs show: "Starting Micro-CFO Bot..."

### 2. Check Logs

```bash
railway logs
```

Or in Dashboard → Logs tab

Look for:
```
INFO - Starting Micro-CFO Bot...
INFO - Application started
```

### 3. Test the Bot

1. Open Telegram
2. Send `/start` to your bot
3. Send an invoice photo
4. Check if bot responds
5. Verify data appears in dashboard

## 🔄 Continuous Deployment

### Automatic Deployments

Railway automatically deploys when you:
- Push to `main` branch
- Merge Pull Request
- Manual trigger in dashboard

### Manual Deployment

```bash
cd micro-cfo
railway up
```

Or in Dashboard → Deployments → "Deploy"

## 📊 Monitoring

### Logs

View real-time logs:
```bash
railway logs --follow
```

Or in Dashboard → Logs tab

### Metrics

Dashboard → Metrics shows:
- CPU usage
- Memory usage
- Network traffic
- Restart count

### Alerts

Set up in Dashboard → Settings → Notifications:
- Deployment failures
- Service crashes
- Resource limits

## 🐛 Troubleshooting

### Bot Not Starting

**Check:**
1. Environment variables set correctly
2. `requirements.txt` has all dependencies
3. Python version is 3.11
4. Logs for error messages

**Fix:**
```bash
# View logs
railway logs

# Restart service
railway restart
```

### Import Errors

**Problem:** Missing dependencies

**Fix:**
```bash
# Update requirements.txt
pip freeze > requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update dependencies"
git push

# Railway auto-deploys
```

### Convex Connection Error

**Check:**
- `CONVEX_URL` environment variable
- Convex deployment is active
- Network connectivity

**Fix:**
- Verify URL in Railway variables
- Test Convex from local machine
- Check Convex dashboard for issues

### Memory Issues

**Problem:** Bot crashes due to memory

**Fix:**
1. Upgrade Railway plan
2. Optimize code
3. Reduce concurrent operations

## 💰 Pricing

### Free Tier (Hobby Plan):
- $5 credit/month
- Enough for small bots
- 512MB RAM
- 1GB disk
- Shared CPU

### Pro Plan ($20/month):
- $20 credit included
- More resources
- Priority support
- Team features

### Usage Estimate:
- Bot typically uses: ~$3-5/month
- Depends on:
  - Number of users
  - Invoice processing frequency
  - API calls

## 🔒 Security

### Environment Variables

- Stored encrypted
- Never logged
- Accessible only to service

### Secrets Management

```bash
# Add secret
railway variables set SECRET_KEY="value"

# Remove secret
railway variables delete SECRET_KEY
```

### Network Security

- Private networking between services
- No public endpoint needed
- Secure Telegram webhook

## 🎯 Optimization

### Reduce Costs

1. **Use Cron Jobs:** If bot doesn't need 24/7
2. **Optimize Memory:** Remove unused imports
3. **Cache Data:** Reduce API calls
4. **Batch Operations:** Process multiple invoices together

### Improve Performance

1. **Use Async:** For concurrent operations
2. **Connection Pooling:** For database
3. **Caching:** For frequent queries
4. **Monitoring:** Track bottlenecks

## 🔄 Updates

### Deploy New Version

```bash
git add .
git commit -m "Update bot"
git push origin main
```

Railway auto-deploys in ~2 minutes.

### Rollback

In Dashboard → Deployments:
1. Find previous deployment
2. Click "Redeploy"
3. Confirm

## 📚 Resources

- [Railway Docs](https://docs.railway.app/)
- [Python on Railway](https://docs.railway.app/guides/python)
- [Environment Variables](https://docs.railway.app/develop/variables)

## 🎯 Next Steps

After deploying:

1. **Monitor Logs:** Check for errors
2. **Test Thoroughly:** Send various invoices
3. **Set Up Alerts:** Get notified of issues
4. **Optimize:** Based on usage patterns

---

**Your bot will run 24/7 on Railway!** 🚀

## Quick Commands

```bash
# View logs
railway logs

# Restart service
railway restart

# Open dashboard
railway open

# Check status
railway status

# Add variable
railway variables set KEY="value"

# Deploy
railway up
```
