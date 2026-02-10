"""
Unit tests for RAG Query Engine
Tests query generation, embedding, and search functionality
"""
import pytest
from unittest.mock import Mock, patch
from app.rag_query import RAGQueryEngine
from app.schemas import InvoiceData, ExpenseCategory


class TestRAGQueryEngine:
    """Test suite for RAG Query Engine"""
    
    @pytest.fixture
    def mock_api_key(self):
        """Mock API key for testing"""
        return "test-api-key-12345"
    
    @pytest.fixture
    def query_engine(self, mock_api_key):
        """Create a RAG query engine instance"""
        with patch('app.rag_query.genai.Client'):
            engine = RAGQueryEngine(mock_api_key)
            return engine
    
    @pytest.fixture
    def sample_invoice(self):
        """Sample invoice for testing"""
        return InvoiceData(
            vendor_name="Test Vendor",
            total_amount=15000.0,
            tax_amount=2700.0,
            gstin="29ABCDE1234F1Z5",
            category=ExpenseCategory.FOOD_BEVERAGE,
            item_description="Restaurant meal for client meeting"
        )
    
    def test_generate_search_query_includes_category(self, query_engine, sample_invoice):
        """Test that search query includes expense category"""
        query = query_engine.generate_search_query(sample_invoice)
        
        assert "Food & Beverage" in query
        assert "GST compliance" in query
    
    def test_generate_search_query_includes_description(self, query_engine, sample_invoice):
        """Test that search query includes item description"""
        query = query_engine.generate_search_query(sample_invoice)
        
        assert "Restaurant meal for client meeting" in query
    
    def test_generate_search_query_includes_itc_when_gstin_present(self, query_engine, sample_invoice):
        """Test that query includes ITC eligibility when GSTIN is present"""
        query = query_engine.generate_search_query(sample_invoice)
        
        assert "input tax credit eligibility" in query
    
    def test_generate_search_query_excludes_itc_when_no_gstin(self, query_engine):
        """Test that query excludes ITC when GSTIN is not present"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=5000.0,
            category=ExpenseCategory.OFFICE_SUPPLIES,
            item_description="Office supplies"
        )
        
        query = query_engine.generate_search_query(invoice)
        
        assert "input tax credit eligibility" not in query
    
    def test_generate_search_query_includes_cash_limit_for_high_value(self, query_engine, sample_invoice):
        """Test that query includes cash payment limits for amounts > ₹10,000"""
        query = query_engine.generate_search_query(sample_invoice)
        
        assert "cash payment limits" in query
        assert "Section 40A(3)" in query
    
    def test_generate_search_query_excludes_cash_limit_for_low_value(self, query_engine):
        """Test that query excludes cash limits for amounts <= ₹10,000"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=5000.0,
            category=ExpenseCategory.OFFICE_SUPPLIES,
            item_description="Office supplies"
        )
        
        query = query_engine.generate_search_query(invoice)
        
        assert "cash payment limits" not in query
    
    def test_generate_search_query_includes_category_specific_keywords_food(self, query_engine, sample_invoice):
        """Test that query includes Section 17(5) for food & beverage"""
        query = query_engine.generate_search_query(sample_invoice)
        
        assert "Section 17(5)" in query
        assert "blocked credits" in query
    
    def test_generate_search_query_includes_category_specific_keywords_travel(self, query_engine):
        """Test that query includes travel-specific keywords"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=5000.0,
            category=ExpenseCategory.TRAVEL,
            item_description="Flight tickets"
        )
        
        query = query_engine.generate_search_query(invoice)
        
        assert "travel expense deduction rules" in query
    
    def test_generate_search_query_includes_category_specific_keywords_professional_fees(self, query_engine):
        """Test that query includes TDS requirements for professional fees"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=50000.0,
            category=ExpenseCategory.PROFESSIONAL_FEES,
            item_description="Legal consultation"
        )
        
        query = query_engine.generate_search_query(invoice)
        
        assert "professional fees TDS requirements" in query
    
    def test_format_legal_context_empty_results(self, query_engine):
        """Test that format_legal_context handles empty results gracefully"""
        context = query_engine.format_legal_context([])
        
        assert context == ""
    
    def test_format_legal_context_single_result(self, query_engine):
        """Test formatting of single search result"""
        results = [
            {
                "chunk_text": "Test legal text content",
                "source_file": "a2017-12.pdf",
                "page_number": 42
            }
        ]
        
        context = query_engine.format_legal_context(results)
        
        assert "Test legal text content" in context
        assert "a2017-12.pdf" in context
        assert "Page 42" in context
    
    def test_format_legal_context_multiple_results(self, query_engine):
        """Test formatting of multiple search results with delimiters"""
        results = [
            {
                "chunk_text": "First legal text",
                "source_file": "a2017-12.pdf",
                "page_number": 10
            },
            {
                "chunk_text": "Second legal text",
                "source_file": "Income-tax-Act-2025.pdf",
                "page_number": 25
            }
        ]
        
        context = query_engine.format_legal_context(results)
        
        assert "First legal text" in context
        assert "Second legal text" in context
        assert "a2017-12.pdf" in context
        assert "Income-tax-Act-2025.pdf" in context
        assert "---" in context  # Delimiter
    
    def test_search_legal_docs_uses_default_limit(self, query_engine):
        """Test that search uses default limit when not specified"""
        mock_convex = Mock()
        mock_convex.query.return_value = []
        
        query_engine.search_legal_docs(mock_convex, [0.1] * 768)
        
        # Verify the query was called with default limit
        mock_convex.query.assert_called_once()
        call_args = mock_convex.query.call_args[0]
        assert call_args[1]["limit"] == 3
    
    def test_search_legal_docs_uses_custom_limit(self, query_engine):
        """Test that search uses custom limit when specified"""
        mock_convex = Mock()
        mock_convex.query.return_value = []
        
        query_engine.search_legal_docs(mock_convex, [0.1] * 768, limit=5)
        
        # Verify the query was called with custom limit
        mock_convex.query.assert_called_once()
        call_args = mock_convex.query.call_args[0]
        assert call_args[1]["limit"] == 5
    
    @patch('app.rag_query.genai.Client')
    def test_generate_query_embedding_returns_768_dimensions(self, mock_client_class, mock_api_key):
        """Test that embedding generation returns 768-dimensional vector"""
        # Setup mock
        mock_client = Mock()
        mock_result = Mock()
        mock_embedding = Mock()
        mock_embedding.values = [0.1] * 768
        mock_result.embeddings = [mock_embedding]
        mock_client.models.embed_content.return_value = mock_result
        mock_client_class.return_value = mock_client
        
        engine = RAGQueryEngine(mock_api_key)
        embedding = engine.generate_query_embedding("test query")
        
        assert len(embedding) == 768
    
    @patch('app.rag_query.genai.Client')
    def test_generate_query_embedding_uses_cache(self, mock_client_class, mock_api_key):
        """Test that embedding generation uses cache for identical queries"""
        # Setup mock
        mock_client = Mock()
        mock_result = Mock()
        mock_embedding = Mock()
        mock_embedding.values = [0.1] * 768
        mock_result.embeddings = [mock_embedding]
        mock_client.models.embed_content.return_value = mock_result
        mock_client_class.return_value = mock_client
        
        engine = RAGQueryEngine(mock_api_key)
        
        # First call
        embedding1 = engine.generate_query_embedding("test query")
        
        # Second call with same query
        embedding2 = engine.generate_query_embedding("test query")
        
        # Should only call API once due to caching
        assert mock_client.models.embed_content.call_count == 1
        assert embedding1 == embedding2
