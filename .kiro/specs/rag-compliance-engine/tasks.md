# Implementation Plan: RAG Compliance Engine

## Overview

This implementation plan breaks down the RAG Compliance Engine into discrete, actionable tasks. The system combines rule-based validation with AI-powered legal reasoning using Retrieval-Augmented Generation (RAG). Implementation follows three phases:

**Phase 1: Database and Ingestion** - Set up Convex schema, vector search functions, and PDF ingestion pipeline
**Phase 2: RAG Engine Core** - Implement hard rules validator, RAG query engine, AI analyzer, and compliance orchestrator
**Phase 3: Bot Integration** - Integrate with Telegram bot, add compliance reporting, and implement monitoring

The implementation includes 21 correctness properties as property-based tests, ensuring comprehensive validation across all requirements.

## Tasks

### Phase 1: Database and Ingestion

- [x] 1. Set up Convex database schema for legal documents
  - [x] 1.1 Update convex/schema.ts with legal_docs table definition
    - Add table with fields: chunk_text, source_file, page_number, category, embedding
    - Create vector index "by_embedding" with 768 dimensions
    - Add filter fields for category and source_file
    - Create indexes on source_file and category
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [x] 1.2 Write property test for embedding dimension validation
    - **Property 1: Embedding Dimension Consistency**
    - **Validates: Requirements 1.2, 2.5, 4.3**

- [x] 2. Implement Convex vector search functions
  - [x] 2.1 Create convex/legalDocs.ts with addLegalDocument mutation
    - Accept chunk_text, source_file, page_number, category, embedding parameters
    - Validate embedding has exactly 768 dimensions
    - Insert document into legal_docs table
    - Throw error if embedding dimensions are invalid
    - _Requirements: 2.1, 2.5, 2.6_

  - [x] 2.2 Create searchLegalDocs query function
    - Accept query_embedding, optional limit (default 3), optional category filter
    - Use vector index to find similar documents
    - Return results ordered by similarity score (descending)
    - Include chunk_text, source_file, page_number, category, and score in results
    - _Requirements: 2.2, 2.3, 2.4_

  - [x] 2.3 Write property test for vector search result ordering
    - **Property 2: Vector Search Result Ordering**
    - **Validates: Requirements 2.3**

  - [x] 2.4 Write unit tests for Convex functions
    - Test addLegalDocument with valid and invalid embeddings
    - Test searchLegalDocs with various query embeddings
    - Test category filtering
    - _Requirements: 2.1, 2.2, 2.5_

- [x] 3. Create PDF ingestion script
  - [x] 3.1 Implement PDFIngestionPipeline class in scripts/ingest_pdfs.py
    - Initialize with Convex client and Gemini API configuration
    - Create process_pdf method to extract text page by page
    - Implement chunk_text method with 1000 char chunks and 100 char overlap
    - Skip empty or whitespace-only chunks
    - _Requirements: 3.1, 3.2, 3.3, 3.6_

  - [x] 3.2 Write property test for text chunking overlap
    - **Property 3: Text Chunking Overlap Preservation**
    - **Validates: Requirements 3.3**

  - [x] 3.3 Write property test for page number preservation
    - **Property 4: Page Number Metadata Preservation**
    - **Validates: Requirements 3.4**

  - [x] 3.4 Write property test for whitespace chunk rejection
    - **Property 5: Whitespace Chunk Rejection**
    - **Validates: Requirements 3.6**

