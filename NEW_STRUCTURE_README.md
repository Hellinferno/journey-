# Micro-CFO - Restructured Repository

## 🎯 New Repository Structure

This repository has been restructured to match the deployment architecture for clean, independent deployments.

```
journey/                    <-- GIT ROOT (Repository)
├── bot/                    <-- DEPLOYS TO RAILWAY 🚂
│   ├── app/                <-- Python Business Logic
│   │   ├── ai.py           <-- Invoice extraction (Gemini AI)
│   │   ├── compliance.py   <-- Compliance orchestrator
│   │   ├── rag_analyzer.py <-- AI compliance analyzer
│   │   ├── rag_query.py    <-- RAG query engine
│   │   ├── rules.py        <-- Hard rules validator
│   │   └── schemas.py      <-- Pydantic data models
│   ├── scripts/
│   │   └── ingest_pdfs.py  <-- PDF ingestion pipeline
│   ├── tests/              <-- 18 test files, 135+ test cases
│   ├── bot.py              <-- Main Telegram bot entry point
│   ├── requirements.txt    <-- Python dependencies
│   ├── Procfile            <-- Railway start command
│   ├── railway.json        <-- Railway configuration
│   └── .env                <-- API keys (not in git)
│
├── dashboard/              <-- DEPLOYS TO VERCEL ▲
│   ├── convex/             <-- ✨ Database Schema & Functions (Single Source of Truth)
│   │   ├── schema.ts       <-- Database schema with vector index
│   │   ├── legalDocs.ts    <-- Legal document queries
│   │   ├── invoices.ts     <-- Invoice CRUD operations
│   │   └── users.ts        <-- User management
│   ├── src/
│   │   ├── app/            <-- Next.js pages
│   │   ├── components/     <-- React components
│   │   └── lib/            <-- Utilities
│   ├── package.json        <-- Node dependencies
│   ├── next.config.ts      <-- Next.js configuration
│   └── .env.local          <-- Convex URL (not in git)
│
├── .kiro/                  <-- Kiro configuration
│   ├── specs/              <-- Feature specifications
│   └── steering/           <-- Project steering rules
│
├── a2017-12.pdf            <-- GST Act (544 chunks)
├── Income-tax-Act-2025.pdf <-- Income Tax Act (2049 chunks)
├── .gitignore
└── README.md
```

## 🚀 Key Changes

### ✅ What Changed

1. **`micro-cfo/` → `bot/`**
   - Clearer naming that matches deployment target
   - Easier to understand repository structure

2. **Removed `bot/convex/`**
   - `dashboard/convex/` is now the single source of truth
   - No more duplicate schema files
   - Easier to maintain consistency

3. **Clean Separation**
   - Bot folder = Railway deployment
   - Dashboard folder = Vercel deployment
   - Each folder is independently deployable

### 🎯 Benefits

- **Clear Deployment Targets**: Each folder maps to one deployment
- **No Duplication**: Convex schema in one place only
- **Easy Maintenance**: Update schema in dashboard/convex/, deploy once
- **Better Organization**: Structure matches architecture
- **Independent Scaling**: Deploy bot and dashboard separately

## 📦 Deployment

### Bot (Railway)

```bash
# Deploy to Railway
cd bot
railway up

# Or use Railway CLI
railway link
railway up
```

**Environment Variables (Railway):**
```
TELEGRAM_TOKEN=your_telegram_bot_token
GOOGLE_API_KEY=your_google_gemini_api_key
CONVEX_URL=https://your-project.convex.cloud
```

### Dashboard (Vercel)

```bash
# Deploy to Vercel
cd dashboard
vercel deploy --prod

# Or use Vercel CLI
vercel link
vercel deploy --prod
```

**Environment Variables (Vercel):**
```
NEXT_PUBLIC_CONVEX_URL=https://your-project.convex.cloud
```

### Convex (Database)

```bash
# Deploy Convex schema (from dashboard folder)
cd dashboard
npx convex deploy
```

## 🔧 Local Development

### Start Bot

```bash
cd bot
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python bot.py
```

### Start Dashboard

