"""
Property-based tests for GSTIN format validation
Feature: rag-compliance-engine
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hypothesis import given, strategies as st, settings, assume
from app.rules import validate_gstin


# Strategy for generating valid GSTIN strings
def valid_gstin_strategy():
    """Generate valid GSTIN strings matching the pattern."""
    return st.builds(
        lambda state_code, pan_chars, entity_num, entity_type, checksum_char, default_z, checksum_final: (
            f"{state_code:02d}"
            f"{''.join(pan_chars)}"
            f"{entity_num:04d}"
            f"{entity_type}"
            f"{checksum_char}"
            f"Z"
            f"{checksum_final}"
        ),
        state_code=st.integers(min_value=1, max_value=37),  # Valid state codes
        pan_chars=st.lists(st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), min_size=5, max_size=5),
        entity_num=st.integers(min_value=0, max_value=9999),
        entity_type=st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
        checksum_char=st.sampled_from('123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
        default_z=st.just('Z'),
        checksum_final=st.sampled_from('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    )


# Feature: rag-compliance-engine, Property 6: GSTIN Format Validation
@given(gstin=valid_gstin_strategy())
@settings(max_examples=100, deadline=None)
def test_valid_gstin_format_accepted(gstin):
    """
    Property 6: GSTIN Format Validation (Valid Format)
    
    For any string matching the GSTIN pattern [0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1},
    the GSTIN validator SHALL return True.
    
    Validates: Requirements 5.1
    """
    result = validate_gstin(gstin)
    
    assert result == True, (
        f"Expected validate_gstin to return True for valid GSTIN format.\n"
        f"GSTIN: {gstin}\n"
        f"Length: {len(gstin)}\n"
        f"Result: {result}"
    )


# Feature: rag-compliance-engine, Property 6: GSTIN Format Validation (Invalid Length)
@given(
    gstin=st.text(
        alphabet=st.characters(min_codepoint=32, max_codepoint=126),
        min_size=0,
        max_size=50
    )
)
@settings(max_examples=100, deadline=None)
def test_invalid_length_rejected(gstin):
    """
    Property 6: GSTIN Format Validation (Invalid Length)
    
    For any string that does not have exactly 15 characters,
    the GSTIN validator SHALL return False.
    
    Validates: Requirements 5.1
    """
    assume(len(gstin) != 15)  # Only test strings that don't have 15 characters
    
    result = validate_gstin(gstin)
    
    assert result == False, (
        f"Expected validate_gstin to return False for GSTIN with invalid length.\n"
        f"GSTIN: {gstin}\n"
        f"Length: {len(gstin)} (expected != 15)\n"
        f"Result: {result}"
    )


# Feature: rag-compliance-engine, Property 6: GSTIN Format Validation (Invalid Pattern)
@given(
    # Generate 15-character strings that don't match the pattern
    gstin=st.one_of(
        # All lowercase
        st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789', min_size=15, max_size=15),
        # Missing Z at position 13
        st.builds(
            lambda a, b, c: f"{a}{b}{c}",
            a=st.text(alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=13, max_size=13),
            b=st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXY'),  # Not Z
            c=st.text(alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=1, max_size=1)
        ),
        # Wrong start (not digits)
        st.builds(
            lambda a, b: f"{a}{b}",
            a=st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=2, max_size=2),
            b=st.text(alphabet='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=13, max_size=13)
        ),
        # Special characters
        st.text(alphabet='!@#$%^&*()_+-=[]{}|;:,.<>?/', min_size=15, max_size=15)
    )
)
@settings(max_examples=100, deadline=None)
def test_invalid_pattern_rejected(gstin):
    """
    Property 6: GSTIN Format Validation (Invalid Pattern)
    
    For any 15-character string that does not match the GSTIN pattern
    [0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1},
    the GSTIN validator SHALL return False.
    
    Validates: Requirements 5.1
    """
    # Ensure it's exactly 15 characters
    assume(len(gstin) == 15)
    
    # Ensure it doesn't match the valid pattern by checking key positions
    # Valid pattern: [0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}
    is_valid_pattern = (
        gstin[0:2].isdigit() and
        gstin[2:7].isupper() and gstin[2:7].isalpha() and
        gstin[7:11].isdigit() and
        gstin[11].isupper() and gstin[11].isalpha() and
        gstin[12] in '123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' and
        gstin[13] == 'Z' and
        gstin[14] in '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    )
    
    assume(not is_valid_pattern)  # Only test invalid patterns
    
    result = validate_gstin(gstin)
    
    assert result == False, (
        f"Expected validate_gstin to return False for invalid GSTIN pattern.\n"
        f"GSTIN: {gstin}\n"
        f"Length: {len(gstin)}\n"
        f"Result: {result}"
    )


# Feature: rag-compliance-engine, Property 6: GSTIN Format Validation (None/Empty)
@given(gstin=st.one_of(st.none(), st.just("")))
@settings(max_examples=10, deadline=None)
def test_none_or_empty_rejected(gstin):
    """
    Property 6: GSTIN Format Validation (None/Empty)
    
    For None or empty string inputs, the GSTIN validator SHALL return False.
    
    Validates: Requirements 5.1
    """
    result = validate_gstin(gstin)
    
    assert result == False, (
        f"Expected validate_gstin to return False for None or empty input.\n"
        f"GSTIN: {repr(gstin)}\n"
        f"Result: {result}"
    )


# Feature: rag-compliance-engine, Property 6: GSTIN Format Validation (Idempotence)
@given(gstin=st.text(min_size=0, max_size=20))
@settings(max_examples=100, deadline=None)
def test_validation_idempotence(gstin):
    """
    Property 6: GSTIN Format Validation (Idempotence)
    
    For any string, calling validate_gstin multiple times SHALL return
    the same result (validation is deterministic and idempotent).
    
    Validates: Requirements 5.1
    """
    result1 = validate_gstin(gstin)
    result2 = validate_gstin(gstin)
    result3 = validate_gstin(gstin)
    
    assert result1 == result2 == result3, (
        f"Expected validate_gstin to return consistent results.\n"
        f"GSTIN: {gstin}\n"
        f"Results: {result1}, {result2}, {result3}"
    )


if __name__ == "__main__":
    # Run the test manually
    import pytest
    pytest.main([__file__, "-v"])
