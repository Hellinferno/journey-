# ✅ Vercel Deployment Checklist

## Before You Start

Make sure you have:
- [ ] Vercel account created
- [ ] GitHub repository connected to Vercel
- [ ] Convex deployment URL: `https://woozy-chihuahua-345.convex.cloud`

## Step 1: Configure Vercel Project Settings

### Go to: Vercel Dashboard → Your Project → Settings

#### General Settings

1. **Root Directory**
   - Set to: `dashboard`
   - ⚠️ This is CRITICAL - Vercel must build from the dashboard folder

2. **Framework Preset**
   - Should auto-detect: Next.js
   - If not, select: Next.js

3. **Node.js Version**
   - Should be: 18.x or 20.x
   - Check in: Settings → General → Node.js Version

#### Build & Development Settings

Leave these as default (auto-detect):
- Build Command: `npm run build`
- Output Directory: `.next`
- Install Command: `npm install`
- Development Command: `npm run dev`

## Step 2: Set Environment Variables

### Go to: Settings → Environment Variables

Add this variable:

| Key | Value | Environments |
|-----|-------|--------------|
| `NEXT_PUBLIC_CONVEX_URL` | `https://woozy-chihuahua-345.convex.cloud` | ✅ Production<br>✅ Preview<br>✅ Development |

**Important:** Check ALL three environment checkboxes!

## Step 3: Deploy

### Option A: Automatic Deploy (Recommended)

1. Push to GitHub:
   ```bash
   git add -A
   git commit -m "fix: Update Vercel configuration"
   git push origin main
   ```

2. Vercel will automatically deploy
3. Wait for build to complete (1-2 minutes)

### Option B: Manual Deploy

1. Go to: Deployments tab
2. Click: "Redeploy" on latest deployment
3. Wait for build to complete

## Step 4: Verify Deployment

### Check Build Status

1. Go to: Deployments tab
2. Look for: ✅ Green checkmark (Success)
3. If ❌ Red X: Click to view build logs

### Test the Dashboard

1. Click on deployment URL (e.g., `https://your-project.vercel.app`)
2. Dashboard should load with:
   - "MICRO-CFO" header
   - KPI cards (may show zeros if no data)
   - Charts
   - Invoice table
   - "SYSTEM ONLINE" indicator

### Check Browser Console

1. Open dashboard URL
2. Press F12 (DevTools)
3. Go to Console tab
4. Should see NO red errors
5. If errors appear, check:
   - Is `NEXT_PUBLIC_CONVEX_URL` set?
   - Is Convex deployment active?

## Step 5: Add Test Data

If dashboard shows all zeros:

1. Run bot locally:
   ```bash
   cd micro-cfo
   python bot.py
   ```

2. Send test invoice via Telegram

3. Refresh dashboard - data should appear

## Common Issues & Quick Fixes

### Issue: 404 Not Found

**Fix:**
- Check Root Directory is set to `dashboard`
- Redeploy after changing

### Issue: Blank White Page

**Fix:**
- Check browser console for errors
- Verify `NEXT_PUBLIC_CONVEX_URL` is set in Vercel
- Ensure all three environments are checked

### Issue: Build Failed

**Fix:**
1. View build logs in Vercel
2. Test build locally:
   ```bash
   cd dashboard
   npm install
   npm run build
   ```
3. Fix any errors shown
4. Push changes and redeploy

### Issue: "Cannot find module" Error

**Fix:**
- Ensure all dependencies are in `package.json`
- Try: Settings → General → Clear Build Cache
- Redeploy

### Issue: Environment Variable Not Working

**Fix:**
1. Go to Settings → Environment Variables
2. Delete existing `NEXT_PUBLIC_CONVEX_URL`
3. Add it again with ALL environments checked
4. Redeploy (important - env vars need redeploy)

## Verification Commands

### Check if dashboard builds locally:
```bash
cd dashboard
npm install
npm run build
npm start
```

Open: http://localhost:3000

### Check Vercel deployment:
```bash
vercel --prod
```

### View Vercel logs:
```bash
vercel logs [your-deployment-url]
```

## Success Criteria

Your deployment is successful when:

- ✅ Build completes without errors
- ✅ Dashboard URL loads
- ✅ No errors in browser console
- ✅ KPI cards visible (even if showing zeros)
- ✅ Charts render
- ✅ Table structure visible
- ✅ "SYSTEM ONLINE" shows green dot

## Next Steps After Successful Deployment

1. **Add Custom Domain** (Optional)
   - Settings → Domains
   - Add your domain
   - Update DNS records

2. **Enable Analytics**
   - Analytics tab
   - View traffic and performance

3. **Set Up Monitoring**
   - Check deployment logs regularly
   - Monitor for errors

4. **Update Bot** (if needed)
   - Bot already uses Convex directly
   - No changes needed to bot code

## Need Help?

### Check These First:
1. ✅ Root Directory = `dashboard`
2. ✅ Environment Variable set with ALL environments
3. ✅ Build logs (no errors)
4. ✅ Browser console (no errors)

### Still Not Working?

Provide this info:
- Vercel deployment URL
- Screenshot of Settings → General (Root Directory)
- Screenshot of Settings → Environment Variables
- Build logs (copy/paste)
- Browser console errors (screenshot)

---

**Most Common Fix:** Set Root Directory to `dashboard` and add environment variable with all three environments checked, then redeploy.
