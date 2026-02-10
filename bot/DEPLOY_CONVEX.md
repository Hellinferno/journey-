# Deploy Convex Functions

## Issue

The dashboard is trying to call `invoices:get` but it hasn't been deployed to Convex yet.

## Solution

You need to deploy the updated Convex functions. Here's how:

### Option 1: Using Convex Dashboard (Recommended)

1. **Go to Convex Dashboard:** https://dashboard.convex.dev/
2. **Login** to your account
3. **Select your project:** "diligent-tiger-109"
4. **Go to Functions tab**
5. **Click "Deploy"** or it should auto-deploy

### Option 2: Using CLI (If configured)

```bash
cd micro-cfo
npx convex deploy
```

### Option 3: Manual Deployment

If the above don't work, you can manually add the function in the Convex dashboard:

1. Go to https://dashboard.convex.dev/
2. Select your project
3. Go to "Functions"
4. Find `invoices.ts`
5. Add this code:

```typescript
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const get = query({
    args: {},
    handler: async (ctx) => {
        return await ctx.db.query("invoices").order("desc").collect();
    },
});

export const add = mutation({
    args: {
        telegram_id: v.string(),
        vendor: v.string(),
        amount: v.number(),
        gstin: v.optional(v.string()),
        date: v.optional(v.string()),
        status: v.string(),
        category: v.optional(v.string()),
        compliance_flags: v.optional(v.array(v.string())),
    },
    handler: async (ctx, args) => {
        await ctx.db.insert("invoices", {
            ...args,
            timestamp: new Date().toISOString(),
        });
    },
});
```

6. Click "Save" or "Deploy"

## What Changed

We added a new `get` query function that:
- Retrieves all invoices from the database
- Orders them by most recent first (desc)
- Returns them to the dashboard

## After Deployment

Once deployed:
1. **Refresh the dashboard:** http://localhost:3000
2. **The error should disappear**
3. **You'll see your invoice data**
4. **The Telegram bot will work again**

## Verify Deployment

Check if the function is deployed:
1. Go to Convex Dashboard
2. Functions tab
3. Look for `invoices:get` in the list
4. It should show as "deployed"

## Troubleshooting

**If dashboard still shows error:**
- Clear browser cache
- Hard refresh (Ctrl + Shift + R)
- Check Convex dashboard for deployment status
- Verify CONVEX_URL in .env.local matches your project

**If bot doesn't work:**
- Restart the bot: `python bot.py`
- Check bot logs for errors
- Verify Convex connection in bot logs

## Quick Fix

The fastest way is to:
1. Open https://dashboard.convex.dev/
2. Login
3. Your project should auto-deploy when you open it
4. Refresh your dashboard

---

**Note:** The Convex deployment should happen automatically when you have `npx convex dev` running, but since we're not running it, you need to deploy manually.
