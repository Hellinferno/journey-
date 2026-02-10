"""
Property-Based Tests for Legal Context Concatenation
Feature: rag-compliance-engine, Property 13: Legal Context Concatenation
"""
from hypothesis import given, strategies as st, assume
from app.rag_query import RAGQueryEngine
from unittest.mock import patch


# Strategy for generating search results
@st.composite
def search_result(draw):
    """Generate a single search result with required fields"""
    return {
        "chunk_text": draw(st.text(min_size=1, max_size=500)),
        "source_file": draw(st.text(min_size=1, max_size=50)),
        "page_number": draw(st.integers(min_value=1, max_value=1000)),
        "category": draw(st.sampled_from(["GST", "Income_Tax"])),
    }


# Feature: rag-compliance-engine, Property 13: Legal Context Concatenation
@given(
    search_results=st.lists(search_result(), min_size=1, max_size=10)
)
def test_legal_context_contains_all_chunks(search_results):
    """
    Property 13: Legal Context Concatenation
    
    For any non-empty list of search results, the formatted legal context 
    SHALL be a single string containing all chunk_text values separated by delimiters.
    
    Validates: Requirements 7.6
    """
    # Create query engine (mock the API client)
    with patch('app.rag_query.genai.Client'):
        engine = RAGQueryEngine("test-api-key")
        context = engine.format_legal_context(search_results)
    
    # Property 1: Context must be a non-empty string
    assert isinstance(context, str), "Context must be a string"
    assert len(context) > 0, "Context must not be empty for non-empty results"
    
    # Property 2: All chunk_text values must be present in the context
    for result in search_results:
        assert result["chunk_text"] in context, \
            f"Chunk text '{result['chunk_text'][:50]}...' not found in context"
    
    # Property 3: All source citations must be present
    for result in search_results:
        assert result["source_file"] in context, \
            f"Source file '{result['source_file']}' not found in context"
        assert str(result["page_number"]) in context, \
            f"Page number {result['page_number']} not found in context"


@given(
    search_results=st.lists(search_result(), min_size=2, max_size=10)
)
def test_legal_context_uses_delimiters(search_results):
    """
    Property 13 (Extended): Legal Context Delimiter Usage
    
    For any list with multiple search results, the formatted legal context 
    SHALL use delimiters to separate chunks.
    
    Validates: Requirements 7.6
    """
    # Filter out results where source_file contains the delimiter
    # (edge case that would cause false positives)
    delimiter = "\n---\n"
    filtered_results = [r for r in search_results if delimiter not in r["source_file"]]
    
    # Skip if we don't have at least 2 results after filtering
    assume(len(filtered_results) >= 2)
    
    # Create query engine (mock the API client)
    with patch('app.rag_query.genai.Client'):
        engine = RAGQueryEngine("test-api-key")
        context = engine.format_legal_context(filtered_results)
    
    # Property: Delimiter must be present for multiple results
    delimiter_count = context.count(delimiter)
    
    # Should have (n-1) delimiters for n results
    expected_delimiters = len(filtered_results) - 1
    assert delimiter_count == expected_delimiters, \
        f"Expected {expected_delimiters} delimiters, found {delimiter_count}"


def test_legal_context_empty_results():
    """
    Property 13 (Edge Case): Empty Results Handling
    
    For an empty list of search results, the formatted legal context 
    SHALL return an empty string.
    
    Validates: Requirements 7.6
    """
    # Create query engine (mock the API client)
    with patch('app.rag_query.genai.Client'):
        engine = RAGQueryEngine("test-api-key")
        context = engine.format_legal_context([])
    
    # Property: Empty results should return empty string
    assert context == "", "Empty results should return empty string"


@given(
    search_results=st.lists(search_result(), min_size=1, max_size=5)
)
def test_legal_context_preserves_order(search_results):
    """
    Property 13 (Extended): Order Preservation
    
    For any list of search results, the formatted legal context 
    SHALL preserve the order of chunks as they appear in the input list.
    
    Validates: Requirements 7.6
    """
    # Create query engine (mock the API client)
    with patch('app.rag_query.genai.Client'):
        engine = RAGQueryEngine("test-api-key")
        context = engine.format_legal_context(search_results)
    
    # Property: Chunks should appear in the same order
    # We'll verify by checking that each chunk appears after the previous one
    # For duplicate chunks, we track the last found position
    last_position = -1
    for i, result in enumerate(search_results):
        # Find the chunk starting from the last position
        position = context.find(result["chunk_text"], last_position + 1)
        assert position != -1, \
            f"Chunk {i} text '{result['chunk_text'][:30]}...' not found in context after position {last_position}"
        assert position > last_position, \
            f"Chunk order not preserved: chunk {i} '{result['chunk_text'][:30]}...' appears at position {position}, expected > {last_position}"
        last_position = position
