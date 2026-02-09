"""
Property-based tests for PDF text chunking
Feature: rag-compliance-engine
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hypothesis import given, strategies as st, settings
from scripts.ingest_pdfs import PDFIngestionPipeline


# Feature: rag-compliance-engine, Property 3: Text Chunking Overlap Preservation
@given(
    text=st.text(min_size=1001, max_size=10000)  # Text longer than 1000 characters
)
@settings(max_examples=20, deadline=None)  # Disable deadline for slower tests
def test_text_chunking_overlap_preservation(text):
    """
    Property 3: Text Chunking Overlap Preservation
    
    For any text longer than 1000 characters, consecutive chunks SHALL have 
    exactly 100 characters of overlap, where the last 100 characters of chunk N 
    equal the first 100 characters of chunk N+1.
    
    Validates: Requirements 3.3
    """
    # Create a pipeline instance (we don't need real API keys for chunking)
    pipeline = PDFIngestionPipeline(
        convex_url="https://dummy.convex.cloud",
        api_key="dummy_key"
    )
    
    # Chunk the text
    chunks = pipeline.chunk_text(text, page_num=1)
    
    # If we have multiple chunks, verify overlap
    if len(chunks) >= 2:
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]["text"]
            next_chunk = chunks[i + 1]["text"]
            
            # Calculate the expected overlap
            # The overlap should be 100 characters, but if the next chunk is shorter than 100,
            # then the overlap is limited by the length of the next chunk
            expected_overlap_size = min(100, len(next_chunk))
            
            # Get the last expected_overlap_size characters of current chunk
            last_n_current = current_chunk[-expected_overlap_size:]
            
            # Get the first expected_overlap_size characters of next chunk
            first_n_next = next_chunk[:expected_overlap_size]
            
            # They should be equal (overlap preservation)
            assert last_n_current == first_n_next, (
                f"Overlap mismatch between chunk {i} and {i+1}:\n"
                f"Chunk {i} length: {len(current_chunk)}\n"
                f"Chunk {i+1} length: {len(next_chunk)}\n"
                f"Expected overlap size: {expected_overlap_size}\n"
                f"Last {expected_overlap_size} of chunk {i}: {repr(last_n_current[:50])}...\n"
                f"First {expected_overlap_size} of chunk {i+1}: {repr(first_n_next[:50])}..."
            )


if __name__ == "__main__":
    # Run the test manually
    import pytest
    pytest.main([__file__, "-v"])
