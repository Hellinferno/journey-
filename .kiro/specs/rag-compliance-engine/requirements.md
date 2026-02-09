# Requirements Document

## Introduction

The RAG Compliance Engine enhances the Micro-CFO Telegram bot with intelligent legal compliance checking powered by Retrieval-Augmented Generation (RAG). The system ingests official GST and Income Tax PDF documents, stores them as vector embeddings in Convex, and uses semantic search to retrieve relevant legal text when auditing invoices. This enables the bot to provide accurate, context-aware compliance guidance based on actual tax law rather than hard-coded rules.

## Glossary

- **RAG_Engine**: The Retrieval-Augmented Generation system that combines vector search with AI reasoning
- **Legal_Docs_Table**: Convex database table storing PDF chunks with vector embeddings
- **Vector_Index**: 768-dimensional vector index for semantic similarity search
- **PDF_Ingestion_Script**: Python script that processes PDFs and stores chunks in Convex
- **Compliance_Auditor**: Component that orchestrates hard rules validation and RAG-based analysis
- **Hard_Rules_Validator**: Component that checks GSTIN format, tax rates, and cash limits
- **Gemini_API**: Google's AI service used for embeddings (text-embedding-004) and analysis (gemini-2.5-flash)
- **Convex_Functions**: TypeScript serverless functions for database operations
- **Invoice_Data**: Structured data extracted from invoice images
- **Compliance_Status**: Enum with values: compliant, review_needed, blocked
- **ITC**: Input Tax Credit - tax credit businesses can claim on purchases
- **GSTIN**: Goods and Services Tax Identification Number (15-character format)
- **Section_40A3**: Income Tax Act provision limiting cash transactions to ₹10,000
- **Section_17_5**: GST Act provision blocking ITC on certain expense categories

## Requirements

### Requirement 1: Legal Documents Database Schema

**User Story:** As a system architect, I want a dedicated database table for legal document chunks with vector search capabilities, so that the RAG engine can efficiently retrieve relevant legal text.

#### Acceptance Criteria

1. THE Legal_Docs_Table SHALL store document chunks with fields: chunk_text, source_file, page_number, category, and embedding
2. THE Legal_Docs_Table SHALL use a vector index with 768 dimensions for the embedding field
3. THE Vector_Index SHALL support similarity search operations
4. WHEN the schema is deployed, THEN the Legal_Docs_Table SHALL be accessible via Convex functions
5. THE Legal_Docs_Table SHALL support metadata filtering by source_file and category

### Requirement 2: Convex Vector Search Functions

**User Story:** As a developer, I want Convex functions for adding documents and performing vector search, so that the RAG engine can store and retrieve legal text efficiently.

#### Acceptance Criteria

1. THE Convex_Functions SHALL include an addLegalDocument mutation that accepts chunk_text, source_file, page_number, category, and embedding
2. THE Convex_Functions SHALL include a searchLegalDocs query that accepts a query_embedding and returns top K similar documents
3. WHEN searchLegalDocs is called, THEN it SHALL return documents ordered by similarity score (highest first)
4. THE searchLegalDocs query SHALL accept an optional limit parameter with default value of 3
5. THE addLegalDocument mutation SHALL validate that embedding has exactly 768 dimensions
6. WHEN a document is added, THEN the system SHALL store the embedding in the Vector_Index

### Requirement 3: PDF Ingestion and Chunking

**User Story:** As a system administrator, I want to ingest PDF documents and store them as searchable chunks, so that the RAG engine has access to official legal text.

#### Acceptance Criteria

1. THE PDF_Ingestion_Script SHALL read PDF files from a designated pdfs folder
2. WHEN processing a PDF, THEN the system SHALL extract text content page by page
3. THE PDF_Ingestion_Script SHALL chunk text into segments of 1000 characters with 100 character overlap
4. WHEN creating chunks, THEN the system SHALL preserve page number metadata for each chunk
5. THE PDF_Ingestion_Script SHALL categorize chunks as "GST" for a2017-12.pdf and "Income_Tax" for Income-tax-Act-2025.pdf
6. WHEN a chunk is empty or contains only whitespace, THEN the system SHALL skip that chunk
7. THE PDF_Ingestion_Script SHALL process both a2017-12.pdf and Income-tax-Act-2025.pdf

### Requirement 4: Vector Embedding Generation

**User Story:** As a developer, I want to generate vector embeddings for text chunks using Google's embedding model, so that semantic search can find relevant legal text.

#### Acceptance Criteria

