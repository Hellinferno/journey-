"""
Unit tests for PDF Ingestion Pipeline
Tests PDF processing, error handling, and retry logic
"""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pypdf import PdfReader, PdfWriter
from io import BytesIO

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scripts.ingest_pdfs import PDFIngestionPipeline


class TestPDFProcessing:
    """Test PDF file processing functionality"""
    
    @pytest.fixture
    def pipeline(self):
        """Create a pipeline instance with mock credentials"""
        with patch('scripts.ingest_pdfs.ConvexClient'):
            with patch('scripts.ingest_pdfs.genai.Client'):
                pipeline = PDFIngestionPipeline(
                    convex_url="https://test.convex.cloud",
                    api_key="test_api_key"
                )
                return pipeline
    
    @pytest.fixture
    def sample_pdf(self):
        """Create a simple sample PDF for testing"""
        # Create a PDF with some text content
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, "Sample Invoice")
        c.drawString(100, 730, "Vendor: Test Company")
        c.drawString(100, 710, "Amount: Rs. 10,000")
        c.drawString(100, 690, "GSTIN: 29ABCDE1234F1Z5")
        c.showPage()
        c.save()
        
        buffer.seek(0)
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
            f.write(buffer.read())
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_process_pdf_with_valid_file(self, pipeline, sample_pdf):
        """Test processing a valid PDF file"""
        chunks = pipeline.process_pdf(sample_pdf, "GST")
        
        # Should create at least one chunk
        assert len(chunks) > 0
        
        # Each chunk should have required fields
        for chunk in chunks:
            assert "text" in chunk
            assert "page_number" in chunk
            assert isinstance(chunk["text"], str)
            assert isinstance(chunk["page_number"], int)
            assert chunk["page_number"] >= 1
    
    def test_process_pdf_extracts_text_content(self, pipeline, sample_pdf):
        """Test that PDF text extraction works correctly"""
        chunks = pipeline.process_pdf(sample_pdf, "GST")
        
        # Combine all chunk text
        all_text = " ".join(chunk["text"] for chunk in chunks)
        
        # Should contain expected content
        assert "Sample Invoice" in all_text or "Invoice" in all_text
    
    def test_process_pdf_preserves_page_numbers(self, pipeline, sample_pdf):
        """Test that page numbers are correctly preserved"""
        chunks = pipeline.process_pdf(sample_pdf, "GST")
        
        # All chunks from this single-page PDF should have page_number = 1
        for chunk in chunks:
            assert chunk["page_number"] == 1


class TestCorruptedPDFHandling:
    """Test error handling for corrupted or invalid PDF files"""
    
    @pytest.fixture
    def pipeline(self):
        """Create a pipeline instance with mock credentials"""
        with patch('scripts.ingest_pdfs.ConvexClient'):
            with patch('scripts.ingest_pdfs.genai.Client'):
                pipeline = PDFIngestionPipeline(
                    convex_url="https://test.convex.cloud",
                    api_key="test_api_key"
                )
                return pipeline
    
    @pytest.fixture
    def corrupted_pdf(self):
        """Create a corrupted PDF file"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
            # Write invalid PDF content
            f.write(b"This is not a valid PDF file content")
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    @pytest.fixture
    def empty_pdf(self):
        """Create an empty PDF file"""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_process_corrupted_pdf_raises_error(self, pipeline, corrupted_pdf):
        """Test that corrupted PDF raises appropriate error"""
        with pytest.raises(Exception):
            pipeline.process_pdf(corrupted_pdf, "GST")
    
    def test_process_nonexistent_pdf_raises_error(self, pipeline):
        """Test that non-existent PDF raises appropriate error"""
        with pytest.raises(FileNotFoundError):
            pipeline.process_pdf("/nonexistent/path/file.pdf", "GST")
    
    def test_process_empty_pdf_handles_gracefully(self, pipeline, empty_pdf):
        """Test that empty PDF is handled gracefully"""
        # Empty PDF should either raise error or return empty chunks
        try:
            chunks = pipeline.process_pdf(empty_pdf, "GST")
            assert isinstance(chunks, list)
        except Exception:
            # It's acceptable to raise an error for empty PDFs
            pass


class TestRetryLogic:
    """Test retry logic for API failures"""
    
    @pytest.fixture
    def pipeline(self):
        """Create a pipeline instance with mock credentials"""
        with patch('scripts.ingest_pdfs.ConvexClient'):
            mock_client = MagicMock()
            with patch('scripts.ingest_pdfs.genai.Client', return_value=mock_client):
                pipeline = PDFIngestionPipeline(
                    convex_url="https://test.convex.cloud",
                    api_key="test_api_key"
                )
                return pipeline
    
    def test_generate_embedding_retries_on_failure(self, pipeline):
        """Test that embedding generation retries on API failure"""
        # Mock the embed_content to fail twice then succeed
        mock_embedding = Mock()
        mock_embedding.values = [0.1] * 768
        
        mock_result = Mock()
        mock_result.embeddings = [mock_embedding]
        
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("API temporarily unavailable")
            return mock_result
        
        pipeline.client.models.embed_content = Mock(side_effect=side_effect)
        
        # Should succeed after retries
        embedding = pipeline.generate_embedding("test text", retries=3)
        
        assert len(embedding) == 768
        assert call_count == 3  # Failed twice, succeeded on third attempt
    
    def test_generate_embedding_fails_after_max_retries(self, pipeline):
        """Test that embedding generation fails after exhausting retries"""
        # Mock the embed_content to always fail
        pipeline.client.models.embed_content = Mock(
            side_effect=Exception("API unavailable")
        )
        
        # Should raise exception after max retries
        with pytest.raises(Exception, match="API unavailable"):
            pipeline.generate_embedding("test text", retries=3)
    
    def test_generate_embedding_exponential_backoff(self, pipeline):
        """Test that retry logic uses exponential backoff"""
        mock_embedding = Mock()
        mock_embedding.values = [0.1] * 768
        
        mock_result = Mock()
        mock_result.embeddings = [mock_embedding]
        
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("API temporarily unavailable")
            return mock_result
        
        pipeline.client.models.embed_content = Mock(side_effect=side_effect)
        
        # Patch time.sleep to verify exponential backoff
        with patch('scripts.ingest_pdfs.time.sleep') as mock_sleep:
            embedding = pipeline.generate_embedding("test text", retries=3)
            
            # Should have called sleep with exponential backoff (2^0 = 1 second)
            assert mock_sleep.call_count == 1
            mock_sleep.assert_called_with(1)  # 2^0 = 1
    
    def test_generate_embedding_success_on_first_try(self, pipeline):
        """Test that successful API call doesn't retry"""
        mock_embedding = Mock()
        mock_embedding.values = [0.1] * 768
        
        mock_result = Mock()
        mock_result.embeddings = [mock_embedding]
        
        pipeline.client.models.embed_content = Mock(return_value=mock_result)
        
        embedding = pipeline.generate_embedding("test text", retries=3)
        
        assert len(embedding) == 768
        assert pipeline.client.models.embed_content.call_count == 1


