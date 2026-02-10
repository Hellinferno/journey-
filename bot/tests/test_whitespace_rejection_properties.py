"""
Property-based tests for whitespace chunk rejection
Feature: rag-compliance-engine
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hypothesis import given, strategies as st, settings
from scripts.ingest_pdfs import PDFIngestionPipeline


# Feature: rag-compliance-engine, Property 5: Whitespace Chunk Rejection
@given(
    whitespace_text=st.text(
        alphabet=st.characters(whitelist_categories=('Zs', 'Cc')),  # Whitespace and control characters
        min_size=1,
        max_size=2000
    )
)
@settings(max_examples=100, deadline=None)
def test_whitespace_chunk_rejection(whitespace_text):
    """
    Property 5: Whitespace Chunk Rejection
    
    For any text chunk that contains only whitespace characters (spaces, tabs, 
    newlines), the system SHALL skip storing that chunk in the database.
    
    Validates: Requirements 3.6
    """
    # Create a pipeline instance (we don't need real API keys for chunking)
    pipeline = PDFIngestionPipeline(
        convex_url="https://dummy.convex.cloud",
        api_key="dummy_key"
    )
    
    # Chunk the whitespace-only text
    chunks = pipeline.chunk_text(whitespace_text, page_num=1)
    
    # Property: No chunks should be returned for whitespace-only text
    assert len(chunks) == 0, (
        f"Expected 0 chunks for whitespace-only text, but got {len(chunks)} chunks.\n"
        f"Input text length: {len(whitespace_text)}\n"
        f"Input text repr: {repr(whitespace_text[:100])}...\n"
        f"Chunks returned: {chunks}"
    )


# Feature: rag-compliance-engine, Property 5: Whitespace Chunk Rejection (Mixed Content)
@given(
    text_parts=st.lists(
        st.one_of(
            st.text(min_size=1, max_size=500),  # Regular text
            st.text(
                alphabet=st.characters(whitelist_categories=('Zs', 'Cc')),
                min_size=1,
                max_size=500
            )  # Whitespace-only text
        ),
        min_size=1,
        max_size=10
    )
)
@settings(max_examples=100, deadline=None)
def test_whitespace_chunk_rejection_mixed_content(text_parts):
    """
    Property 5: Whitespace Chunk Rejection (Mixed Content Variant)
    
    For any text containing a mix of content and whitespace-only sections,
    only chunks with non-whitespace content SHALL be included.
    
    Validates: Requirements 3.6
    """
    # Create a pipeline instance
    pipeline = PDFIngestionPipeline(
        convex_url="https://dummy.convex.cloud",
        api_key="dummy_key"
    )
    
    # Combine text parts
    combined_text = "".join(text_parts)
    
    # Chunk the text
    chunks = pipeline.chunk_text(combined_text, page_num=1)
    
    # Property: All returned chunks must have non-whitespace content
    for i, chunk in enumerate(chunks):
        chunk_text = chunk["text"]
        assert chunk_text.strip() != "", (
            f"Chunk {i} contains only whitespace but was not rejected.\n"
            f"Chunk text length: {len(chunk_text)}\n"
            f"Chunk text repr: {repr(chunk_text[:100])}..."
        )


if __name__ == "__main__":
    # Run the test manually
    import pytest
    pytest.main([__file__, "-v"])
