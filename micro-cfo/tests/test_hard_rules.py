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
    
    def test_invalid_length(self):
        """Test with incorrect length"""
        assert validate_gstin("27AAPFU0939F1Z") == False  # 14 chars
        assert validate_gstin("27AAPFU0939F1ZVV") == False  # 16 chars
    
    def test_invalid_pattern(self):
        """Test with invalid pattern"""
        assert validate_gstin("AA27APFU0939F1ZV") == False  # Wrong start
        assert validate_gstin("27aapfu0939F1ZV") == False  # Lowercase letters
        assert validate_gstin("27AAPFU0939F1XV") == False  # Missing Z
    
    def test_none_or_empty(self):
        """Test with None or empty string"""
        assert validate_gstin(None) == False
        assert validate_gstin("") == False


class TestValidateGSTRate:
    """Test GST rate validation function"""
    
    def test_valid_5_percent(self):
        """Test with 5% GST rate"""
        total = 105.0
        tax = 5.0
        assert validate_gst_rate(total, tax) == True
    
    def test_valid_18_percent(self):
        """Test with 18% GST rate"""
        total = 118.0
        tax = 18.0
        assert validate_gst_rate(total, tax) == True
    
    def test_invalid_rate(self):
        """Test with non-standard rate"""
        total = 110.0
        tax = 10.0  # 10% rate
        assert validate_gst_rate(total, tax) == False
    
    def test_zero_total(self):
        """Test with zero total amount"""
        assert validate_gst_rate(0, 0) == True


class TestCheckCashLimit:
    """Test cash limit checking function"""
    
    def test_below_limit(self):
        """Test amount below ₹10,000"""
        flags = check_cash_limit(9999.0)
        assert len(flags) == 0
    
    def test_above_limit(self):
        """Test amount above ₹10,000"""
        flags = check_cash_limit(10001.0)
        assert len(flags) == 1
        assert "Section 40A(3)" in flags[0]


class TestCheckBlockedITC:
    """Test blocked ITC checking function"""
    
    def test_food_beverage_blocked(self):
        """Test food & beverage category is blocked"""
        flags = check_blocked_itc(ExpenseCategory.FOOD_BEVERAGE)
        assert len(flags) == 1
        assert "Section 17(5)" in flags[0]
    
    def test_other_category_allowed(self):
        """Test other categories are not blocked"""
        flags = check_blocked_itc(ExpenseCategory.OFFICE_SUPPLIES)
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
