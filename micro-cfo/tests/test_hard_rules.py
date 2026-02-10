"""
Unit tests for hard rules validator
"""
import pytest
from app.rules import (
    validate_gstin,
    validate_gst_rate,
    check_cash_limit,
    check_blocked_itc,
    check_math,
    HardRulesValidator
)
from app.schemas import InvoiceData, ExpenseCategory


class TestValidateGSTIN:
    """Test GSTIN validation function"""
    
    def test_valid_gstin(self):
        """Test with valid GSTIN format"""
        valid_gstin = "27AAPFU0939F1ZV"
        assert validate_gstin(valid_gstin) == True
    
    def test_valid_gstin_multiple_formats(self):
        """Test multiple valid GSTIN formats"""
        valid_gstins = [
            "27AAPFU0939F1ZV",
            "09AAACH7409R1ZZ",
            "29AABCT1332L1Z5",
            "33AABCU9603R1Z1"
        ]
        for gstin in valid_gstins:
            assert validate_gstin(gstin) == True, f"Failed for {gstin}"
    
    def test_invalid_length(self):
        """Test with incorrect length"""
        assert validate_gstin("27AAPFU0939F1Z") == False  # 14 chars
        assert validate_gstin("27AAPFU0939F1ZVV") == False  # 16 chars
        assert validate_gstin("27AAPFU") == False  # Too short
    
    def test_invalid_pattern_first_two_digits(self):
        """Test with invalid first two digits (state code)"""
        assert validate_gstin("AA27APFU0939F1ZV") == False  # Letters instead of digits
        assert validate_gstin("A7AAPFU0939F1ZV") == False  # One letter, one digit
    
    def test_invalid_pattern_pan_section(self):
        """Test with invalid PAN section (chars 3-12)"""
        assert validate_gstin("27aapfu0939F1ZV") == False  # Lowercase letters
        assert validate_gstin("27AAP1U0939F1ZV") == False  # Digit in letter position
        assert validate_gstin("27AAPFUAA39F1ZV") == False  # Letters in digit position
    
    def test_invalid_pattern_missing_z(self):
        """Test with missing Z at position 14"""
        assert validate_gstin("27AAPFU0939F1XV") == False  # X instead of Z
        assert validate_gstin("27AAPFU0939F11V") == False  # 1 instead of Z
    
    def test_invalid_pattern_last_char(self):
        """Test with invalid last character"""
        # Last char should be alphanumeric
        assert validate_gstin("27AAPFU0939F1Z!") == False  # Special char
    
    def test_none_or_empty(self):
        """Test with None or empty string"""
        assert validate_gstin(None) == False
        assert validate_gstin("") == False
        assert validate_gstin("   ") == False  # Whitespace only


class TestValidateGSTRate:
    """Test GST rate validation function"""
    
    def test_valid_5_percent(self):
        """Test with 5% GST rate"""
        total = 105.0
        tax = 5.0
        assert validate_gst_rate(total, tax) == True
    
    def test_valid_12_percent(self):
        """Test with 12% GST rate"""
        total = 112.0
        tax = 12.0
        assert validate_gst_rate(total, tax) == True
    
    def test_valid_18_percent(self):
        """Test with 18% GST rate"""
        total = 118.0
        tax = 18.0
        assert validate_gst_rate(total, tax) == True
    
    def test_valid_28_percent(self):
        """Test with 28% GST rate"""
        total = 128.0
        tax = 28.0
        assert validate_gst_rate(total, tax) == True
    
    def test_all_standard_rates(self):
        """Test all standard GST rates (5%, 12%, 18%, 28%)"""
        test_cases = [
            (105.0, 5.0),    # 5%
            (112.0, 12.0),   # 12%
            (118.0, 18.0),   # 18%
            (128.0, 28.0),   # 28%
        ]
        for total, tax in test_cases:
            assert validate_gst_rate(total, tax) == True, f"Failed for {tax}/{total}"
    
    def test_invalid_rate_10_percent(self):
        """Test with non-standard 10% rate"""
        total = 110.0
        tax = 10.0  # 10% rate
        assert validate_gst_rate(total, tax) == False
    
    def test_invalid_rate_15_percent(self):
        """Test with non-standard 15% rate"""
        total = 115.0
        tax = 15.0  # 15% rate
        assert validate_gst_rate(total, tax) == False
    
    def test_invalid_rate_20_percent(self):
        """Test with non-standard 20% rate"""
        total = 120.0
        tax = 20.0  # 20% rate
        assert validate_gst_rate(total, tax) == False
    
    def test_rate_within_tolerance(self):
        """Test rates within 0.5% tolerance"""
        # 18% with slight rounding: should pass
        total = 118.4
        tax = 18.0
        assert validate_gst_rate(total, tax) == True
    
    def test_zero_total(self):
        """Test with zero total amount"""
        assert validate_gst_rate(0, 0) == True
    
    def test_zero_tax(self):
        """Test with zero tax amount"""
        assert validate_gst_rate(100.0, 0) == False
    
    def test_negative_tax(self):
        """Test with negative tax amount"""
        assert validate_gst_rate(100.0, -5.0) == False
    
    def test_tax_greater_than_total(self):
        """Test with tax >= total (invalid invoice)"""
        assert validate_gst_rate(100.0, 100.0) == False
        assert validate_gst_rate(100.0, 150.0) == False


