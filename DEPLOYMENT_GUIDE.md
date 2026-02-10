# Micro-CFO Deployment Guide

Complete guide to deploy your Micro-CFO system to production.

## 🏗️ Architecture

```
┌─────────────────┐
│   Telegram Bot  │ ← Users send invoices
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Railway (Bot)  │ ← Python bot processes invoices
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Convex (DB)    │ ← Stores invoice data
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Vercel (Dashboard) │ ← Users view analytics
└─────────────────┘
```

## 📦 Components

1. **Frontend (Dashboard)** → Vercel
   - Next.js 16 application
   - Real-time data visualization
   - Responsive design

2. **Backend (Bot)** → Railway
   - Python Telegram bot
   - Invoice processing
   - Compliance checking

3. **Database** → Convex
   - Real-time sync
   - Vector search
   - Serverless

## 🚀 Deployment Steps

### Step 1: Deploy Convex (Already Done ✅)

Your Convex is already deployed:
- **URL:** `https://woozy-chihuahua-345.convex.cloud`
- **Dashboard:** https://dashboard.convex.dev/d/woozy-chihuahua-345
- **Status:** ✅ Live

### Step 2: Deploy Dashboard to Vercel

**Quick Deploy:**
```bash
cd dashboard
npm install -g vercel
vercel login
vercel
```

**Set Environment Variable:**
```bash
vercel env add NEXT_PUBLIC_CONVEX_URL
# Enter: https://woozy-chihuahua-345.convex.cloud
```

**Deploy to Production:**
```bash
vercel --prod
```

**Result:** `https://micro-cfo-dashboard.vercel.app`

📚 **Detailed Guide:** `dashboard/VERCEL_DEPLOYMENT.md`

### Step 3: Deploy Bot to Railway

**Quick Deploy:**
```bash
cd micro-cfo
npm install -g @railway/cli
railway login
railway init
```

**Set Environment Variables:**
```bash
railway variables set TELEGRAM_TOKEN="YOUR_TOKEN"
railway variables set CONVEX_URL="https://woozy-chihuahua-345.convex.cloud"
railway variables set GOOGLE_API_KEY="YOUR_KEY"
```

**Deploy:**
```bash
railway up
```

**Result:** Bot runs 24/7 on Railway

📚 **Detailed Guide:** `micro-cfo/RAILWAY_DEPLOYMENT.md`

## 🔑 Environment Variables

### Dashboard (Vercel)

| Variable | Value | Where to Set |
|----------|-------|--------------|
| `NEXT_PUBLIC_CONVEX_URL` | `https://woozy-chihuahua-345.convex.cloud` | Vercel Dashboard → Settings → Environment Variables |

### Bot (Railway)

| Variable | Value | Where to Set |
|----------|-------|--------------|
| `TELEGRAM_TOKEN` | Your bot token | Railway Dashboard → Variables |
| `CONVEX_URL` | `https://woozy-chihuahua-345.convex.cloud` | Railway Dashboard → Variables |
| `GOOGLE_API_KEY` | Your Gemini API key | Railway Dashboard → Variables |

## ✅ Verification Checklist

### After Deployment

- [ ] Dashboard loads at Vercel URL
- [ ] No console errors in browser
- [ ] Convex connection successful
- [ ] Bot running on Railway
- [ ] Bot logs show "Application started"
- [ ] Send test invoice to bot
- [ ] Invoice appears in dashboard
- [ ] Real-time updates work
- [ ] Charts display correctly
- [ ] Compliance checks work

## 🧪 Testing

### 1. Test Bot

```
1. Open Telegram
2. Send /start to bot
3. Send invoice photo
4. Verify bot responds
5. Check compliance report
```

### 2. Test Dashboard

```
1. Open dashboard URL
2. Check if invoice appears
3. Verify KPI cards update
4. Check charts render
5. Test real-time sync
```

### 3. Test Integration

```
1. Send invoice via bot
2. Watch dashboard update live
3. Verify data accuracy
4. Check compliance flags
5. Test multiple invoices
```

## 🔄 Continuous Deployment

### Automatic Deployments

**Vercel (Dashboard):**
- Push to `main` → Auto-deploy to production
- Push to branch → Preview deployment
- Pull Request → Preview deployment

**Railway (Bot):**
- Push to `main` → Auto-deploy
- Manual trigger in dashboard
- CLI: `railway up`