- [x] 4. Implement embedding generation with retry logic
  - [x] 4.1 Add generate_embedding method to PDFIngestionPipeline
    - Use Google text-embedding-004 model
    - Set task_type to "retrieval_document"
    - Implement retry logic with exponential backoff (3 attempts)
    - Return 768-dimensional vector
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 4.2 Add ingest_document method to orchestrate full pipeline
    - Process PDF to extract chunks
    - Generate embeddings for each chunk
    - Store chunks with embeddings in Convex via addLegalDocument
    - Add progress indicators for long-running operations
    - Categorize as "GST" for a2017-12.pdf and "Income_Tax" for Income-tax-Act-2025.pdf
    - _Requirements: 3.5, 3.7, 4.5, 4.6_

  - [x] 4.3 Create main function to ingest both PDFs
    - Load environment variables (CONVEX_URL, GOOGLE_API_KEY)
    - Create pipeline instance
    - Ingest a2017-12.pdf as GST category
    - Ingest Income-tax-Act-2025.pdf as Income_Tax category
    - _Requirements: 3.7, 13.1, 13.2_

  - [x] 4.4 Write unit tests for PDF ingestion
    - Test with sample PDF files
    - Test error handling for corrupted PDFs
    - Test retry logic for API failures
    - _Requirements: 3.1, 3.2, 4.4, 12.3, 12.4_

- [x] 5. Checkpoint - Verify database and ingestion pipeline
  - Run PDF ingestion script with both documents
  - Verify chunks are stored in Convex legal_docs table
  - Test vector search with sample queries
  - Ensure all tests pass, ask the user if questions arise

### Phase 2: RAG Engine Core

- [x] 6. Enhance hard rules validator
  - [x] 6.1 Implement validate_gstin function in app/rules.py
    - Check for exactly 15 characters
    - Validate pattern: [0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}
    - Return boolean result
    - _Requirements: 5.1_

  - [x] 6.2 Write property test for GSTIN format validation
    - **Property 6: GSTIN Format Validation**
    - **Validates: Requirements 5.1**

  - [x] 6.3 Implement validate_gst_rate function
    - Calculate tax rate from total and tax amounts
    - Check if rate is within 0.5% of standard rates (5%, 12%, 18%, 28%)
    - Handle zero total amount edge case
    - _Requirements: 5.2_

  - [ ] 6.4 Write property test for GST rate validation
    - **Property 7: GST Rate Validation**
    - **Validates: Requirements 5.2**

  - [x] 6.5 Implement check_cash_limit function
    - Flag transactions over ₹10,000 with Section 40A(3) warning
    - Return list of violation flags
    - _Requirements: 5.3_

  - [x] 6.6 Implement check_blocked_itc function
    - Map blocked categories (FOOD_BEVERAGE) to Section 17(5) flags
    - Return list of ITC blocking flags
    - _Requirements: 5.4_

  - [x] 6.7 Implement check_math function
    - Validate GST rate calculations
    - Return list of math validation flags
    - _Requirements: 5.2_

  - [x] 6.8 Create HardRulesValidator class
    - Implement validate method that orchestrates all hard rule checks
    - Combine all flags from GSTIN, math, cash limit, and ITC checks
    - Determine preliminary status (compliant, review_needed, blocked)
    - Return dict with status and flags
    - _Requirements: 5.5, 5.6_

  - [ ]* 6.9 Write property test for hard rule violation flagging
    - **Property 8: Hard Rule Violation Flagging**
    - **Validates: Requirements 5.5**

  - [ ]* 6.10 Write unit tests for hard rules validator
    - Test valid and invalid GSTIN formats
    - Test standard and non-standard GST rates
    - Test cash limit boundary (₹10,000)
    - Test blocked ITC categories
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 15.1_

