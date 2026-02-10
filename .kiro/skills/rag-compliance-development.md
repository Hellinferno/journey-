# RAG Compliance Development Skill

Expert guidance for developing and maintaining RAG-powered compliance systems with property-based testing, vector search, and AI-driven analysis.

## Core Principles

### 1. RAG Architecture Patterns
- **Vector Search First**: Always query legal document embeddings before making compliance decisions
- **Multi-Layer Validation**: Combine hard rules (fast, deterministic) with AI analysis (context-aware, flexible)
- **Citation Tracking**: Every compliance decision must reference source documents with page numbers
- **Embedding Consistency**: Use consistent dimensions (3072 for gemini-embedding-001) across ingestion and query

### 2. Property-Based Testing
- **Use Hypothesis**: Generate test cases that explore edge cases automatically
- **Test Properties, Not Examples**: Focus on invariants that should always hold
- **Shrinking**: Let Hypothesis find minimal failing cases for easier debugging
- **Stateful Testing**: Model complex workflows with state machines

### 3. Compliance Domain Modeling
- **Pydantic Schemas**: Use strict type validation for all domain models
- **Enum Categories**: Define fixed categories for expense types, compliance statuses
- **Optional Fields**: Mark fields as optional when they may be missing from invoices
- **Validation Methods**: Add custom validators for domain-specific rules (GSTIN format, GST rates)

## Implementation Patterns

### RAG Query Pipeline

```python
# 1. Generate search query from invoice context
query = generate_search_query(invoice, category)

# 2. Create embedding
embedding = create_embedding(query)

# 3. Vector search with filters
results = vector_search(
    embedding=embedding,
    filters={"category": "GST"},
    limit=5
)

# 4. Extract citations
citations = [{"source": r.source_file, "page": r.page_number} 
             for r in results]

# 5. AI analysis with legal context
analysis = ai_analyze(invoice, legal_context=results, citations=citations)
```

### Property-Based Test Structure

```python
from hypothesis import given, strategies as st

@given(
    gstin=st.from_regex(r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$"),
    amount=st.floats(min_value=0.01, max_value=1000000)
)
def test_valid_gstin_property(gstin, amount):
    """Valid GSTINs should always pass validation"""
    invoice = InvoiceData(gstin=gstin, total_amount=amount, ...)
    result = validate_gstin(invoice)
    assert result.is_valid
    assert "invalid" not in result.flags
```

### Hard Rules Validation

```python
def validate_hard_rules(invoice: InvoiceData) -> ValidationResult:
    """Fast, deterministic validation before AI analysis"""
    flags = []
    
    # GSTIN format check
    if invoice.gstin and not is_valid_gstin_format(invoice.gstin):
        flags.append("Invalid GSTIN format")
    
    # GST rate validation
    if invoice.gst_rate not in [5, 12, 18, 28]:
        flags.append(f"Invalid GST rate: {invoice.gst_rate}%")
    
    # Cash limit check (Section 40A(3))
    if invoice.total_amount > 10000 and invoice.payment_mode == "cash":
        flags.append("Cash payment exceeds ₹10,000 limit (Section 40A(3))")
    
    return ValidationResult(flags=flags, is_valid=len(flags) == 0)
```

### PDF Ingestion with Progress Tracking

```python
def ingest_pdf_with_progress(pdf_path: str, category: str):
    """Ingest PDF with chunking, embedding, and progress tracking"""
    # Extract text with page numbers
    pages = extract_pdf_pages(pdf_path)
    
    # Chunk with overlap
    chunks = []
    for page_num, text in pages:
        page_chunks = chunk_text(text, chunk_size=500, overlap=50)
        chunks.extend([(chunk, page_num) for chunk in page_chunks])
    
    # Batch embed and store
    batch_size = 10
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        embeddings = create_embeddings([c[0] for c in batch])
        
        # Store in vector database
        for (chunk_text, page_num), embedding in zip(batch, embeddings):
            store_legal_doc(
                chunk_text=chunk_text,
                source_file=pdf_path,
                page_number=page_num,
                category=category,
                embedding=embedding
            )
        
        print(f"Progress: {i+len(batch)}/{len(chunks)} chunks")
```

## Best Practices

### 1. Error Handling
- **Graceful Degradation**: Fall back to hard rules if RAG/AI fails
- **Retry Logic**: Implement exponential backoff for API calls
- **Logging**: Log all errors with context (invoice ID, user ID, timestamp)
- **User Feedback**: Provide clear error messages to end users

### 2. Performance Optimization
- **Batch Operations**: Process embeddings in batches (10-20 at a time)
- **Caching**: Cache embeddings for repeated queries
- **Async Operations**: Use async/await for I/O-bound operations
- **Vector Index Filters**: Use category/source filters to reduce search space

### 3. Testing Strategy
- **Unit Tests**: Test individual validators and extractors
- **Property Tests**: Test invariants with Hypothesis
- **Integration Tests**: Test full workflow with real invoices
- **Regression Tests**: Add tests for every bug found

### 4. Schema Evolution
- **Optional Fields**: Add new fields as optional to maintain backward compatibility
- **Migration Scripts**: Write scripts to backfill data when schema changes
- **Version Tracking**: Track schema version in database
- **Deploy Atomically**: Use `npx convex deploy` to update schema atomically

## Common Patterns

### Compliance Status Determination

