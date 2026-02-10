"""
Property-Based Tests for Conditional Query Enhancement
Feature: rag-compliance-engine, Property 11: Conditional Query Enhancement
"""
from hypothesis import given, strategies as st, assume
from app.rag_query import RAGQueryEngine
from app.schemas import InvoiceData, ExpenseCategory
from unittest.mock import patch


# Feature: rag-compliance-engine, Property 11: Conditional Query Enhancement
@given(
    vendor=st.text(min_size=1, max_size=100),
    amount=st.floats(min_value=0.01, max_value=1000000, allow_nan=False, allow_infinity=False),
    tax=st.floats(min_value=0.0, max_value=100000, allow_nan=False, allow_infinity=False),
    category=st.sampled_from(ExpenseCategory),
    description=st.text(min_size=1, max_size=200),
    has_gstin=st.booleans(),
)
def test_query_includes_itc_when_gstin_present(vendor, amount, tax, category, description, has_gstin):
    """
    Property 11: Conditional Query Enhancement (Part 1 - GSTIN)
    
    For any invoice with a non-null GSTIN, the generated search query 
    SHALL include "input tax credit eligibility".
    
    Validates: Requirements 6.4
    """
    # Create invoice with or without GSTIN
    gstin = "29ABCDE1234F1Z5" if has_gstin else None
    
    invoice = InvoiceData(
        vendor_name=vendor,
        total_amount=amount,
        tax_amount=tax,
        gstin=gstin,
        category=category,
        item_description=description
    )
    
    # Create query engine (mock the API client)
    with patch('app.rag_query.genai.Client'):
        engine = RAGQueryEngine("test-api-key")
        query = engine.generate_search_query(invoice)
    
    # Property: If GSTIN present, query must include ITC eligibility
    if has_gstin:
        assert "input tax credit eligibility" in query, \
            f"Query '{query}' does not contain 'input tax credit eligibility' when GSTIN is present"
    else:
        # When no GSTIN, ITC eligibility should not be in query
        assert "input tax credit eligibility" not in query, \
            f"Query '{query}' contains 'input tax credit eligibility' when GSTIN is not present"


# Feature: rag-compliance-engine, Property 11: Conditional Query Enhancement
@given(
    vendor=st.text(min_size=1, max_size=100),
    amount=st.floats(min_value=0.01, max_value=1000000, allow_nan=False, allow_infinity=False),
    tax=st.floats(min_value=0.0, max_value=100000, allow_nan=False, allow_infinity=False),
    category=st.sampled_from(ExpenseCategory),
    description=st.text(min_size=1, max_size=200),
)
def test_query_includes_cash_limit_when_amount_exceeds_10000(vendor, amount, tax, category, description):
    """
    Property 11: Conditional Query Enhancement (Part 2 - Cash Limit)
    
    For any invoice with total_amount > 10000, the generated search query 
    SHALL include "cash payment limits".
    
    Validates: Requirements 6.5
    """
    # Ensure amount is not too close to boundary to avoid floating point issues
    assume(amount < 9999.0 or amount > 10001.0)
    
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
    
    # Property: If amount > 10000, query must include cash payment limits
    if amount > 10000:
        assert "cash payment limits" in query, \
            f"Query '{query}' does not contain 'cash payment limits' when amount (₹{amount}) > ₹10,000"
    else:
        # When amount <= 10000, cash limits should not be in query
        assert "cash payment limits" not in query, \
            f"Query '{query}' contains 'cash payment limits' when amount (₹{amount}) <= ₹10,000"
