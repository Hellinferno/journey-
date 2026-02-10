"""
Property-based tests for page number metadata preservation
Feature: rag-compliance-engine
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hypothesis import given, strategies as st, settings
from scripts.ingest_pdfs import PDFIngestionPipeline


# Feature: rag-compliance-engine, Property 4: Page Number Metadata Preservation
@given(
    text=st.text(min_size=1, max_size=10000),
    page_num=st.integers(min_value=1, max_value=1000)
)
@settings(max_examples=100, deadline=None)
def test_page_number_metadata_preservation(text, page_num):
    """
    Property 4: Page Number Metadata Preservation
    
    For any chunk created from a PDF, the chunk SHALL contain the page_number 
    field matching the source page from which the text was extracted.
    
    Validates: Requirements 3.4
    """
    # Create a pipeline instance (we don't need real API keys for chunking)
    pipeline = PDFIngestionPipeline(
        convex_url="https://dummy.convex.cloud",
        api_key="dummy_key"
    )
    
    # Chunk the text with the given page number
    chunks = pipeline.chunk_text(text, page_num=page_num)
    
    # Verify that all chunks have the correct page number
    for i, chunk in enumerate(chunks):
        assert "page_number" in chunk, (
            f"Chunk {i} is missing 'page_number' field"
        )
        
        assert chunk["page_number"] == page_num, (
            f"Chunk {i} has incorrect page number:\n"
            f"Expected: {page_num}\n"
            f"Got: {chunk['page_number']}"
        )


if __name__ == "__main__":
    # Run the test manually
    import pytest
    pytest.main([__file__, "-v"])
