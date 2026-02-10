"""
Property-Based Tests for Search Result Field Completeness
Feature: rag-compliance-engine, Property 12: Search Result Field Completeness
"""
from hypothesis import given, strategies as st
from app.rag_query import RAGQueryEngine
from unittest.mock import Mock, patch


# Feature: rag-compliance-engine, Property 12: Search Result Field Completeness
@given(
    num_results=st.integers(min_value=1, max_value=10),
    chunk_texts=st.lists(st.text(min_size=10, max_size=500), min_size=1, max_size=10),
    source_files=st.lists(st.sampled_from(["a2017-12.pdf", "Income-tax-Act-2025.pdf"]), min_size=1, max_size=10),
    page_numbers=st.lists(st.integers(min_value=1, max_value=500), min_size=1, max_size=10),
    categories=st.lists(st.sampled_from(["GST", "Income_Tax"]), min_size=1, max_size=10),
)
def test_search_results_have_all_required_fields(num_results, chunk_texts, source_files, page_numbers, categories):
    """
    Property 12: Search Result Field Completeness
    
    For any document returned by vector search, the result SHALL contain 
    all required fields: chunk_text, source_file, page_number, and category.
    
    Validates: Requirements 7.4
    """
    # Ensure all lists have the same length
    min_len = min(len(chunk_texts), len(source_files), len(page_numbers), len(categories))
    num_results = min(num_results, min_len)
    
    # Create mock search results
    mock_results = []
    for i in range(num_results):
        mock_results.append({
            "chunk_text": chunk_texts[i],
            "source_file": source_files[i],
            "page_number": page_numbers[i],
            "category": categories[i],
            "score": 0.9 - (i * 0.1)  # Decreasing scores
        })
    
    # Create query engine and mock Convex client
    with patch('app.rag_query.genai.Client'):
        engine = RAGQueryEngine("test-api-key")
        
        mock_convex = Mock()
        mock_convex.query.return_value = mock_results
        
        # Execute search
        results = engine.search_legal_docs(mock_convex, [0.1] * 768)
    
    # Property: All results must have required fields
    for i, result in enumerate(results):
        assert "chunk_text" in result, \
            f"Result {i} missing 'chunk_text' field"
        assert "source_file" in result, \
            f"Result {i} missing 'source_file' field"
        assert "page_number" in result, \
            f"Result {i} missing 'page_number' field"
        assert "category" in result, \
            f"Result {i} missing 'category' field"
        
        # Verify field types
        assert isinstance(result["chunk_text"], str), \
            f"Result {i} 'chunk_text' is not a string"
        assert isinstance(result["source_file"], str), \
            f"Result {i} 'source_file' is not a string"
        assert isinstance(result["page_number"], int), \
            f"Result {i} 'page_number' is not an integer"
        assert isinstance(result["category"], str), \
            f"Result {i} 'category' is not a string"