```python
def determine_compliance_status(
    hard_rules_result: ValidationResult,
    ai_analysis: AIAnalysis
) -> str:
    """Combine hard rules and AI analysis for final status"""
    
    # Hard rules violations = blocked
    if any("Section 17(5)" in flag for flag in hard_rules_result.flags):
        return "blocked"
    
    if any("Section 40A(3)" in flag for flag in hard_rules_result.flags):
        return "blocked"
    
    # AI determines ITC eligibility
    if not ai_analysis.itc_eligible:
        return "review_needed"
    
    # No violations = compliant
    if len(hard_rules_result.flags) == 0:
        return "compliant"
    
    return "review_needed"
```

### Citation Formatting

```python
def format_citations(citations: List[Citation]) -> str:
    """Format legal citations for user display"""
    if not citations:
        return "No legal references found"
    
    formatted = []
    for citation in citations:
        source_name = citation.source.replace(".pdf", "")
        formatted.append(f"📄 {source_name}, Page {citation.page}")
    
    return "\n".join(formatted)
```

### Test Case Generation

```python
# Generate test cases for different expense categories
@given(
    category=st.sampled_from([
        "Office Supplies", "Food & Beverage", "Travel", 
        "Professional Services", "Rent", "Utilities"
    ]),
    amount=st.floats(min_value=100, max_value=50000)
)
def test_category_compliance_properties(category, amount):
    """Test compliance rules across all categories"""
    invoice = create_test_invoice(category=category, amount=amount)
    result = audit_invoice(invoice)
    
    # Property: Food & Beverage should always be flagged (Section 17(5))
    if category == "Food & Beverage":
        assert "Section 17(5)" in str(result.flags)
        assert result.status in ["blocked", "review_needed"]
    
    # Property: Office Supplies should generally be compliant
    if category == "Office Supplies" and amount < 10000:
        assert result.status == "compliant"
```

## Anti-Patterns to Avoid

### ❌ Don't: Skip Hard Rules Validation
```python
# BAD: Going straight to AI without basic validation
result = ai_analyze(invoice)
```

### ✅ Do: Validate First, Then Analyze
```python
# GOOD: Fast hard rules first, then expensive AI
hard_rules = validate_hard_rules(invoice)
if hard_rules.is_blocked:
    return {"status": "blocked", "flags": hard_rules.flags}

ai_result = ai_analyze_with_rag(invoice)
return combine_results(hard_rules, ai_result)
```

### ❌ Don't: Ignore Embedding Dimensions
```python
# BAD: Mismatched dimensions cause vector search to fail
vector_index(dimensions=768)  # Wrong!
embedding = gemini_embed(text)  # Returns 3072 dimensions
```

### ✅ Do: Match Embedding Model Dimensions
```python
# GOOD: Consistent dimensions throughout
vector_index(dimensions=3072)  # Matches gemini-embedding-001
embedding = gemini_embed(text)  # Returns 3072 dimensions
```

### ❌ Don't: Forget Citations
```python
# BAD: No way to verify AI decisions
return {"itc_eligible": True, "reasoning": "Looks good"}
```

### ✅ Do: Always Include Citations
```python
# GOOD: Traceable to source documents
return {
    "itc_eligible": True,
    "reasoning": "Office supplies are generally eligible",
    "citations": [{"source": "a2017-12.pdf", "page": 35}]
}
```

## Debugging Techniques

### 1. Vector Search Quality
```python
# Check if relevant documents are being retrieved
results = vector_search(query_embedding)
for r in results:
    print(f"Score: {r.score}, Page: {r.page}, Preview: {r.text[:100]}")
```

### 2. Embedding Consistency
```python
# Verify embedding dimensions
embedding = create_embedding("test query")
assert len(embedding) == 3072, f"Expected 3072, got {len(embedding)}"
```

### 3. Property Test Failures
```python
# Hypothesis will shrink to minimal failing case
# Example output:
# Falsifying example: test_gstin_validation(gstin='00AAAAA0000A0Z0')
# This helps identify the exact edge case causing failure
```

## Integration with Telegram Bot

### Message Handler Pattern
```python
async def handle_invoice_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process invoice with full compliance workflow"""
    try:
        # 1. Download and extract
        file_path = await download_photo(update.message.photo[-1])
        invoice = analyze_invoice(file_path)
        
        # 2. Audit with RAG
        audit_result = audit_invoice(invoice)
        
        # 3. Store in database
        store_invoice(invoice, audit_result)
        
        # 4. Format response
        response = format_compliance_response(invoice, audit_result)
        await update.message.reply_text(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Invoice processing failed: {e}")
        await update.message.reply_text("⚠️ Processing failed. Please try again.")
    finally:
        cleanup_temp_files(file_path)
```

## Monitoring and Observability

### Key Metrics to Track
- **Processing Time**: Invoice extraction + RAG query + AI analysis
- **Success Rate**: Percentage of invoices processed without errors
- **Compliance Distribution**: Compliant vs review_needed vs blocked
- **API Quota Usage**: Track Gemini API calls and quota limits
- **Vector Search Quality**: Average relevance scores of retrieved documents

### Logging Best Practices
```python
logger.info(f"Processing invoice for user {user_id}")
logger.debug(f"Extracted data: {invoice.dict()}")
logger.info(f"Hard rules: {len(hard_rules.flags)} flags")
logger.info(f"RAG retrieved {len(rag_results)} documents")
logger.info(f"Final status: {audit_result.status}")
```

## Summary

This skill provides patterns for building robust RAG-powered compliance systems with:
- Multi-layer validation (hard rules + AI)
- Property-based testing for edge case coverage
- Vector search with proper embedding management
- Citation tracking for explainability
- Graceful error handling and fallbacks

Apply these patterns consistently across the codebase for maintainable, reliable compliance automation.
