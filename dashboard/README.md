# Micro-CFO Dashboard

A stunning, real-time financial compliance dashboard for the Micro-CFO Telegram bot.

## 🎨 Design Philosophy

This dashboard breaks away from generic AI aesthetics with:

- **Unique Typography**: Syne (headings) + JetBrains Mono (body) for a distinctive financial terminal feel
- **Dark Terminal Theme**: Inspired by professional trading terminals and IDE themes
- **Atmospheric Backgrounds**: Layered gradients and animated grid patterns create depth
- **Neon Accents**: Purple and pink gradient highlights with glow effects
- **Smooth Animations**: Staggered page load reveals and micro-interactions
- **Glass Morphism**: Translucent cards with backdrop blur for modern aesthetics

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create `.env.local` file:

```env
NEXT_PUBLIC_CONVEX_URL=https://your-project.convex.cloud
```

### 3. Start Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## 📊 Features

### Real-Time Monitoring
- Live invoice feed from Telegram bot
- Automatic updates when new invoices are processed
- Real-time compliance status tracking

### Financial KPIs
- **Total Expenditure**: Sum of all processed invoices
- **ITC Eligible**: Calculated Input Tax Credit from compliant bills
- **Blocked Credits**: Count of Section 17(5) violations
- **Compliance Rate**: Percentage of compliant invoices

### Visual Analytics
- **Expenditure Distribution**: Pie chart showing spending by category
- **Compliance Status**: Bar chart of compliant/review/blocked invoices
- **Live Audit Stream**: Real-time table of recent invoice processing

### Compliance Insights
- Color-coded status badges (Green/Yellow/Red)
- Category-wise spending breakdown
- Vendor-level transaction details
- GST compliance flags and warnings

## 🎨 Design System

### Color Palette
- **Primary**: Purple (`rgb(139, 92, 246)`) - Main brand color
- **Accent**: Pink (`rgb(236, 72, 153)`) - Highlights and CTAs
- **Profit**: Green (`rgb(34, 197, 94)`) - Compliant status
- **Loss**: Red (`rgb(239, 68, 68)`) - Blocked status
- **Warning**: Yellow (`rgb(251, 191, 36)`) - Review needed
- **Info**: Blue (`rgb(59, 130, 246)`) - Informational

### Typography
- **Headings**: Syne (Bold, 700-800 weight)
- **Body**: JetBrains Mono (Regular, 400-600 weight)
- **Monospace**: Used for numbers, codes, and technical data

### Animations
- **Page Load**: Staggered slide-up animations (0.1s delays)
- **Glow Effects**: Pulsing neon borders on interactive elements
- **Fade In**: Smooth opacity transitions for table rows
- **Grid Background**: Animated grid pattern with opacity

## 🏗️ Architecture

### Tech Stack
- **Framework**: Next.js 16 (App Router)
- **Styling**: Tailwind CSS v4
- **UI Components**: Custom components with shadcn/ui patterns
- **Charts**: Recharts
- **Database**: Convex (real-time sync)
- **Icons**: Lucide React

### Project Structure
```
dashboard/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Main dashboard
│   │   ├── layout.tsx            # Root layout
│   │   ├── globals.css           # Global styles & animations
│   │   └── ConvexClientProvider.tsx
│   ├── components/
│   │   └── ui/                   # Reusable UI components
│   └── lib/
│       └── utils.ts              # Utility functions
├── convex/                       # Convex schema (synced)
└── public/                       # Static assets
```

## 📡 Data Flow

1. **Telegram Bot** processes invoice image
2. **Gemini AI** extracts invoice data
3. **Compliance Engine** audits the invoice
4. **Convex Database** stores the result
5. **Dashboard** receives real-time update
6. **UI** displays new invoice in audit stream

## 🎯 Key Components

### KPI Cards
Four metric cards showing:
- Total expenditure with invoice count
- ITC eligible amount with compliant count
- Blocked credits with violation count
- Compliance rate percentage

### Live Audit Stream
Real-time table displaying:
- Vendor name and category
- Compliance status badge
- Invoice amount
- Animated row reveals

### Charts
- **Pie Chart**: Category-wise spending distribution
- **Bar Chart**: Status-wise invoice breakdown
- Interactive tooltips with formatted values

## 🔧 Customization

### Changing Colors
Edit CSS variables in `src/app/globals.css`:

```css
:root {
  --primary: 139 92 246;    /* Purple */
  --accent: 236 72 153;     /* Pink */
  --profit: 34 197 94;      /* Green */
  --loss: 239 68 68;        /* Red */
}
```

### Adjusting Animations
Modify animation delays in `globals.css`:

```css
.stagger-1 { animation-delay: 0.1s; }
.stagger-2 { animation-delay: 0.2s; }
```

### Adding New Charts
Use Recharts components in `page.tsx`:

```tsx
import { LineChart, Line } from "recharts";
```

## 🚀 Deployment

### Vercel (Recommended)
```bash
npm run build
vercel deploy
```

### Environment Variables
Set in Vercel dashboard:
- `NEXT_PUBLIC_CONVEX_URL`

## 📝 Development

### Running Locally
```bash
npm run dev
```

### Building for Production
```bash
npm run build
npm start
```

### Linting
```bash
npm run lint
```

## 🎨 Design Credits

- **Typography**: Syne by Bonjour Monde, JetBrains Mono by JetBrains
- **Color Inspiration**: Financial terminals, IDE themes (Dracula, Monokai)
- **UI Patterns**: Glass morphism, Neon effects, Terminal aesthetics

## 📄 License

Part of the Micro-CFO project.

---

**Built with ❤️ for financial compliance automation**