1. THE PDF_Ingestion_Script SHALL use Google's text-embedding-004 model for generating embeddings
2. WHEN generating an embedding, THEN the system SHALL pass the chunk text to the Gemini_API
3. THE Gemini_API SHALL return a 768-dimensional vector for each text chunk
4. WHEN an API call fails, THEN the system SHALL retry up to 3 times with exponential backoff
5. THE PDF_Ingestion_Script SHALL batch process chunks to optimize API usage
6. WHEN all chunks are processed, THEN the system SHALL store embeddings in the Legal_Docs_Table via Convex_Functions

### Requirement 5: Hard Rules Validation

**User Story:** As a compliance officer, I want the system to validate basic compliance rules before RAG analysis, so that obvious violations are caught immediately.

#### Acceptance Criteria

1. WHEN validating GSTIN, THEN the Hard_Rules_Validator SHALL check for exactly 15 characters matching the pattern [0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}
2. WHEN validating GST rates, THEN the Hard_Rules_Validator SHALL verify tax_amount corresponds to standard rates (5%, 12%, 18%, or 28%)
3. WHEN total_amount exceeds ₹10,000 and payment method is cash, THEN the Hard_Rules_Validator SHALL flag a Section_40A3 violation
4. WHEN category is FOOD_BEVERAGE, THEN the Hard_Rules_Validator SHALL flag blocked ITC under Section_17_5
5. WHEN any hard rule fails, THEN the system SHALL add a descriptive flag to the compliance report
6. THE Hard_Rules_Validator SHALL return a list of violation flags and a preliminary status

### Requirement 6: RAG Query Generation

**User Story:** As a developer, I want the system to generate intelligent search queries based on invoice data, so that vector search retrieves the most relevant legal sections.

#### Acceptance Criteria

1. WHEN generating a search query, THEN the RAG_Engine SHALL include the expense category in the query text
2. WHEN generating a search query, THEN the RAG_Engine SHALL include the item description in the query text
3. THE RAG_Engine SHALL construct queries in the format: "GST compliance for {category}: {item_description}"
4. WHEN the invoice has a GSTIN, THEN the query SHALL include "input tax credit eligibility"
5. WHEN total_amount exceeds ₹10,000, THEN the query SHALL include "cash payment limits"
6. THE RAG_Engine SHALL generate a single consolidated query string for vector search

### Requirement 7: Vector Search Execution

**User Story:** As a developer, I want to perform vector search on legal documents using invoice-based queries, so that the most relevant legal text is retrieved for compliance analysis.

#### Acceptance Criteria

1. WHEN executing vector search, THEN the RAG_Engine SHALL generate an embedding for the search query using text-embedding-004
2. THE RAG_Engine SHALL call the searchLegalDocs Convex function with the query embedding
3. WHEN search results are returned, THEN the system SHALL retrieve the top 3 most similar legal document chunks
4. THE RAG_Engine SHALL extract chunk_text, source_file, and page_number from each result
5. WHEN no results are found, THEN the system SHALL proceed with hard rules validation only
6. THE RAG_Engine SHALL concatenate retrieved chunks into a single legal context string

### Requirement 8: AI-Powered Compliance Analysis

**User Story:** As a compliance officer, I want the system to use AI reasoning with retrieved legal context to determine invoice compliance, so that decisions are based on actual tax law.

#### Acceptance Criteria

1. WHEN performing compliance analysis, THEN the RAG_Engine SHALL send Invoice_Data and retrieved legal context to Gemini_API
2. THE RAG_Engine SHALL use the gemini-2.5-flash model for compliance reasoning
3. THE Gemini_API SHALL receive a structured prompt containing invoice details and legal text
4. WHEN analyzing compliance, THEN the AI SHALL determine if the expense is eligible for ITC
5. WHEN analyzing compliance, THEN the AI SHALL identify any tax law violations
6. THE Gemini_API SHALL return a Compliance_Status (compliant, review_needed, or blocked)
7. THE Gemini_API SHALL return a list of specific compliance flags with explanations
8. WHEN the AI response is ambiguous, THEN the system SHALL default to review_needed status

### Requirement 9: Compliance Report Generation

**User Story:** As a user, I want to receive a comprehensive compliance report for my invoice, so that I understand any tax implications or violations.

#### Acceptance Criteria

1. THE Compliance_Auditor SHALL combine hard rules flags and RAG analysis flags into a single report
2. WHEN generating a report, THEN the system SHALL include the final Compliance_Status
3. THE report SHALL list all compliance flags in priority order (blocked > review_needed > compliant)
4. WHEN legal text was used, THEN the report SHALL include citations with source_file and page_number
5. THE report SHALL include the expense category for context
6. WHEN status is blocked, THEN the report SHALL clearly indicate the expense cannot be claimed
7. WHEN status is review_needed, THEN the report SHALL suggest consulting a CA
8. THE report SHALL be formatted as a structured dictionary with keys: status, flags, category, citations

