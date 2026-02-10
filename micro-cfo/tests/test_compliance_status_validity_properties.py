"""
Property-based tests for compliance status validity
Feature: rag-compliance-engine
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hypothesis import given, strategies as st, settings, assume
from app.rules import HardRulesValidator
from app.rag_analyzer import AIComplianceAnalyzer
from app.schemas import InvoiceData, ExpenseCategory
from unittest.mock import Mock, patch
import json


# Valid compliance status values
VALID_STATUSES = ["compliant", "review_needed", "blocked"]


# Strategy for generating invoice data
def invoice_strategy():
    """Generate random invoice data for testing."""
    return st.builds(
        InvoiceData,
        vendor_name=st.text(min_size=1, max_size=100),
        invoice_number=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
        date=st.one_of(st.none(), st.text(min_size=1, max_size=20)),
        total_amount=st.floats(min_value=0.01, max_value=1000000, allow_nan=False, allow_infinity=False),
        tax_amount=st.floats(min_value=0.0, max_value=100000, allow_nan=False, allow_infinity=False),
        gstin=st.one_of(
            st.none(),
            st.text(min_size=15, max_size=15)
        ),
        currency=st.just("INR"),
        category=st.sampled_from(ExpenseCategory),
        item_description=st.text(min_size=1, max_size=200)
    )


# Feature: rag-compliance-engine, Property 14: Compliance Status Validity (Hard Rules)
@given(invoice=invoice_strategy())
@settings(max_examples=100, deadline=None)
def test_hard_rules_validator_returns_valid_status(invoice):
    """
    Property 14: Compliance Status Validity (Hard Rules Validator)
    
    For any invoice validated by HardRulesValidator, the returned status
    SHALL be exactly one of: "compliant", "review_needed", or "blocked".
    
    Validates: Requirements 8.6
    """
    validator = HardRulesValidator()
    result = validator.validate(invoice)
    
    # Check that result has status field
    assert "status" in result, (
        f"Expected result to contain 'status' field.\n"
        f"Result keys: {result.keys()}"
    )
    
    # Check that status is one of the valid values
    status = result["status"]
    assert status in VALID_STATUSES, (
        f"Expected status to be one of {VALID_STATUSES}.\n"
        f"Got: {status}\n"
        f"Invoice: vendor={invoice.vendor_name}, amount={invoice.total_amount}, "
        f"category={invoice.category.value}"
    )


# Feature: rag-compliance-engine, Property 14: Compliance Status Validity (AI Analyzer)
@given(
    invoice=invoice_strategy(),
    legal_context=st.text(min_size=0, max_size=1000),
    valid_status=st.sampled_from(VALID_STATUSES)
)
@settings(max_examples=100, deadline=None)
def test_ai_analyzer_returns_valid_status_on_success(invoice, legal_context, valid_status):
    """
    Property 14: Compliance Status Validity (AI Analyzer - Success Case)
    
    For any invoice analyzed by AIComplianceAnalyzer with a successful AI response,
    the returned status SHALL be exactly one of: "compliant", "review_needed", or "blocked".
    
    Validates: Requirements 8.6
    """
    # Mock the Gemini API to return a valid response
    mock_response = Mock()
    
    mock_response.text = json.dumps({
        "status": valid_status,
        "flags": ["Test flag"],
        "itc_eligible": True,
        "reasoning": "Test reasoning"
    })
    
    with patch('app.rag_analyzer.genai.Client') as mock_client:
        mock_instance = Mock()
        mock_instance.models.generate_content.return_value = mock_response
        mock_client.return_value = mock_instance
        
        analyzer = AIComplianceAnalyzer(api_key="test_key")
        result = analyzer.analyze_compliance(invoice, legal_context)
    
    # Check that result has status field
    assert "status" in result, (
        f"Expected result to contain 'status' field.\n"
        f"Result keys: {result.keys()}"
    )
    
    # Check that status is one of the valid values
    status = result["status"]
    assert status in VALID_STATUSES, (
        f"Expected status to be one of {VALID_STATUSES}.\n"
        f"Got: {status}\n"
        f"Invoice: vendor={invoice.vendor_name}, amount={invoice.total_amount}"
    )


# Feature: rag-compliance-engine, Property 14: Compliance Status Validity (AI Analyzer - Invalid Response)
@given(
    invoice=invoice_strategy(),
    legal_context=st.text(min_size=0, max_size=1000),
    invalid_status=st.text(min_size=0, max_size=50).filter(lambda s: s not in VALID_STATUSES)
)
@settings(max_examples=100, deadline=None)
def test_ai_analyzer_corrects_invalid_status(invoice, legal_context, invalid_status):
    """
    Property 14: Compliance Status Validity (AI Analyzer - Invalid Response Correction)
    
    For any invoice where the AI returns an invalid status value,
    the AIComplianceAnalyzer SHALL correct it to "review_needed".
    
    Validates: Requirements 8.6, 8.8
    """
    # Mock the Gemini API to return an invalid status
    mock_response = Mock()
    mock_response.text = json.dumps({
        "status": invalid_status,
        "flags": ["Test flag"],
        "itc_eligible": True,
        "reasoning": "Test reasoning"
    })
    
    with patch('app.rag_analyzer.genai.Client') as mock_client:
        mock_instance = Mock()
        mock_instance.models.generate_content.return_value = mock_response
        mock_client.return_value = mock_instance
        
        analyzer = AIComplianceAnalyzer(api_key="test_key")
        result = analyzer.analyze_compliance(invoice, legal_context)
    
    # Check that result has status field
    assert "status" in result, (
        f"Expected result to contain 'status' field.\n"
        f"Result keys: {result.keys()}"
    )
    
    # Check that status was corrected to a valid value
    status = result["status"]
    assert status in VALID_STATUSES, (
        f"Expected invalid status '{invalid_status}' to be corrected to one of {VALID_STATUSES}.\n"
        f"Got: {status}"
    )
    
    # Specifically, it should be corrected to "review_needed"
    assert status == "review_needed", (
        f"Expected invalid status to be corrected to 'review_needed'.\n"
        f"Got: {status}"
    )


# Feature: rag-compliance-engine, Property 14: Compliance Status Validity (AI Analyzer - Error Fallback)
@given(
    invoice=invoice_strategy(),
    legal_context=st.text(min_size=0, max_size=1000)
)
@settings(max_examples=100, deadline=None)
def test_ai_analyzer_returns_valid_status_on_error(invoice, legal_context):
    """
    Property 14: Compliance Status Validity (AI Analyzer - Error Fallback)
    
    For any invoice where the AI analysis fails with an exception,
    the AIComplianceAnalyzer SHALL return a valid status (review_needed).
    
    Validates: Requirements 8.6, 8.8
    """
    # Mock the Gemini API to raise an exception
    with patch('app.rag_analyzer.genai.Client') as mock_client:
        mock_instance = Mock()
        mock_instance.models.generate_content.side_effect = Exception("API Error")
        mock_client.return_value = mock_instance
        
        analyzer = AIComplianceAnalyzer(api_key="test_key")
        result = analyzer.analyze_compliance(invoice, legal_context)
    
    # Check that result has status field
    assert "status" in result, (
        f"Expected result to contain 'status' field even on error.\n"
        f"Result keys: {result.keys()}"
    )
    
    # Check that status is one of the valid values
    status = result["status"]
    assert status in VALID_STATUSES, (
        f"Expected status to be one of {VALID_STATUSES} even on error.\n"
        f"Got: {status}"
    )
    
    # Specifically, error fallback should return "review_needed"
    assert status == "review_needed", (
        f"Expected error fallback to return 'review_needed'.\n"
        f"Got: {status}"
    )


# Feature: rag-compliance-engine, Property 14: Compliance Status Validity (AI Analyzer - Missing Status)
@given(
    invoice=invoice_strategy(),
    legal_context=st.text(min_size=0, max_size=1000)
)
@settings(max_examples=100, deadline=None)
def test_ai_analyzer_handles_missing_status_field(invoice, legal_context):
    """
    Property 14: Compliance Status Validity (AI Analyzer - Missing Status Field)
    
    For any invoice where the AI response is missing the status field,
    the AIComplianceAnalyzer SHALL default to "review_needed".
    
    Validates: Requirements 8.6, 8.8
    """
    # Mock the Gemini API to return a response without status field
    mock_response = Mock()
    mock_response.text = json.dumps({
        "flags": ["Test flag"],
        "itc_eligible": True,
        "reasoning": "Test reasoning"
        # Note: no "status" field
    })
    
    with patch('app.rag_analyzer.genai.Client') as mock_client:
        mock_instance = Mock()
        mock_instance.models.generate_content.return_value = mock_response
        mock_client.return_value = mock_instance
        
        analyzer = AIComplianceAnalyzer(api_key="test_key")
        result = analyzer.analyze_compliance(invoice, legal_context)
    
    # Check that result has status field
    assert "status" in result, (
        f"Expected result to contain 'status' field even when AI response is missing it.\n"
        f"Result keys: {result.keys()}"
    )
    
    # Check that status is one of the valid values
    status = result["status"]
    assert status in VALID_STATUSES, (
        f"Expected status to be one of {VALID_STATUSES}.\n"
        f"Got: {status}"
    )
    
    # Specifically, missing status should default to "review_needed"
    assert status == "review_needed", (
        f"Expected missing status to default to 'review_needed'.\n"
        f"Got: {status}"
    )


# Feature: rag-compliance-engine, Property 14: Compliance Status Validity (Status Determinism)
@given(invoice=invoice_strategy())
@settings(max_examples=100, deadline=None)
def test_hard_rules_validator_status_is_deterministic(invoice):
    """
    Property 14: Compliance Status Validity (Determinism)
    
    For any invoice, calling HardRulesValidator.validate multiple times
    SHALL return the same valid status value (validation is deterministic).
    
    Validates: Requirements 8.6
    """
    validator = HardRulesValidator()
    
    result1 = validator.validate(invoice)
    result2 = validator.validate(invoice)
    result3 = validator.validate(invoice)
    
    status1 = result1["status"]
    status2 = result2["status"]
    status3 = result3["status"]
    
    # All statuses should be valid
    assert status1 in VALID_STATUSES, f"First call returned invalid status: {status1}"
    assert status2 in VALID_STATUSES, f"Second call returned invalid status: {status2}"
    assert status3 in VALID_STATUSES, f"Third call returned invalid status: {status3}"
    
    # All statuses should be identical
    assert status1 == status2 == status3, (
        f"Expected consistent status across multiple calls.\n"
        f"Got: {status1}, {status2}, {status3}\n"
        f"Invoice: vendor={invoice.vendor_name}, amount={invoice.total_amount}, "
        f"category={invoice.category.value}"
    )


if __name__ == "__main__":
    # Run the tests manually
    import pytest
    pytest.main([__file__, "-v"])