- [ ] 7. Implement RAG query engine
  - [ ] 7.1 Create RAGQueryEngine class in app/rag_query.py
    - Initialize with Gemini API key
    - Configure text-embedding-004 model
    - _Requirements: 4.1, 13.1_

  - [ ] 7.2 Implement generate_search_query method
    - Include expense category in query
    - Include item description in query
    - Add "input tax credit eligibility" if GSTIN present
    - Add "cash payment limits" if amount > ₹10,000
    - Add category-specific keywords (Section 17(5) for food, etc.)
    - Return consolidated query string
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

  - [ ]* 7.3 Write property test for query category inclusion
    - **Property 9: Query Category Inclusion**
    - **Validates: Requirements 6.1**

  - [ ]* 7.4 Write property test for query description inclusion
    - **Property 10: Query Description Inclusion**
    - **Validates: Requirements 6.2**

  - [ ]* 7.5 Write property test for conditional query enhancement
    - **Property 11: Conditional Query Enhancement**
    - **Validates: Requirements 6.4, 6.5**

  - [ ] 7.6 Implement generate_query_embedding method
    - Use text-embedding-004 with task_type "retrieval_query"
    - Return 768-dimensional embedding vector
    - _Requirements: 7.1_

  - [ ] 7.7 Implement search_legal_docs method
    - Call Convex searchLegalDocs query with embedding
    - Return top 3 results by default
    - Extract chunk_text, source_file, page_number from results
    - _Requirements: 7.2, 7.3, 7.4_

  - [ ]* 7.8 Write property test for search result field completeness
    - **Property 12: Search Result Field Completeness**
    - **Validates: Requirements 7.4**

  - [ ] 7.9 Implement format_legal_context method
    - Concatenate retrieved chunks with citations
    - Include source_file and page_number for each chunk
    - Use delimiters to separate chunks
    - Handle empty results gracefully
    - _Requirements: 7.6_

  - [ ]* 7.10 Write property test for legal context concatenation
    - **Property 13: Legal Context Concatenation**
    - **Validates: Requirements 7.6**

  - [ ]* 7.11 Write unit tests for RAG query engine
    - Test query generation with various invoice types
    - Test embedding generation
    - Test context formatting
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.6_

- [ ] 8. Implement AI compliance analyzer
  - [ ] 8.1 Create AIComplianceAnalyzer class in app/rag_analyzer.py
    - Initialize with Gemini API key
    - Configure gemini-2.5-flash model
    - Set response_mime_type to "application/json"
    - Set temperature to 0.1 for consistent decisions
    - _Requirements: 8.2, 13.1_

  - [ ] 8.2 Implement analyze_compliance method
    - Build structured prompt with invoice details and legal context
    - Request JSON response with status, flags, itc_eligible, reasoning
    - Parse and validate AI response structure
    - Default to "review_needed" if response is invalid or ambiguous
    - Implement error handling with fallback response
    - _Requirements: 8.1, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

  - [ ]* 8.3 Write property test for compliance status validity
    - **Property 14: Compliance Status Validity**
    - **Validates: Requirements 8.6**

  - [ ]* 8.4 Write unit tests for AI analyzer
    - Test with mock AI responses
    - Test error handling and fallback
    - Test response validation
    - _Requirements: 8.1, 8.6, 8.8, 12.1_

- [ ] 9. Create compliance auditor orchestrator
  - [ ] 9.1 Implement ComplianceAuditor class in app/compliance.py
    - Initialize with environment variables (GOOGLE_API_KEY, CONVEX_URL)
    - Create instances of HardRulesValidator, RAGQueryEngine, AIComplianceAnalyzer
    - _Requirements: 13.1, 13.2_

  - [ ] 9.2 Implement audit_invoice method
    - Step 1: Run hard rules validation
    - Step 2: Generate search query from invoice
    - Step 3: Generate query embedding
    - Step 4: Execute vector search
    - Step 5: Format legal context
    - Step 6: Run AI analysis with legal context
    - Step 7: Extract citations from search results
    - Step 8: Combine hard rules and AI flags
    - Step 9: Determine final status (most restrictive wins)
    - Step 10: Return comprehensive compliance report
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.8_

  - [ ]* 9.3 Write property test for compliance report structure
    - **Property 15: Compliance Report Structure**
    - **Validates: Requirements 9.8**

  - [ ]* 9.4 Write property test for flag aggregation completeness
    - **Property 16: Flag Aggregation Completeness**
    - **Validates: Requirements 9.1**

  - [ ]* 9.5 Write property test for status priority resolution
    - **Property 17: Status Priority Resolution**
    - **Validates: Requirements 9.3**

  - [ ]* 9.6 Write property test for citation inclusion
    - **Property 18: Citation Inclusion with Legal Context**
    - **Validates: Requirements 9.4**

  - [ ] 9.7 Implement error handling and graceful degradation
    - Catch RAG engine failures and fall back to hard rules only
    - Catch vector search failures and proceed with hard rules
    - Log all errors with timestamps and context
    - Return "review_needed" status on unexpected errors
    - _Requirements: 12.1, 12.2, 12.6, 12.7_

  - [ ] 9.8 Add backward compatibility function
    - Create audit_invoice function that wraps ComplianceAuditor
    - Maintain existing function signature for bot integration
    - _Requirements: 11.2_

  - [ ]* 9.9 Write integration tests for complete audit workflow
    - Test end-to-end flow with sample invoices
    - Test graceful degradation when RAG fails
    - Test with various invoice categories and amounts
    - _Requirements: 15.4_

