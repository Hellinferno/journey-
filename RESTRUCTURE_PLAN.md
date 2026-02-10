# Repository Restructuring Plan

## Goal
Reorganize the repository to match deployment architecture:
- `dashboard/` → Deploys to Vercel (with convex/)
- `bot/` → Deploys to Railway (Python bot)

## Current Issues
1. `micro-cfo/convex/` should be in `dashboard/convex/`
2. `micro-cfo/` should be renamed to `bot/`
3. Convex schema needs to be in one place (dashboard)

## Restructuring Steps

### Step 1: Rename micro-cfo to bot
```bash
git mv micro-cfo bot
```

### Step 2: Move convex to dashboard (if not already there)
```bash
# Check if dashboard already has convex
# If micro-cfo/convex exists and dashboard/convex doesn't:
git mv bot/convex dashboard/convex

# If both exist, merge them (dashboard/convex should be the source of truth)
```

### Step 3: Update import paths in bot
- Update any references to `micro-cfo` → `bot`
- Update convex imports to point to `../dashboard/convex`

### Step 4: Update documentation
- Update README.md
- Update DEPLOYMENT_GUIDE.md
- Update structure.md
- Update all references to folder names

### Step 5: Update .gitignore
```
# Python
bot/__pycache__/
bot/.env
bot/.pytest_cache/

# Dashboard
dashboard/node_modules/
dashboard/.next/
dashboard/.env.local

# Convex
dashboard/convex/.env.local
```

### Step 6: Update deployment configs
- Railway: Point to `bot/` directory
- Vercel: Point to `dashboard/` directory

## New Structure

```
journey/                    <-- GIT ROOT
├── dashboard/              <-- VERCEL DEPLOYMENT
│   ├── convex/             <-- Convex Schema & Functions
│   │   ├── schema.ts
│   │   ├── legalDocs.ts
│   │   ├── invoices.ts
│   │   └── users.ts
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── lib/
│   ├── package.json
│   ├── next.config.ts
│   └── .env.local          <-- NEXT_PUBLIC_CONVEX_URL
│
├── bot/                    <-- RAILWAY DEPLOYMENT
│   ├── app/
│   │   ├── ai.py
│   │   ├── compliance.py
│   │   ├── rag_analyzer.py
│   │   ├── rag_query.py
│   │   ├── rules.py
│   │   └── schemas.py
│   ├── scripts/
│   │   └── ingest_pdfs.py
│   ├── tests/
│   ├── bot.py
│   ├── requirements.txt
│   ├── Procfile
│   ├── railway.json
│   └── .env               <-- TELEGRAM_TOKEN, GOOGLE_API_KEY, CONVEX_URL
│
├── .gitignore
├── README.md
├── a2017-12.pdf
└── Income-tax-Act-2025.pdf
```

## Benefits

1. **Clear Separation**: Dashboard and bot are separate deployable units
2. **Single Source of Truth**: Convex schema lives in dashboard only
3. **Easy Deployment**: Each folder deploys independently
4. **Better Organization**: Matches deployment architecture
5. **No Duplication**: Convex schema not duplicated

## Deployment Commands

### Dashboard (Vercel)
```bash
cd dashboard
npm run build
vercel deploy --prod
```

### Bot (Railway)
```bash
cd bot
railway up
```

## Environment Variables

### Dashboard (.env.local)
```
NEXT_PUBLIC_CONVEX_URL=https://your-project.convex.cloud
```

### Bot (.env)
```
TELEGRAM_TOKEN=your_telegram_token
GOOGLE_API_KEY=your_google_api_key
CONVEX_URL=https://your-project.convex.cloud
```

## Migration Checklist

- [ ] Backup current repository
- [ ] Rename micro-cfo to bot
- [ ] Ensure dashboard/convex is the source of truth
- [ ] Remove bot/convex if it exists
- [ ] Update all import paths
- [ ] Update documentation
- [ ] Update .gitignore
- [ ] Test bot locally
- [ ] Test dashboard locally
- [ ] Deploy to Railway
- [ ] Deploy to Vercel
- [ ] Verify both work together
- [ ] Update GitHub README

## Rollback Plan

If something goes wrong:
```bash
git reset --hard HEAD~1
git clean -fd
```

## Notes

- Keep PDFs in root (both bot and dashboard may need them)
- Keep .kiro/ in root (development configuration)
- Tests stay with bot (they test bot functionality)
- Convex functions are called by both bot and dashboard via API
