# Micro CFO - AI-Powered Tax Compliance Bot

An intelligent Telegram bot that analyzes invoices for GST and Income Tax compliance using RAG (Retrieval-Augmented Generation) technology.

## 🎯 Features

- **Invoice Analysis**: Extract and analyze invoice details from images
- **GST Compliance**: Validate GSTIN, check GST rates, determine ITC eligibility
- **Income Tax Compliance**: Check cash payment limits (Section 40A(3))
- **AI-Powered Decisions**: Context-aware compliance analysis using Gemini 2.5 Flash
- **Legal Citations**: Provides source documents and page numbers
- **Multi-Layer Validation**: Hard rules + Vector search + AI analysis

## 📊 System Architecture

```
┌─────────────────────────────────────────┐
│     RAG Compliance Engine               │
├─────────────────────────────────────────┤
│  📊 Convex Vector Database              │
│     ├─ 2593 legal document chunks       │
│     ├─ GST Act 2017 (544 chunks)        │
│     └─ Income Tax Act 2025 (2049 chunks)│
│                                         │
│  🤖 AI Analysis (Gemini 2.5 Flash)      │
│  🔍 RAG Query Engine                    │
│  ✅ Hard Rules Validator                │
│  📱 Telegram Bot Interface              │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Tesseract OCR
- Node.js (for Convex)
- Telegram Bot Token
- Google Gemini API Key

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd micro-cfo
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Node dependencies**
```bash
npm install
```

4. **Configure environment variables**

Create `.env` file:
```env
TELEGRAM_TOKEN=your_telegram_bot_token
GOOGLE_API_KEY=your_google_api_key
CONVEX_URL=your_convex_deployment_url
TESSERACT_CMD=path_to_tesseract
```

5. **Deploy Convex database**
```bash
npx convex deploy
```

6. **Start the bot**
```bash
python bot.py
```

## 📁 Project Structure

```
micro-cfo/
├── app/                    # Core application code
│   ├── ai.py              # AI analysis module
│   ├── compliance.py      # Compliance orchestrator
│   ├── extraction.py      # Invoice extraction
│   ├── rag_analyzer.py    # AI compliance analyzer
│   ├── rag_query.py       # RAG query engine
│   ├── rules.py           # Hard rules validator
│   └── schemas.py         # Data models
├── convex/                # Convex database functions
│   ├── schema.ts          # Database schema
│   └── legalDocs.ts       # Legal documents functions
├── scripts/               # Utility scripts
│   └── ingest_pdfs.py     # PDF ingestion pipeline
├── tests/                 # Test suite
│   ├── test_hard_rules.py
│   ├── test_gstin_properties.py
│   └── test_gst_rate_properties.py
├── bot.py                 # Main bot entry point
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🧪 Testing

Run the integration tests:
```bash
python test_bot_integration.py
```

Run property-based tests:
```bash
pytest tests/
```

Verify system status:
```bash
python verify_system.py
```

## 📖 Usage

### On Telegram

1. Start a conversation with your bot
2. Send `/start` to see instructions
3. Send an invoice image
4. Receive compliance analysis with:
   - ITC eligibility determination
   - Compliance flags
   - Legal citations
   - AI-powered reasoning

### Example Analysis

```json
{
  "status": "compliant",
  "category": "Office Supplies",
  "itc_eligible": true,
  "flags": [
    "ITC eligibility for office supplies is generally allowed",
    "No specific provisions blocking ITC"
  ],
  "citations": [
    {"source": "a2017-12.pdf", "page": 35}
  ]
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_TOKEN` | Telegram bot token from @BotFather | Yes |
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `CONVEX_URL` | Convex deployment URL | Yes |
| `TESSERACT_CMD` | Path to Tesseract OCR executable | Yes |

### Convex Schema

The system uses a 3072-dimensional vector index for embeddings:
- Model: `models/gemini-embedding-001`
- Dimensions: 3072
- Filter fields: category, source_file

## 📊 System Capabilities

### GST Compliance
- ✅ GSTIN format validation
- ✅ GST rate validation (5%, 12%, 18%, 28%)
- ✅ ITC eligibility determination
- ✅ Section 17(5) blocking rules
- ✅ Legal citation tracking

### Income Tax Compliance
- ✅ Section 40A(3) cash payment limits
- ✅ Deduction allowability
- ✅ Capital vs revenue expenditure
- ✅ TDS requirements

### AI Analysis
- ✅ Context-aware decisions
- ✅ Legal reasoning
- ✅ Explainable results
- ✅ Page-level citations

## 🛠️ Development

### Adding New Rules

Edit `app/rules.py` to add hard validation rules:

```python
def validate_custom_rule(invoice: InvoiceData) -> bool:
    # Your validation logic
    return True
```

### Ingesting New Documents

Use the ingestion script:

```bash
python scripts/ingest_pdfs.py
```

The script automatically:
- Chunks documents
- Generates embeddings
- Stores in Convex
- Tracks progress
- Resumes on failure

## 📈 Performance

- **Test Pass Rate**: 100% (4/4 integration tests)
- **PDF Ingestion**: 100% (2593/2593 chunks)
- **Response Time**: < 5 seconds
- **Accuracy**: High (AI-powered with legal context)

## 🐛 Troubleshooting

### Bot Conflict Error

If you see `Conflict: terminated by other getUpdates request`:

1. Stop all Python processes
2. Wait 30 seconds
3. Restart the bot

See `BOT_STATUS_AND_SOLUTION.md` for detailed troubleshooting.

### Invoice Extraction Fails

- Verify Tesseract OCR is installed
- Check `TESSERACT_CMD` path in `.env`
- Ensure image is clear and readable

### RAG Analysis Unavailable

- Check `GOOGLE_API_KEY` in `.env`
- Verify Convex connection
- System will fall back to hard rules

## 📚 Documentation

- `100_PERCENT_COMPLETE.md` - Complete system overview
- `MISSION_ACCOMPLISHED.md` - Achievement summary
- `BOT_STATUS_AND_SOLUTION.md` - Bot troubleshooting
- `START_BOT_GUIDE.md` - Detailed startup guide

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

- **Google Gemini API** - Embeddings and AI analysis
- **Convex** - Vector database
- **Telegram Bot API** - User interface
- **Tesseract OCR** - Text extraction

## 📞 Support

For issues and questions:
- Check documentation in the repository
- Review troubleshooting guides
- Open an issue on GitHub

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: February 2026