class TestIngestDocumentWorkflow:
    """Test the complete document ingestion workflow"""
    
    @pytest.fixture
    def pipeline(self):
        """Create a pipeline instance with mocked dependencies"""
        mock_convex = Mock()
        mock_client = MagicMock()
        
        with patch('scripts.ingest_pdfs.ConvexClient', return_value=mock_convex):
            with patch('scripts.ingest_pdfs.genai.Client', return_value=mock_client):
                pipeline = PDFIngestionPipeline(
                    convex_url="https://test.convex.cloud",
                    api_key="test_api_key"
                )
                return pipeline
    
    @pytest.fixture
    def sample_pdf(self):
        """Create a simple sample PDF for testing"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, "Test Document")
        c.showPage()
        c.save()
        
        buffer.seek(0)
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.pdf', delete=False) as f:
            f.write(buffer.read())
            temp_path = f.name
        
        yield temp_path
        
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    def test_ingest_document_processes_and_stores_chunks(self, pipeline, sample_pdf):
        """Test that ingest_document processes PDF and stores chunks"""
        # Mock embedding generation
        mock_embedding = Mock()
        mock_embedding.values = [0.1] * 768
        mock_result = Mock()
        mock_result.embeddings = [mock_embedding]
        pipeline.client.models.embed_content = Mock(return_value=mock_result)
        
        # Mock Convex mutation
        pipeline.convex.mutation = Mock()
        
        # Run ingestion
        pipeline.ingest_document(sample_pdf, "GST")
        
        # Should have called mutation at least once
        assert pipeline.convex.mutation.call_count > 0
        
        # Verify mutation was called with correct structure
        call_args = pipeline.convex.mutation.call_args
        assert call_args[0][0] == "legalDocs:addLegalDocument"
        
        # Verify data structure (second argument is the data dict)
        data = call_args[0][1]
        assert "chunk_text" in data
        assert "source_file" in data
        assert "page_number" in data
        assert "category" in data
        assert "embedding" in data
        assert data["category"] == "GST"
    
    def test_ingest_document_handles_chunk_errors_gracefully(self, pipeline, sample_pdf):
        """Test that errors in individual chunks don't stop the entire process"""
        # Mock embedding to fail for some chunks
        call_count = 0
        def embed_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Embedding failed")
            mock_embedding = Mock()
            mock_embedding.values = [0.1] * 768
            mock_result = Mock()
            mock_result.embeddings = [mock_embedding]
            return mock_result
        
        pipeline.client.models.embed_content = Mock(side_effect=embed_side_effect)
        pipeline.convex.mutation = Mock()
        
        # Should complete without raising exception
        pipeline.ingest_document(sample_pdf, "GST")
        
        # Should have attempted multiple chunks
        assert call_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
