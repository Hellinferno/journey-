"""
Property-Based Tests for Query Category Inclusion
Feature: rag-compliance-engine, Property 9: Query Category Inclusion
"""
from hypothesis import given, strategies as st
from app.rag_query import RAGQueryEngine
from app.schemas import InvoiceData, ExpenseCategory
from unittest.mock import patch


# Feature: rag-compliance-engine, Property 9: Query Category Inclusion
@given(
    vendor=st.text(min_size=1, max_size=100),
    amount=st.floats(min_value=0.01, max_value=1000000, allow_nan=False, allow_infinity=False),
    tax=st.floats(min_value=0.0, max_value=100000, allow_nan=False, allow_infinity=False),
    category=st.sampled_from(ExpenseCategory),
    description=st.text(min_size=1, max_size=200),
)
def test_query_always_includes_category(vendor, amount, tax, category, description):
    """
    Property 9: Query Category Inclusion
    
    For any invoice, the generated search query SHALL contain 
    the expense category value as a substring.
    
    Validates: Requirements 6.1
    """
    # Create invoice with random data
    invoice = InvoiceData(
        vendor_name=vendor,
        total_amount=amount,
        tax_amount=tax,
        category=category,
        item_description=description
    )
    
    # Create query engine (mock the API client)
    with patch('app.rag_query.genai.Client'):
        engine = RAGQueryEngine("test-api-key")
        query = engine.generate_search_query(invoice)
    
    # Property: Category value must be in the query
    assert category.value in query, \
        f"Query '{query}' does not contain category '{category.value}'"
