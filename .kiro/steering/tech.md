# Technology Stack

## Backend (Telegram Bot)

### Core Technologies
- **Python 3.11+**: Primary language
- **python-telegram-bot 22.6+**: Telegram Bot API wrapper
- **google-generativeai**: Gemini AI for invoice extraction and embeddings
- **Convex**: Serverless database with vector search
- **Pydantic**: Data validation and schemas
- **Pillow**: Image processing
- **pypdf 3.0+**: PDF text extraction

### Testing
- **pytest 7.0+**: Test framework
- **hypothesis 6.0+**: Property-based testing library
- **reportlab 4.0+**: PDF generation for tests

### AI/ML
- **Gemini 2.5 Flash**: Invoice data extraction and compliance analysis
- **gemini-embedding-001**: Vector embeddings (3072 dimensions)
- **RAG Architecture**: Vector search over legal documents

## Frontend (Dashboard)

### Core Technologies
- **Next.js 16**: React framework with App Router
- **React 19**: UI library
- **TypeScript 5**: Type safety
- **Tailwind CSS v4**: Styling with @tailwindcss/postcss
- **Convex 1.31+**: Real-time database client

### UI Components
- **Recharts 3.7+**: Charts and data visualization
- **Lucide React**: Icon library
- **shadcn/ui patterns**: Custom UI components
- **class-variance-authority**: Component variants
- **tailwind-merge**: Utility class merging

### Development
- **ESLint 9**: Linting
- **fast-check 3.15+**: Property-based testing for TypeScript
- **babel-plugin-react-compiler**: React optimization

## Database

### Convex Schema
- **Vector Index**: 3072-dimensional embeddings for legal documents
- **Filter Fields**: category, source_file
- **Tables**: users, invoices, legal_docs, messages
- **Real-time Sync**: Automatic updates to dashboard

## Common Commands

### Telegram Bot (micro-cfo/)

```bash
# Setup
pip install -r requirements.txt
python -m venv venv
venv\Scripts\activate  # Windows

# Start bot
python bot.py

# Run integration tests
python test_bot_integration.py

# Run property-based tests
pytest tests/

# Ingest legal PDFs
python scripts/ingest_pdfs.py

# Deploy Convex schema
npx convex deploy
```

### Dashboard (dashboard/)

```bash
# Setup
npm install

# Development
npm run dev

# Build
npm run build

# Production
npm start

# Lint
npm run lint

# Deploy Convex schema
npx convex deploy
```

## Environment Configuration

### Bot (.env in micro-cfo/)
```
TELEGRAM_TOKEN=your_telegram_bot_token
GOOGLE_API_KEY=your_google_gemini_api_key
CONVEX_URL=your_convex_deployment_url
```

### Dashboard (.env.local in dashboard/)
```
NEXT_PUBLIC_CONVEX_URL=your_convex_deployment_url
```

## Key Dependencies Notes

- **Embedding Dimensions**: Must use 3072 for gemini-embedding-001 (not 768)
- **Convex Schema**: Shared between bot and dashboard via convex/ folder
- **Python Version**: Requires 3.11+ for modern type hints
- **Node.js**: Required for Convex CLI and dashboard