class TestCheckCashLimit:
    """Test cash limit checking function"""
    
    def test_below_limit(self):
        """Test amount below ₹10,000"""
        flags = check_cash_limit(9999.0)
        assert len(flags) == 0
    
    def test_at_limit(self):
        """Test amount exactly at ₹10,000 boundary"""
        flags = check_cash_limit(10000.0)
        assert len(flags) == 0  # Should not flag at exactly 10,000
    
    def test_above_limit(self):
        """Test amount above ₹10,000"""
        flags = check_cash_limit(10001.0)
        assert len(flags) == 1
        assert "Section 40A(3)" in flags[0]
    
    def test_high_value_transaction(self):
        """Test with significantly high value"""
        flags = check_cash_limit(50000.0)
        assert len(flags) == 1
        assert "Section 40A(3)" in flags[0]
        assert "10,000" in flags[0]
    
    def test_small_amount(self):
        """Test with small amounts"""
        for amount in [100.0, 1000.0, 5000.0]:
            flags = check_cash_limit(amount)
            assert len(flags) == 0, f"Failed for amount {amount}"


class TestCheckBlockedITC:
    """Test blocked ITC checking function"""
    
    def test_food_beverage_blocked(self):
        """Test food & beverage category is blocked"""
        flags = check_blocked_itc(ExpenseCategory.FOOD_BEVERAGE)
        assert len(flags) == 1
        assert "Section 17(5)" in flags[0]
        assert "Food & Beverage" in flags[0]
    
    def test_office_supplies_allowed(self):
        """Test office supplies category is not blocked"""
        flags = check_blocked_itc(ExpenseCategory.OFFICE_SUPPLIES)
        assert len(flags) == 0
    
    def test_travel_allowed(self):
        """Test travel category is not blocked"""
        flags = check_blocked_itc(ExpenseCategory.TRAVEL)
        assert len(flags) == 0
    
    def test_electronics_allowed(self):
        """Test electronics category is not blocked"""
        flags = check_blocked_itc(ExpenseCategory.ELECTRONICS)
        assert len(flags) == 0
    
    def test_professional_fees_allowed(self):
        """Test professional fees category is not blocked"""
        flags = check_blocked_itc(ExpenseCategory.PROFESSIONAL_FEES)
        assert len(flags) == 0
    
    def test_utilities_allowed(self):
        """Test utilities category is not blocked"""
        flags = check_blocked_itc(ExpenseCategory.UTILITIES)
        assert len(flags) == 0
    
    def test_rent_allowed(self):
        """Test rent category is not blocked"""
        flags = check_blocked_itc(ExpenseCategory.RENT)
        assert len(flags) == 0
    
    def test_other_allowed(self):
        """Test other category is not blocked"""
        flags = check_blocked_itc(ExpenseCategory.OTHER)
        assert len(flags) == 0


class TestCheckMath:
    """Test math validation function"""
    
    def test_valid_math(self):
        """Test with valid GST calculation"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=118.0,
            tax_amount=18.0,
            category=ExpenseCategory.OFFICE_SUPPLIES,
            item_description="Test item"
        )
        flags = check_math(invoice)
        assert len(flags) == 0
    
    def test_invalid_math(self):
        """Test with invalid GST calculation"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=110.0,
            tax_amount=10.0,  # 10% rate - invalid
            category=ExpenseCategory.OFFICE_SUPPLIES,
            item_description="Test item"
        )
        flags = check_math(invoice)
        assert len(flags) == 1
        assert "doesn't match standard GST rates" in flags[0]


