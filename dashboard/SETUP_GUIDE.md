# Micro-CFO Dashboard Setup Guide

## 🎯 Overview

This guide will help you set up and run the Micro-CFO dashboard - a stunning, real-time financial compliance monitoring interface.

## ✅ Prerequisites

Before starting, ensure you have:

- [x] Node.js 18+ installed
- [x] npm or yarn package manager
- [x] Micro-CFO bot running (for data)
- [x] Convex account and deployment URL

## 📦 Installation Steps

### Step 1: Navigate to Dashboard Directory

```bash
cd dashboard
```

### Step 2: Install Dependencies

```bash
npm install
```

This will install:
- Next.js 16 (React framework)
- Tailwind CSS v4 (Styling)
- Recharts (Data visualization)
- Convex (Real-time database)
- Lucide React (Icons)
- UI component dependencies

### Step 3: Configure Environment

Create a `.env.local` file in the dashboard directory:

```env
NEXT_PUBLIC_CONVEX_URL=https://your-project.convex.cloud
```

**Where to find your Convex URL:**
1. Open `micro-cfo/.env`
2. Copy the `CONVEX_URL` value
3. Paste it into dashboard's `.env.local`

Example:
```env
NEXT_PUBLIC_CONVEX_URL=https://diligent-tiger-109.convex.cloud
```

### Step 4: Start Development Server

**Option A: Using npm**
```bash
npm run dev
```

**Option B: Using the batch file (Windows)**
```bash
start_dashboard.bat
```

**Option C: Using yarn**
```bash
yarn dev
```

### Step 5: Open in Browser