### Requirement 10: Invoice Storage with Compliance Data

**User Story:** As a system administrator, I want invoices to be stored with their compliance analysis results, so that users can review historical compliance decisions.

#### Acceptance Criteria

1. WHEN an invoice is audited, THEN the system SHALL store the Invoice_Data in the invoices table
2. THE invoices table SHALL include a compliance_flags field storing the list of flags
3. THE invoices table SHALL include a status field storing the Compliance_Status
4. WHEN storing an invoice, THEN the system SHALL include the telegram_id for user association
5. THE system SHALL store the expense category with each invoice
6. WHEN an invoice is stored, THEN the system SHALL generate a timestamp
7. THE invoices table SHALL support querying by telegram_id and status

### Requirement 11: Telegram Bot Integration

**User Story:** As a user, I want to send invoice images to the Telegram bot and receive compliance analysis, so that I can understand tax implications immediately.

#### Acceptance Criteria

1. WHEN a user sends an image, THEN the bot SHALL extract Invoice_Data using Gemini_API
2. WHEN extraction is complete, THEN the bot SHALL call the Compliance_Auditor with the Invoice_Data
3. THE bot SHALL display the compliance report to the user in a readable format
4. WHEN status is compliant, THEN the bot SHALL use a ✅ indicator
5. WHEN status is review_needed, THEN the bot SHALL use a ⚠️ indicator
6. WHEN status is blocked, THEN the bot SHALL use a 🚫 indicator
7. THE bot SHALL display each compliance flag on a separate line
8. WHEN citations are available, THEN the bot SHALL show the source document and page number
9. WHEN the audit is complete, THEN the bot SHALL save the invoice to Convex
10. THE bot SHALL handle API errors gracefully and inform the user of any issues

### Requirement 12: Error Handling and Resilience

**User Story:** As a system administrator, I want the RAG engine to handle errors gracefully, so that the system remains operational even when external services fail.

#### Acceptance Criteria

1. WHEN the Gemini_API is unavailable, THEN the system SHALL fall back to hard rules validation only
2. WHEN vector search fails, THEN the system SHALL proceed with hard rules validation and log the error
3. WHEN PDF ingestion fails for a file, THEN the system SHALL log the error and continue with other files
4. WHEN embedding generation fails, THEN the system SHALL retry up to 3 times before skipping the chunk
5. WHEN Convex operations fail, THEN the system SHALL return an error message to the user
6. THE system SHALL log all errors with timestamps and context for debugging
7. WHEN an unexpected error occurs during compliance analysis, THEN the system SHALL return status review_needed with a generic flag

### Requirement 13: Configuration and Environment Management

**User Story:** As a developer, I want centralized configuration for API keys and settings, so that the system can be deployed across different environments.

#### Acceptance Criteria

1. THE system SHALL read the Gemini API key from environment variable GOOGLE_API_KEY
2. THE system SHALL read the Convex deployment URL from environment variable CONVEX_URL
3. THE PDF_Ingestion_Script SHALL accept a configurable pdfs folder path
4. THE system SHALL support configurable chunk size and overlap parameters
5. THE system SHALL support configurable vector search result limit (default 3)
6. WHEN required environment variables are missing, THEN the system SHALL raise a clear error message
7. THE system SHALL validate API keys on startup before processing requests

### Requirement 14: Performance and Scalability

**User Story:** As a system administrator, I want the RAG engine to process invoices efficiently, so that users receive timely responses.

#### Acceptance Criteria

1. WHEN processing an invoice, THEN the complete compliance audit SHALL complete within 10 seconds
2. THE vector search operation SHALL return results within 2 seconds
3. THE PDF_Ingestion_Script SHALL process both PDF files within 5 minutes
4. WHEN multiple users submit invoices simultaneously, THEN the system SHALL handle concurrent requests without degradation
5. THE system SHALL cache embeddings for identical query strings to reduce API calls
6. WHEN the Legal_Docs_Table exceeds 10,000 chunks, THEN vector search SHALL maintain sub-2-second response times

### Requirement 15: Testing and Validation

**User Story:** As a developer, I want comprehensive tests for the RAG engine, so that I can verify correctness and catch regressions.

#### Acceptance Criteria

1. THE system SHALL include unit tests for hard rules validation functions
2. THE system SHALL include integration tests for PDF ingestion and storage
3. THE system SHALL include tests for vector search with known queries and expected results
4. THE system SHALL include end-to-end tests simulating the complete invoice audit flow
5. WHEN running tests, THEN the system SHALL use mock data for external API calls
6. THE system SHALL include tests for error handling and fallback scenarios
7. THE test suite SHALL achieve at least 80% code coverage for core compliance logic
