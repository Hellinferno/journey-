# Project Structure

## Repository Layout

```
journey/
├── bot/                    # Python Telegram bot (main application)
├── dashboard/              # Next.js real-time dashboard
├── .kiro/                  # Kiro configuration and specs
│   ├── specs/              # Feature specifications
│   └── steering/           # Project steering rules
└── *.pdf                   # Legal documents (GST Act, Income Tax Act)
```

## Telegram Bot (bot/)

```
bot/
├── app/                    # Core application modules
│   ├── ai.py              # Invoice extraction using Gemini AI
│   ├── compliance.py      # Compliance orchestrator (main workflow)
│   ├── rag_analyzer.py    # AI compliance analyzer with legal context
│   ├── rag_query.py       # RAG query engine for vector search
│   ├── rules.py           # Hard rules validator (GSTIN, GST rates, cash limits)
│   └── schemas.py         # Pydantic data models (InvoiceData, ExpenseCategory)
├── convex/                # Convex database functions (TypeScript)
│   ├── schema.ts          # Database schema with vector index
│   ├── legalDocs.ts       # Legal document queries and mutations
│   ├── invoices.ts        # Invoice CRUD operations
│   └── users.ts           # User management
├── scripts/               # Utility scripts
│   └── ingest_pdfs.py     # PDF ingestion pipeline for legal documents
├── tests/                 # Property-based test suite
│   ├── test_hard_rules.py              # Hard rules validation tests
│   ├── test_gstin_properties.py        # GSTIN format properties
│   ├── test_gst_rate_properties.py     # GST rate validation properties
│   ├── test_whitespace_rejection_properties.py
│   ├── test_flag_aggregation_properties.py
│   └── test_pdf_ingestion.py           # PDF chunking tests
├── bot.py                 # Main bot entry point
├── test_bot_integration.py # Integration test suite
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration (not in git)
└── PROJECT_STATUS.md      # Detailed project documentation
```

## Dashboard (dashboard/)

```
dashboard/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Main dashboard page
│   │   ├── layout.tsx            # Root layout with fonts
│   │   ├── globals.css           # Global styles and animations
│   │   └── ConvexClientProvider.tsx # Convex real-time client
│   ├── components/
│   │   └── ui/                   # Reusable UI components
│   │       ├── badge.tsx         # Status badges
│   │       ├── card.tsx          # KPI cards
│   │       └── table.tsx         # Audit stream table
│   └── lib/
│       └── utils.ts              # Utility functions (cn, formatters)
├── convex/                       # Convex schema (synced with bot)
│   ├── schema.ts                 # Database schema
│   ├── legalDocs.ts              # Legal docs queries
│   ├── invoices.ts               # Invoice queries
│   └── users.ts                  # User queries
├── public/                       # Static assets
├── package.json                  # Node dependencies
├── next.config.ts                # Next.js configuration
├── tailwind.config.ts            # Tailwind CSS configuration
├── tsconfig.json                 # TypeScript configuration
├── .env.local                    # Environment variables (not in git)
└── README.md                     # Dashboard documentation
```

## Kiro Configuration (.kiro/)

```
.kiro/
├── specs/
│   └── rag-compliance-engine/    # RAG compliance feature spec
│       ├── requirements.md       # Feature requirements
│       ├── design.md             # Design document with properties
│       ├── tasks.md              # Implementation task list
│       └── .config.kiro          # Spec configuration
└── steering/                     # Project steering rules
    ├── product.md                # Product overview
    ├── tech.md                   # Tech stack and commands
    └── structure.md              # This file
```

## Key Architectural Patterns

### Module Organization
- **app/**: Business logic modules with single responsibility
- **convex/**: Database layer with TypeScript type safety
- **tests/**: Property-based tests using Hypothesis
- **scripts/**: One-off utilities and data pipelines

### Data Flow
1. **bot.py** → Telegram API handler
2. **app/ai.py** → Invoice extraction
3. **app/compliance.py** → Orchestrates validation workflow
4. **app/rules.py** → Hard rules validation
5. **app/rag_query.py** → Vector search
6. **app/rag_analyzer.py** → AI analysis with legal context
7. **convex/** → Data persistence
8. **dashboard/** → Real-time visualization

### Shared Components
- **Convex Schema**: Defined in `dashboard/convex/` (single source of truth)
- **Legal Documents**: PDFs in root directory, ingested into Convex vector database
- **Environment Variables**: Separate `.env` files for bot and dashboard

## File Naming Conventions

### Python
- **Modules**: lowercase with underscores (`rag_query.py`)
- **Classes**: PascalCase (`InvoiceData`, `ExpenseCategory`)
- **Functions**: lowercase with underscores (`analyze_invoice()`)
- **Tests**: `test_*.py` prefix for pytest discovery

### TypeScript
- **Components**: PascalCase (`ConvexClientProvider.tsx`)
- **Utilities**: camelCase (`utils.ts`)
- **Convex Functions**: camelCase with namespace (`invoices:add`)

## Important Notes

- **Convex Schema Sync**: Changes to schema must be deployed with `npx convex deploy`
- **Vector Dimensions**: Must use 3072 for gemini-embedding-001 embeddings
- **Test Discovery**: pytest finds tests in `tests/` directory with `test_*.py` pattern
- **Environment Files**: Never commit `.env` or `.env.local` files