Navigate to: [http://localhost:3000](http://localhost:3000)

You should see the Micro-CFO dashboard with:
- Dark terminal theme
- Animated grid background
- Gradient orbs
- KPI cards
- Live audit stream
- Interactive charts

## 🎨 What You'll See

### Dashboard Features

1. **Header Section**
   - Gradient "MICRO-CFO" title
   - System status indicator (green dot)
   - Live monitoring badge
   - Record count

2. **KPI Cards (4 metrics)**
   - Total Expenditure (₹)
   - ITC Eligible (₹)
   - Blocked Credits (count)
   - Compliance Rate (%)

3. **Live Audit Stream**
   - Real-time invoice table
   - Vendor names and categories
   - Color-coded status badges
   - Amount in INR

4. **Charts**
   - Pie chart: Spending by category
   - Bar chart: Compliance status distribution

5. **Footer**
   - Technology credits
   - Last updated timestamp

## 🔄 Testing Real-Time Updates

### Step 1: Ensure Bot is Running

In the `micro-cfo` directory:
```bash
python bot.py
```

### Step 2: Send Invoice to Bot

1. Open Telegram
2. Find your Micro-CFO bot
3. Send an invoice photo

### Step 3: Watch Dashboard Update

The dashboard will automatically:
- Add new row to audit stream
- Update KPI numbers
- Refresh charts
- Show animated entry

## 🎨 Design Highlights

### Unique Aesthetic Features

1. **Typography**
   - Headings: Syne (bold, distinctive)
   - Body: JetBrains Mono (monospace, terminal-like)
   - Numbers: Monospace for financial data

2. **Color Palette**
   - Primary: Purple (`#8B5CF6`)
   - Accent: Pink (`#EC4899`)
   - Profit: Green (`#22C55E`)
   - Loss: Red (`#EF4444`)
   - Warning: Yellow (`#FBBF24`)

3. **Animations**
   - Staggered page load (0.1s delays)
   - Glow pulse on status indicators
   - Slide-up card reveals
   - Fade-in table rows
   - Hover neon borders

4. **Backgrounds**
   - Animated grid pattern
   - Gradient orbs (purple & pink)
   - Glass morphism cards
   - Backdrop blur effects

## 🛠️ Troubleshooting

### Issue: Dashboard shows no data

**Solution:**
1. Check if Convex URL is correct in `.env.local`
2. Verify bot has processed at least one invoice
3. Check browser console for errors
4. Ensure Convex deployment is active

### Issue: Styles not loading

**Solution:**
1. Clear Next.js cache: `rm -rf .next`
2. Reinstall dependencies: `npm install`
3. Restart dev server: `npm run dev`

### Issue: Real-time updates not working

**Solution:**
1. Check Convex connection in browser console
2. Verify `NEXT_PUBLIC_` prefix in env variable
3. Restart development server
4. Check network tab for WebSocket connection

### Issue: Charts not displaying

**Solution:**
1. Ensure Recharts is installed: `npm list recharts`
2. Check if invoice data has categories
3. Verify data format in browser console
4. Clear browser cache

### Issue: Port 3000 already in use

**Solution:**
```bash
# Kill process on port 3000
npx kill-port 3000

# Or use different port
npm run dev -- -p 3001
```

## 📊 Understanding the Data

### Invoice Status Types

1. **Compliant** (Green)
   - All validations passed
   - ITC eligible
   - Ready for GST filing

2. **Review Needed** (Yellow)
   - Minor issues detected
   - Requires manual review
   - May have warnings

3. **Blocked** (Red)
   - Section 17(5) violation
   - ITC not eligible
   - Compliance issue

### KPI Calculations

**Total Expenditure:**
```
Sum of all invoice amounts
```

**ITC Eligible:**
```
Sum of (compliant invoice amount × 0.18)
Assumes 18% GST rate
```

**Blocked Credits:**
```
Count of invoices with status = "blocked"
```

**Compliance Rate:**
```
(Compliant invoices / Total invoices) × 100
```

## 🚀 Production Deployment

### Deploy to Vercel

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel deploy --prod
   ```

4. **Set Environment Variables**
   - Go to Vercel dashboard
   - Project Settings → Environment Variables
   - Add: `NEXT_PUBLIC_CONVEX_URL`

### Deploy to Netlify

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Build Project**
   ```bash
   npm run build
   ```

3. **Deploy**
   ```bash
   netlify deploy --prod
   ```

4. **Set Environment Variables**
   - Go to Netlify dashboard
   - Site Settings → Environment Variables
   - Add: `NEXT_PUBLIC_CONVEX_URL`

## 📝 Customization Guide

### Change Colors

Edit `src/app/globals.css`:

```css
:root {
  --primary: 139 92 246;    /* Your primary color */
  --accent: 236 72 153;     /* Your accent color */
}
```

### Adjust Animations

Modify animation speeds:

```css
@keyframes glow-pulse {
  /* Change duration here */
  animation: glow-pulse 3s ease-in-out infinite;
}
```

### Add New KPI Card

In `src/app/page.tsx`:

```tsx
<Card className="glass border-[rgb(var(--border))]">
  <CardHeader>
    <CardTitle>Your Metric</CardTitle>
    <YourIcon className="h-5 w-5" />
  </CardHeader>
  <CardContent>
    <div className="text-3xl font-bold">
      {yourCalculation}
    </div>
  </CardContent>
</Card>
```

### Modify Chart Colors

Update the `COLORS` array:

```tsx
const COLORS = [
  'rgb(139, 92, 246)',  // Purple
  'rgb(236, 72, 153)',  // Pink
  // Add more colors...
];
```

## 🎯 Next Steps

1. **Customize the design** to match your brand
2. **Add more charts** for deeper insights
3. **Create filters** for date ranges
4. **Add export functionality** for reports
5. **Implement user authentication** for multi-user
6. **Add notifications** for critical events
7. **Create mobile responsive** views
8. **Add dark/light theme** toggle

## 📚 Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS v4](https://tailwindcss.com/docs)
- [Recharts Documentation](https://recharts.org/)
- [Convex Documentation](https://docs.convex.dev/)
- [Lucide Icons](https://lucide.dev/)

## 🆘 Getting Help

If you encounter issues:

1. Check the browser console for errors
2. Review the terminal output
3. Verify environment variables
4. Check Convex dashboard for data
5. Ensure bot is running and processing invoices

## ✨ Enjoy Your Dashboard!

You now have a stunning, real-time financial compliance dashboard that:
- Monitors invoices automatically
- Provides instant compliance insights
- Visualizes spending patterns
- Tracks GST compliance
- Looks absolutely gorgeous!

---

**Built with ❤️ for financial compliance automation**