- [ ] 10. Checkpoint - Verify core RAG engine functionality
  - Test compliance auditor with sample invoices
  - Verify hard rules validation works correctly
  - Verify RAG analysis retrieves relevant legal text
  - Verify error handling and fallback mechanisms
  - Ensure all tests pass, ask the user if questions arise

### Phase 3: Bot Integration and Finalization

- [ ] 11. Update invoice storage schema
  - [ ] 11.1 Add compliance fields to invoices table in convex/schema.ts
    - Add compliance_flags field (array of strings)
    - Add status field (string: compliant, review_needed, blocked)
    - Ensure telegram_id, category, and timestamp fields exist
    - Add index on telegram_id and status for querying
    - _Requirements: 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

  - [ ]* 11.2 Write property test for invoice storage completeness
    - **Property 19: Invoice Storage Completeness**
    - **Validates: Requirements 10.4, 10.5, 10.6**

- [ ] 12. Integrate RAG engine with Telegram bot
  - [ ] 12.1 Update bot.py to use ComplianceAuditor
    - Import ComplianceAuditor from app.compliance
    - Replace existing audit logic with auditor.audit_invoice() call
    - Pass extracted InvoiceData to auditor
    - _Requirements: 11.2_

  - [ ] 12.2 Format compliance report for Telegram display
    - Use ✅ indicator for "compliant" status
    - Use ⚠️ indicator for "review_needed" status
    - Use 🚫 indicator for "blocked" status
    - Display each flag on a separate line
    - Show citations with source document and page number
    - _Requirements: 11.3, 11.4, 11.5, 11.6, 11.7, 11.8_

  - [ ] 12.3 Implement invoice storage after audit
    - Save invoice to Convex invoices table
    - Include telegram_id, vendor, amount, status, category, compliance_flags, timestamp
    - Handle storage errors gracefully
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 11.9_

  - [ ] 12.4 Add error handling for bot integration
    - Handle Gemini API unavailability
    - Handle Convex operation failures
    - Display user-friendly error messages
    - Log errors for debugging
    - _Requirements: 11.10, 12.1, 12.5_

  - [ ]* 12.5 Write integration tests for bot workflow
    - Test image → extraction → audit → display flow
    - Test error handling and user messaging
    - Mock external API calls
    - _Requirements: 11.1, 11.2, 11.9, 15.5_

- [ ] 13. Implement configuration and environment management
  - [ ] 13.1 Add environment variable validation
    - Check for GOOGLE_API_KEY on startup
    - Check for CONVEX_URL on startup
    - Raise clear error messages if variables are missing
    - _Requirements: 13.1, 13.2, 13.6_

  - [ ]* 13.2 Write property test for missing environment variable detection
    - **Property 21: Missing Environment Variable Detection**
    - **Validates: Requirements 13.6**

  - [ ] 13.3 Add configurable parameters
    - Make pdfs folder path configurable
    - Make chunk size and overlap configurable
    - Make vector search result limit configurable (default 3)
    - _Requirements: 13.3, 13.4, 13.5_

  - [ ] 13.4 Update requirements.txt with new dependencies
    - Add pypdf>=3.0.0
    - Add google-generativeai>=0.3.0
    - Add hypothesis>=6.0.0 for property-based testing
    - _Requirements: 4.1, 15.5_

  - [ ] 13.5 Update package.json with TypeScript testing dependencies
    - Add fast-check to devDependencies for property-based testing
    - _Requirements: 15.3_