```bash
cd dashboard
npm install
npm run dev
```

Open http://localhost:3000

### Run Tests

```bash
cd bot
pytest tests/ -v
```

## 📊 System Architecture

```
┌─────────────┐
│   Telegram  │
│    User     │
└──────┬──────┘
       │ Sends invoice image
       ▼
┌─────────────────────────────────────┐
│         Bot (Railway)               │
│  ┌──────────────────────────────┐  │
│  │  bot.py                      │  │
│  │  ├─> app/ai.py (Extract)    │  │
│  │  ├─> app/rules.py (Validate)│  │
│  │  ├─> app/rag_query.py       │  │
│  │  └─> app/compliance.py      │  │
│  └──────────────────────────────┘  │
└──────────┬──────────────────────────┘
           │
           │ Stores invoice
           ▼
    ┌──────────────┐
    │    Convex    │
    │   Database   │
    │ (Vector DB)  │
    └──────┬───────┘
           │
           │ Real-time sync
           ▼
┌─────────────────────────────────────┐
│      Dashboard (Vercel)             │
│  ┌──────────────────────────────┐  │
│  │  Next.js App                 │  │
│  │  ├─> KPI Cards               │  │
│  │  ├─> Live Audit Stream       │  │
│  │  └─> Charts                  │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
           │
           ▼
    ┌──────────────┐
    │   Browser    │
    │   (User)     │
    └──────────────┘
```

## 🔄 Migration Guide

If you're migrating from the old structure:

1. **Close all applications** using the folders
2. **Run the migration script**: `RESTRUCTURE_MIGRATION.bat`
3. **Test locally**:
   ```bash
   cd bot && python bot.py
   cd dashboard && npm run dev
   ```
4. **Push to GitHub**: `git push origin main`
5. **Redeploy**:
   - Railway: Point to `bot/` directory
   - Vercel: Point to `dashboard/` directory

## 📝 Important Notes

### Convex Schema

- **Single Source**: `dashboard/convex/` is the only place for schema
- **Deployment**: Deploy from dashboard folder: `npx convex deploy`
- **Access**: Both bot and dashboard access via Convex API

### Environment Variables

**Bot (.env):**
```env
TELEGRAM_TOKEN=your_token
GOOGLE_API_KEY=your_key
CONVEX_URL=https://your-project.convex.cloud
```

**Dashboard (.env.local):**
```env
NEXT_PUBLIC_CONVEX_URL=https://your-project.convex.cloud
```

### PDFs

- Keep in root directory
- Both bot and dashboard can access them
- Used for PDF ingestion: `python bot/scripts/ingest_pdfs.py`

## 🧪 Testing

```bash
# Run all tests
cd bot
pytest tests/ -v

# Run specific test
pytest tests/test_gst_rate_properties.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## 📚 Documentation

- **Bot**: See `bot/README.md` (if exists)
- **Dashboard**: See `dashboard/README.md`
- **Deployment**: See `DEPLOYMENT_GUIDE.md`
- **API**: See `dashboard/convex/README.md`

## 🆘 Troubleshooting

### Bot not connecting to Convex

1. Check `CONVEX_URL` in `bot/.env`
2. Ensure Convex deployment is active
3. Verify API key permissions

### Dashboard not showing data

1. Check `NEXT_PUBLIC_CONVEX_URL` in `dashboard/.env.local`
2. Ensure bot has processed at least one invoice
3. Check browser console for errors

### Tests failing

1. Ensure virtual environment is activated
2. Install dependencies: `pip install -r bot/requirements.txt`
3. Check Python version: `python --version` (should be 3.11+)

## 🎉 Success Criteria

After restructuring, you should have:

- ✅ Clean folder structure matching deployment
- ✅ Bot deploys independently to Railway
- ✅ Dashboard deploys independently to Vercel
- ✅ Single Convex schema in dashboard/convex/
- ✅ All tests passing
- ✅ Both services communicating via Convex

## 📞 Support

For issues or questions:
1. Check documentation in each folder
2. Review deployment guides
3. Check GitHub issues
4. Verify environment variables

---

**Built with ❤️ for financial compliance automation**
