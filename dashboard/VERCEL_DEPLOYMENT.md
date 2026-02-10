# Deploy Dashboard to Vercel

## 🚀 Quick Deploy

### Option 1: Vercel CLI (Recommended)

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy from dashboard directory:**
   ```bash
   cd dashboard
   vercel
   ```

4. **Follow prompts:**
   - Set up and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N**
   - Project name? **micro-cfo-dashboard**
   - Directory? **./dashboard**
   - Override settings? **N**

5. **Set Environment Variable:**
   ```bash
   vercel env add NEXT_PUBLIC_CONVEX_URL
   ```
   Enter: `https://woozy-chihuahua-345.convex.cloud`

6. **Deploy to Production:**
   ```bash
   vercel --prod
   ```

### Option 2: Vercel Dashboard (Easy)

1. **Go to:** https://vercel.com/new

2. **Import Git Repository:**
   - Click "Import Project"
   - Connect your GitHub account
   - Select your repository
   - Select `dashboard` as root directory

3. **Configure Project:**
   - **Framework Preset:** Next.js
   - **Root Directory:** `dashboard`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`
   - **Install Command:** `npm install`

4. **Add Environment Variables:**
   - Key: `NEXT_PUBLIC_CONVEX_URL`
   - Value: `https://woozy-chihuahua-345.convex.cloud`

5. **Click "Deploy"**

### Option 3: GitHub Integration (Automatic)

1. **Push to GitHub:**
   ```bash
   git push origin main
   ```

2. **Connect Vercel:**
   - Go to https://vercel.com/dashboard
   - Click "Add New Project"
   - Import from GitHub
   - Select repository
   - Configure as above

3. **Auto-Deploy:**
   - Every push to `main` auto-deploys
   - Preview deployments for PRs

## 🔧 Configuration

### Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

| Variable | Value | Environment |
|----------|-------|-------------|
| `NEXT_PUBLIC_CONVEX_URL` | `https://woozy-chihuahua-345.convex.cloud` | Production, Preview, Development |

### Build Settings

- **Framework:** Next.js 16
- **Node Version:** 18.x or higher
- **Build Command:** `npm run build`
- **Output Directory:** `.next`
- **Install Command:** `npm install`

### Regions

Recommended: **Mumbai (bom1)** for India-based users

Change in `vercel.json`:
```json
"regions": ["bom1"]
```

Other options:
- `sin1` - Singapore
- `hnd1` - Tokyo
- `iad1` - Washington DC

## ✅ Post-Deployment

### 1. Verify Deployment

After deployment, Vercel will give you a URL like:
```
https://micro-cfo-dashboard.vercel.app
```

### 2. Test the Dashboard

- Open the URL
- Check if it loads without errors
- Verify Convex connection
- Send test invoice via bot
- Confirm real-time updates work

### 3. Custom Domain (Optional)

1. Go to Vercel Dashboard → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. SSL certificate auto-provisioned

## 🔄 Continuous Deployment

### Automatic Deployments

Vercel automatically deploys when you:
- Push to `main` branch → Production
- Push to other branches → Preview
- Open Pull Request → Preview

### Manual Deployment

```bash
cd dashboard
vercel --prod
```

## 🐛 Troubleshooting

### Build Fails

**Check:**
- Node version (18.x+)
- All dependencies in `package.json`
- Environment variables set correctly

**Fix:**
```bash
# Locally test build
npm run build

# Check for errors
npm run lint
```

### Convex Connection Error

**Check:**
- `NEXT_PUBLIC_CONVEX_URL` is set
- URL is correct (woozy-chihuahua-345)
- Convex deployment is active

**Fix:**
- Verify in Vercel → Settings → Environment Variables
- Redeploy after fixing

### Slow Loading

**Optimize:**
- Enable Edge Functions
- Use Image Optimization
- Enable Caching
- Select nearest region

## 📊 Monitoring

### Vercel Analytics

Enable in Dashboard → Analytics:
- Page views
- Performance metrics
- User demographics
- Real-time visitors

### Logs

View in Dashboard → Deployments → [Your Deployment] → Logs:
- Build logs
- Function logs
- Error tracking

## 🔒 Security

### Environment Variables

- Never commit `.env.local`
- Use Vercel's encrypted storage
- Rotate keys regularly

### CORS

Convex handles CORS automatically, no configuration needed.

## 💰 Pricing

### Free Tier Includes:
- Unlimited deployments
- 100GB bandwidth/month
- Automatic HTTPS
- Preview deployments
- Analytics

### Pro Tier ($20/month):
- 1TB bandwidth
- Advanced analytics
- Team collaboration
- Priority support

## 🎯 Next Steps

After deploying:

1. **Update Bot:** No changes needed (bot uses Convex directly)
2. **Share URL:** Give dashboard URL to users
3. **Monitor:** Check Vercel analytics
4. **Optimize:** Review performance metrics

## 📚 Resources

- [Vercel Docs](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Convex + Vercel](https://docs.convex.dev/production/hosting/vercel)

---

**Your dashboard will be live at:** `https://micro-cfo-dashboard.vercel.app` 🚀