class TestHardRulesValidator:
    """Test HardRulesValidator class"""
    
    def test_compliant_invoice(self):
        """Test with fully compliant invoice"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=118.0,
            tax_amount=18.0,
            gstin="27AAPFU0939F1ZV",
            category=ExpenseCategory.OFFICE_SUPPLIES,
            item_description="Test item"
        )
        validator = HardRulesValidator()
        result = validator.validate(invoice)
        
        assert result["status"] == "compliant"
        assert len(result["flags"]) == 0
    
    def test_compliant_invoice_without_gstin(self):
        """Test compliant invoice without GSTIN"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=118.0,
            tax_amount=18.0,
            category=ExpenseCategory.OFFICE_SUPPLIES,
            item_description="Test item"
        )
        validator = HardRulesValidator()
        result = validator.validate(invoice)
        
        assert result["status"] == "compliant"
        assert len(result["flags"]) == 0
    
    def test_invalid_gstin(self):
        """Test with invalid GSTIN"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=118.0,
            tax_amount=18.0,
            gstin="INVALID",
            category=ExpenseCategory.OFFICE_SUPPLIES,
            item_description="Test item"
        )
        validator = HardRulesValidator()
        result = validator.validate(invoice)
        
        assert result["status"] == "review_needed"
        assert any("Invalid GSTIN" in flag for flag in result["flags"])
    
    def test_invalid_gst_rate(self):
        """Test with invalid GST rate"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=110.0,
            tax_amount=10.0,  # 10% - non-standard rate
            category=ExpenseCategory.OFFICE_SUPPLIES,
            item_description="Test item"
        )
        validator = HardRulesValidator()
        result = validator.validate(invoice)
        
        assert result["status"] == "review_needed"
        assert any("doesn't match standard GST rates" in flag for flag in result["flags"])
    
    def test_blocked_itc(self):
        """Test with blocked ITC category"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=118.0,
            tax_amount=18.0,
            category=ExpenseCategory.FOOD_BEVERAGE,
            item_description="Restaurant bill"
        )
        validator = HardRulesValidator()
        result = validator.validate(invoice)
        
        assert result["status"] == "blocked"
        assert any("Section 17(5)" in flag for flag in result["flags"])
    
    def test_high_value_transaction(self):
        """Test with high value transaction"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=15000.0,
            tax_amount=2700.0,
            category=ExpenseCategory.OFFICE_SUPPLIES,
            item_description="Test item"
        )
        validator = HardRulesValidator()
        result = validator.validate(invoice)
        
        assert result["status"] == "review_needed"
        assert any("Section 40A(3)" in flag for flag in result["flags"])
    
    def test_cash_limit_boundary(self):
        """Test cash limit at exactly ₹10,000"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=10000.0,
            tax_amount=1800.0,
            category=ExpenseCategory.OFFICE_SUPPLIES,
            item_description="Test item"
        )
        validator = HardRulesValidator()
        result = validator.validate(invoice)
        
        # At exactly 10,000, should not flag
        assert not any("Section 40A(3)" in flag for flag in result["flags"])
    
    def test_multiple_violations(self):
        """Test invoice with multiple violations"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=15000.0,
            tax_amount=1500.0,  # 10% - invalid rate
            gstin="INVALID",
            category=ExpenseCategory.FOOD_BEVERAGE,
            item_description="Restaurant bill"
        )
        validator = HardRulesValidator()
        result = validator.validate(invoice)
        
        # Should be blocked due to ITC category
        assert result["status"] == "blocked"
        # Should have multiple flags
        assert len(result["flags"]) >= 3
        assert any("Invalid GSTIN" in flag for flag in result["flags"])
        assert any("doesn't match standard GST rates" in flag for flag in result["flags"])
        assert any("Section 40A(3)" in flag for flag in result["flags"])
        assert any("Section 17(5)" in flag for flag in result["flags"])
    
    def test_status_priority_blocked_over_review(self):
        """Test that blocked status takes priority over review_needed"""
        invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=110.0,
            tax_amount=10.0,  # Invalid rate -> review_needed
            category=ExpenseCategory.FOOD_BEVERAGE,  # Blocked ITC -> blocked
            item_description="Restaurant bill"
        )
        validator = HardRulesValidator()
        result = validator.validate(invoice)
        
        # Blocked should take priority
        assert result["status"] == "blocked"