### Deployment Workflow

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Vercel auto-deploys dashboard
# Railway auto-deploys bot
# Both live in ~2 minutes
```

## 📊 Monitoring

### Dashboard (Vercel)

- **Analytics:** Vercel Dashboard → Analytics
- **Logs:** Vercel Dashboard → Deployments → Logs
- **Performance:** Real-time metrics
- **Errors:** Automatic error tracking

### Bot (Railway)

- **Logs:** `railway logs --follow`
- **Metrics:** Railway Dashboard → Metrics
- **Alerts:** Railway Dashboard → Notifications
- **Status:** Railway Dashboard → Overview

### Convex

- **Dashboard:** https://dashboard.convex.dev/
- **Functions:** Monitor query performance
- **Database:** View tables and data
- **Logs:** Function execution logs

## 💰 Cost Estimate

### Monthly Costs

| Service | Plan | Cost | Usage |
|---------|------|------|-------|
| Vercel | Hobby | $0 | Free tier sufficient |
| Railway | Hobby | $5 | $5 credit/month |
| Convex | Free | $0 | Free tier (with limits) |
| **Total** | | **~$5/month** | For moderate usage |

### Scaling Costs

**If you exceed free tiers:**
- Vercel Pro: $20/month
- Railway Pro: $20/month
- Convex Pro: $25/month

**Total for Pro:** ~$65/month

## 🔒 Security

### Best Practices

1. **Environment Variables:**
   - Never commit `.env` files
   - Use platform secret management
   - Rotate keys regularly

2. **API Keys:**
   - Restrict by IP if possible
   - Monitor usage
   - Set spending limits

3. **Access Control:**
   - Use strong passwords
   - Enable 2FA
   - Limit team access

4. **Monitoring:**
   - Set up alerts
   - Review logs regularly
   - Track unusual activity

## 🐛 Troubleshooting

### Dashboard Not Loading

**Check:**
- Vercel deployment status
- Browser console for errors
- Environment variables set
- Convex URL correct

**Fix:**
```bash
# Redeploy
cd dashboard
vercel --prod
```

### Bot Not Responding

**Check:**
- Railway service running
- Logs for errors
- Environment variables
- Telegram token valid

**Fix:**
```bash
# View logs
railway logs

# Restart
railway restart
```

### Data Not Syncing

**Check:**
- Convex deployment active
- Both services use same Convex URL
- Network connectivity
- Convex dashboard for errors

**Fix:**
- Verify URLs match
- Check Convex dashboard
- Redeploy if needed

## 🎯 Post-Deployment

### 1. Custom Domains (Optional)

**Dashboard:**
- Vercel Dashboard → Domains
- Add custom domain
- Update DNS records

**Bot:**
- No domain needed (Telegram handles routing)

### 2. SSL Certificates

- Vercel: Auto-provisioned ✅
- Railway: Not needed for bot ✅
- Convex: Included ✅

### 3. Monitoring Setup

**Set up alerts for:**
- Deployment failures
- Service crashes
- High error rates
- Resource limits
- Cost thresholds

### 4. Backup Strategy

**Convex Data:**
- Export data regularly
- Use Convex backup features
- Keep local copies

**Code:**
- Git repository (already done ✅)
- Multiple remotes recommended
- Tag releases

## 📚 Resources

### Documentation

- [Vercel Docs](https://vercel.com/docs)
- [Railway Docs](https://docs.railway.app/)
- [Convex Docs](https://docs.convex.dev/)
- [Next.js Docs](https://nextjs.org/docs)
- [Telegram Bot API](https://core.telegram.org/bots/api)

### Support

- Vercel: support@vercel.com
- Railway: Discord community
- Convex: support@convex.dev

## 🎊 Success!

Once deployed, you'll have:

✅ **Dashboard:** Live at `https://micro-cfo-dashboard.vercel.app`
✅ **Bot:** Running 24/7 on Railway
✅ **Database:** Real-time sync via Convex
✅ **Monitoring:** Full observability
✅ **Auto-Deploy:** Push to deploy
✅ **Scalable:** Ready for growth

## 🚀 Quick Start Commands

```bash
# Deploy Dashboard
cd dashboard
vercel --prod

# Deploy Bot
cd micro-cfo
railway up

# View Logs
railway logs --follow

# Check Status
railway status
vercel ls
```

---

**Your Micro-CFO system is now production-ready!** 🎉

For detailed instructions, see:
- `dashboard/VERCEL_DEPLOYMENT.md`
- `micro-cfo/RAILWAY_DEPLOYMENT.md`