- [ ] 14. Implement error logging and monitoring
  - [ ] 14.1 Add structured logging throughout the system
    - Log INFO for successful operations and audit results
    - Log WARNING for fallback to hard rules and retry attempts
    - Log ERROR for API failures, database errors, unexpected exceptions
    - Include timestamps and context in all log entries
    - _Requirements: 12.6_

  - [ ]* 14.2 Write property test for error logging completeness
    - **Property 20: Error Logging Completeness**
    - **Validates: Requirements 12.6**

  - [ ]* 14.3 Write unit tests for error handling scenarios
    - Test Gemini API unavailability
    - Test vector search failures
    - Test PDF processing errors
    - Test Convex operation failures
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 15.6_

- [ ] 15. Performance optimization and testing
  - [ ] 15.1 Add query embedding caching
    - Cache embeddings for identical query strings
    - Reduce redundant API calls
    - _Requirements: 14.5_

  - [ ] 15.2 Implement batch processing for PDF ingestion
    - Process multiple chunks in parallel where possible
    - Optimize API usage during ingestion
    - _Requirements: 4.5_

  - [ ]* 15.3 Write performance tests
    - Test compliance audit completes within 10 seconds
    - Test vector search returns within 2 seconds
    - Test PDF ingestion completes within 5 minutes
    - Test concurrent request handling
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.6_

- [ ] 16. Final integration and end-to-end testing
  - [ ] 16.1 Run complete end-to-end test workflow
    - Ingest both PDF documents
    - Test bot with various invoice images
    - Verify compliance reports are accurate
    - Verify citations are included
    - Verify invoices are stored correctly
    - _Requirements: 15.4_

  - [ ] 16.2 Verify test coverage goals
    - Ensure core compliance logic has 80% coverage
    - Ensure hard rules validators have 100% coverage
    - Ensure all 21 properties are implemented as tests
    - Ensure all error paths are tested
    - _Requirements: 15.1, 15.2, 15.3, 15.7_

  - [ ] 16.3 Manual testing with real documents
    - Test with actual GST and Income Tax PDFs
    - Test with real invoice images from users
    - Verify legal text retrieval is relevant
    - Verify AI analysis is accurate
    - _Requirements: 3.7, 11.1, 11.2_

- [ ] 17. Final checkpoint - Complete system verification
  - Run full test suite (unit tests, property tests, integration tests)
  - Verify all 15 requirements are satisfied
  - Verify all 21 correctness properties are tested
  - Test error handling and graceful degradation
  - Ensure all tests pass, ask the user if questions arise

## Notes

### Task Organization
- Tasks are organized into three phases: Database & Ingestion, RAG Engine Core, and Bot Integration
- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones

### Testing Strategy
- **Property tests**: Validate universal correctness properties (minimum 100 iterations each)
- **Unit tests**: Validate specific examples, edge cases, and error conditions
- All 21 correctness properties must be implemented as property-based tests
- Each property test must include a comment tag: `# Feature: rag-compliance-engine, Property {N}: {title}`

### Technology Stack
- **Python**: Compliance logic, PDF ingestion, property tests (using `hypothesis`)
- **TypeScript**: Convex serverless functions, property tests (using `fast-check`)
- **Gemini API**: text-embedding-004 (embeddings), gemini-2.5-flash (AI analysis)
- **Convex**: Serverless database with vector search (768 dimensions)

### Implementation Phases
1. **Phase 1 (Database & Ingestion)**: Foundation for storing and searching legal documents
2. **Phase 2 (RAG Engine Core)**: Core compliance logic with hard rules and AI reasoning
3. **Phase 3 (Bot Integration)**: User-facing integration with Telegram bot

### Error Handling
- System implements graceful degradation: Full RAG → Hard Rules Only → Review Needed
- All errors are logged with timestamps and context
- External API failures trigger retry logic with exponential backoff (3 attempts)

### Performance Targets
- Complete compliance audit: < 10 seconds
- Vector search operation: < 2 seconds
- PDF ingestion (both files): < 5 minutes
- Test coverage for core logic: ≥ 80%
