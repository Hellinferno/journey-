# Vercel Dashboard Not Showing - Troubleshooting Guide

## 🔍 Common Issues & Solutions

### Issue 1: Root Directory Not Set Correctly

**Problem:** Vercel is trying to build from repository root instead of `dashboard/` folder.

**Solution:**
1. Go to Vercel Dashboard → Your Project → Settings → General
2. Find "Root Directory" setting
3. Set it to: `dashboard`
4. Click "Save"
5. Redeploy from Deployments tab

### Issue 2: Environment Variable Missing

**Problem:** `NEXT_PUBLIC_CONVEX_URL` not set in Vercel.

**Solution:**
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add new variable:
   - **Name:** `NEXT_PUBLIC_CONVEX_URL`
   - **Value:** `https://woozy-chihuahua-345.convex.cloud`
   - **Environments:** Production, Preview, Development (check all)
3. Click "Save"
4. Redeploy from Deployments tab

### Issue 3: Build Command Issues

**Problem:** Build failing or using wrong commands.

**Solution:**
1. Go to Vercel Dashboard → Your Project → Settings → General
2. Check Build & Development Settings:
   - **Framework Preset:** Next.js
   - **Build Command:** `npm run build` (or leave empty for auto-detect)
   - **Output Directory:** `.next` (or leave empty)
   - **Install Command:** `npm install` (or leave empty)
3. Click "Save"
4. Redeploy

### Issue 4: Node.js Version

**Problem:** Using incompatible Node.js version.

**Solution:**
1. Create/update `dashboard/.nvmrc` file:
   ```
   18
   ```
2. Or add to `dashboard/package.json`:
   ```json
   "engines": {
     "node": ">=18.0.0"
   }
   ```
3. Commit and push changes

### Issue 5: Blank Page / White Screen

**Problem:** Dashboard loads but shows nothing.

**Possible Causes:**
- Convex URL not set
- No data in database
- JavaScript errors

**Solution:**

1. **Check Browser Console:**
   - Open browser DevTools (F12)
   - Look for errors in Console tab
   - Common errors:
     - "NEXT_PUBLIC_CONVEX_URL is undefined"
     - "Failed to fetch"
     - CORS errors

2. **Verify Convex Connection:**
   - Check if `NEXT_PUBLIC_CONVEX_URL` is set in Vercel
   - Verify URL is correct: `https://woozy-chihuahua-345.convex.cloud`
   - Ensure Convex deployment is active

3. **Check Database:**
   - Run bot locally to add test data
   - Verify data exists in Convex dashboard
   - Check if invoices table has records

### Issue 6: 404 Not Found

**Problem:** Vercel shows "404: This page could not be found"

**Solution:**
1. Check if build succeeded in Vercel Deployments tab
2. Verify `dashboard/src/app/page.tsx` exists
3. Check for build errors in deployment logs
4. Ensure Next.js App Router is being used (not Pages Router)

### Issue 7: Build Errors

**Problem:** Deployment fails during build.

**Solution:**

1. **Check Build Logs:**
   - Go to Vercel → Deployments → [Failed Deployment]
   - Click "View Build Logs"
   - Look for error messages

2. **Common Build Errors:**

   **TypeScript Errors:**
   ```bash
   # Test locally first
   cd dashboard
   npm run build
   ```

   **Missing Dependencies:**
   ```bash
   # Ensure all deps are in package.json
   npm install
   ```

   **Convex Schema Issues:**
   ```bash
   # Deploy Convex schema first
   cd dashboard
   npx convex deploy
   ```

## 🚀 Step-by-Step Deployment Checklist

### Pre-Deployment

- [ ] Dashboard works locally: `cd dashboard && npm run dev`
- [ ] Build succeeds locally: `cd dashboard && npm run build`
- [ ] `.env.local` has correct `NEXT_PUBLIC_CONVEX_URL`
- [ ] Convex schema deployed: `npx convex deploy`
- [ ] Test data exists in Convex database

### Vercel Configuration

- [ ] Root Directory set to: `dashboard`
- [ ] Framework Preset: Next.js
- [ ] Environment Variable added: `NEXT_PUBLIC_CONVEX_URL`
- [ ] Node.js version: 18.x or higher
- [ ] Build Command: `npm run build` (or auto)
- [ ] Output Directory: `.next` (or auto)

### Post-Deployment

- [ ] Build succeeded (green checkmark)
- [ ] No errors in build logs
- [ ] Dashboard URL loads
- [ ] No JavaScript errors in browser console
- [ ] Data displays correctly
- [ ] Real-time updates work

## 🔧 Quick Fix Commands

### Redeploy from CLI

```bash
cd dashboard
vercel --prod
```

### Force Rebuild

```bash
# In Vercel Dashboard
Deployments → [Latest] → ... → Redeploy
```

### Check Environment Variables

```bash
vercel env ls
```

### View Logs

```bash
vercel logs [deployment-url]
```

## 📊 Debugging Steps

### 1. Check Vercel Deployment Status

```
Vercel Dashboard → Deployments
```

Look for:
- ✅ Green checkmark = Success
- ❌ Red X = Failed
- 🟡 Yellow = Building

### 2. View Build Logs

Click on deployment → "View Build Logs"

Look for:
- `Error:` messages
- `Warning:` messages
- Build time (should be < 2 minutes)

### 3. Check Runtime Logs

Click on deployment → "Functions" tab

Look for:
- Runtime errors
- API call failures
- Timeout issues

### 4. Test Locally First

```bash
cd dashboard

# Install dependencies
npm install

# Build
npm run build

# Start production server
npm start
```

If it works locally but not on Vercel, it's a configuration issue.

### 5. Check Browser Console

Open deployed URL → F12 → Console tab

Look for:
- Red error messages
- Network failures (Network tab)
- Failed API calls

## 🎯 Most Likely Issues

Based on your setup, check these first:

### 1. Root Directory (MOST COMMON)

**Current structure:**
```
journey/
├── dashboard/     <-- Vercel needs to build from here
├── micro-cfo/
└── ...
```

**Vercel Setting:**
- Root Directory: `dashboard` ✅
- NOT: `.` or empty ❌

### 2. Environment Variable

**Must be set in Vercel:**
```
NEXT_PUBLIC_CONVEX_URL=https://woozy-chihuahua-345.convex.cloud
```

**Check:**
- Settings → Environment Variables
- All environments checked (Production, Preview, Development)

### 3. No Data in Database

**If dashboard loads but shows zeros:**
- Run bot locally: `cd micro-cfo && python bot.py`
- Send test invoice via Telegram
- Check Convex dashboard for data

## 📞 Get Help

### Check These Resources

1. **Vercel Build Logs:** Most errors show here
2. **Browser Console:** JavaScript errors show here
3. **Convex Dashboard:** Verify data exists
4. **Local Build:** Test with `npm run build`

### Provide This Info When Asking for Help

- Vercel deployment URL
- Build logs (copy/paste errors)
- Browser console errors (screenshot)
- Whether it works locally
- Root directory setting in Vercel

## ✅ Success Indicators

Your dashboard is working when:

- ✅ Vercel deployment shows green checkmark
- ✅ Dashboard URL loads without errors
- ✅ KPI cards show data (not all zeros)
- ✅ Charts display
- ✅ Invoice table shows records
- ✅ "SYSTEM ONLINE" indicator is green
- ✅ No errors in browser console

---

**Need immediate help?** Check Vercel deployment logs first - they usually show exactly what's wrong.
