"""
Unit tests for AI Compliance Analyzer
Tests AI analysis with mock responses, error handling, and response validation
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from app.rag_analyzer import AIComplianceAnalyzer
from app.schemas import InvoiceData, ExpenseCategory


class TestAIComplianceAnalyzer:
    """Test suite for AI Compliance Analyzer"""
    
    @pytest.fixture
    def mock_api_key(self):
        """Mock API key for testing"""
        return "test-api-key-12345"
    
    @pytest.fixture
    def analyzer(self, mock_api_key):
        """Create an AI compliance analyzer instance with mocked client"""
        with patch('app.rag_analyzer.genai.Client'):
            analyzer = AIComplianceAnalyzer(mock_api_key)
            return analyzer
    
    @pytest.fixture
    def sample_invoice(self):
        """Sample invoice for testing"""
        return InvoiceData(
            vendor_name="Test Vendor",
            total_amount=15000.0,
            tax_amount=2700.0,
            gstin="29ABCDE1234F1Z5",
            category=ExpenseCategory.FOOD_BEVERAGE,
            item_description="Restaurant meal for client meeting"
        )
    
    @pytest.fixture
    def sample_legal_context(self):
        """Sample legal context for testing"""
        return """[Source: a2017-12.pdf, Page 42]
Section 17(5) of the CGST Act blocks input tax credit on food and beverages.
Businesses cannot claim ITC on restaurant expenses unless specifically allowed."""
    
    # Test with mock AI responses
    
    def test_analyze_compliance_with_compliant_response(self, analyzer, sample_invoice, sample_legal_context):
        """Test analysis with AI returning compliant status"""
        # Mock the AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "compliant",
            "flags": ["✅ Expense is allowable"],
            "itc_eligible": True,
            "reasoning": "Standard business expense with valid GSTIN"
        })
        analyzer.client.models.generate_content = Mock(return_value=mock_response)
        
        result = analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        assert result["status"] == "compliant"
        assert "flags" in result
        assert result["itc_eligible"] is True
        assert "reasoning" in result
    
    def test_analyze_compliance_with_review_needed_response(self, analyzer, sample_invoice, sample_legal_context):
        """Test analysis with AI returning review_needed status"""
        # Mock the AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "review_needed",
            "flags": ["⚠️ High-value transaction requires review"],
            "itc_eligible": False,
            "reasoning": "Amount exceeds threshold, manual review recommended"
        })
        analyzer.client.models.generate_content = Mock(return_value=mock_response)
        
        result = analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        assert result["status"] == "review_needed"
        assert len(result["flags"]) > 0
        assert result["itc_eligible"] is False
    
    def test_analyze_compliance_with_blocked_response(self, analyzer, sample_invoice, sample_legal_context):
        """Test analysis with AI returning blocked status"""
        # Mock the AI response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "blocked",
            "flags": ["🚫 Section 17(5): Food & Beverage ITC blocked"],
            "itc_eligible": False,
            "reasoning": "ITC explicitly disallowed under Section 17(5)"
        })
        analyzer.client.models.generate_content = Mock(return_value=mock_response)
        
        result = analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        assert result["status"] == "blocked"
        assert len(result["flags"]) > 0
        assert result["itc_eligible"] is False
    
    # Test response validation
    
    def test_analyze_compliance_validates_invalid_status(self, analyzer, sample_invoice, sample_legal_context):
        """Test that invalid status is corrected to review_needed"""
        # Mock the AI response with invalid status
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "invalid_status",
            "flags": ["Some flag"],
            "itc_eligible": False,
            "reasoning": "Some reasoning"
        })
        analyzer.client.models.generate_content = Mock(return_value=mock_response)
        
        result = analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        # Should default to review_needed for invalid status
        assert result["status"] == "review_needed"
    
    def test_analyze_compliance_validates_missing_status(self, analyzer, sample_invoice, sample_legal_context):
        """Test that missing status field is added with review_needed"""
        # Mock the AI response without status field
        mock_response = Mock()
        mock_response.text = json.dumps({
            "flags": ["Some flag"],
            "itc_eligible": False,
            "reasoning": "Some reasoning"
        })
        analyzer.client.models.generate_content = Mock(return_value=mock_response)
        
        result = analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        # Should default to review_needed when status is missing
        assert result["status"] == "review_needed"
    
    def test_analyze_compliance_validates_missing_flags(self, analyzer, sample_invoice, sample_legal_context):
        """Test that missing flags field is added as empty list"""
        # Mock the AI response without flags field
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "compliant",
            "itc_eligible": True,
            "reasoning": "Some reasoning"
        })
        analyzer.client.models.generate_content = Mock(return_value=mock_response)
        
        result = analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        # Should add empty flags list when missing
        assert "flags" in result
        assert isinstance(result["flags"], list)
    
    def test_analyze_compliance_validates_all_valid_statuses(self, analyzer, sample_invoice, sample_legal_context):
        """Test that all three valid statuses are accepted"""
        valid_statuses = ["compliant", "review_needed", "blocked"]
        
        for status in valid_statuses:
            mock_response = Mock()
            mock_response.text = json.dumps({
                "status": status,
                "flags": [],
                "itc_eligible": False,
                "reasoning": "Test"
            })
            analyzer.client.models.generate_content = Mock(return_value=mock_response)
            
            result = analyzer.analyze_compliance(sample_invoice, sample_legal_context)
            
            assert result["status"] == status
    
    # Test error handling and fallback
    
    def test_analyze_compliance_handles_api_exception(self, analyzer, sample_invoice, sample_legal_context):
        """Test that API exceptions are caught and fallback response is returned"""
        # Mock the AI to raise an exception
        analyzer.client.models.generate_content = Mock(side_effect=Exception("API Error"))
        
        result = analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        # Should return fallback response
        assert result["status"] == "review_needed"
        assert len(result["flags"]) > 0
        assert "AI analysis failed" in result["flags"][0]
        assert result["itc_eligible"] is False
        assert "reasoning" in result
    
    def test_analyze_compliance_handles_json_decode_error(self, analyzer, sample_invoice, sample_legal_context):
        """Test that JSON decode errors are caught and fallback response is returned"""
        # Mock the AI response with invalid JSON
        mock_response = Mock()
        mock_response.text = "This is not valid JSON"
        analyzer.client.models.generate_content = Mock(return_value=mock_response)
        
        result = analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        # Should return fallback response
        assert result["status"] == "review_needed"
        assert len(result["flags"]) > 0
        assert "AI analysis failed" in result["flags"][0]
        assert result["itc_eligible"] is False
    
    def test_analyze_compliance_handles_network_timeout(self, analyzer, sample_invoice, sample_legal_context):
        """Test that network timeouts are handled gracefully"""
        # Mock the AI to raise a timeout exception
        analyzer.client.models.generate_content = Mock(side_effect=TimeoutError("Request timeout"))
        
        result = analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        # Should return fallback response
        assert result["status"] == "review_needed"
        assert result["itc_eligible"] is False
        assert any("AI analysis failed" in flag for flag in result["flags"])
    
    def test_analyze_compliance_fallback_includes_error_message(self, analyzer, sample_invoice, sample_legal_context):
        """Test that fallback response includes the error message"""
        error_message = "Specific API error occurred"
        analyzer.client.models.generate_content = Mock(side_effect=Exception(error_message))
        
        result = analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        # Should include error message in flags
        assert any(error_message in flag for flag in result["flags"])
    
    # Test prompt construction
    
    def test_analyze_compliance_includes_invoice_details_in_prompt(self, analyzer, sample_invoice, sample_legal_context):
        """Test that the prompt includes all invoice details"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "compliant",
            "flags": [],
            "itc_eligible": True,
            "reasoning": "Test"
        })
        analyzer.client.models.generate_content = Mock(return_value=mock_response)
        
        analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        # Get the prompt that was sent
        call_args = analyzer.client.models.generate_content.call_args
        prompt = call_args[1]["contents"]
        
        # Verify invoice details are in prompt
        assert sample_invoice.vendor_name in prompt
        assert str(sample_invoice.total_amount) in prompt
        assert str(sample_invoice.tax_amount) in prompt
        assert sample_invoice.gstin in prompt
        assert sample_invoice.category.value in prompt
        assert sample_invoice.item_description in prompt
    
    def test_analyze_compliance_includes_legal_context_in_prompt(self, analyzer, sample_invoice, sample_legal_context):
        """Test that the prompt includes the legal context"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "compliant",
            "flags": [],
            "itc_eligible": True,
            "reasoning": "Test"
        })
        analyzer.client.models.generate_content = Mock(return_value=mock_response)
        
        analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        # Get the prompt that was sent
        call_args = analyzer.client.models.generate_content.call_args
        prompt = call_args[1]["contents"]
        
        # Verify legal context is in prompt
        assert sample_legal_context in prompt
    
    def test_analyze_compliance_uses_correct_model_config(self, analyzer, sample_invoice, sample_legal_context):
        """Test that the correct model configuration is used"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "compliant",
            "flags": [],
            "itc_eligible": True,
            "reasoning": "Test"
        })
        analyzer.client.models.generate_content = Mock(return_value=mock_response)
        
        analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        # Get the config that was sent
        call_args = analyzer.client.models.generate_content.call_args
        config = call_args[1]["config"]
        
        # Verify configuration
        assert config["response_mime_type"] == "application/json"
        assert config["temperature"] == 0.1
    
    def test_analyze_compliance_uses_correct_model_name(self, analyzer, sample_invoice, sample_legal_context):
        """Test that the correct model name is used"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "compliant",
            "flags": [],
            "itc_eligible": True,
            "reasoning": "Test"
        })
        analyzer.client.models.generate_content = Mock(return_value=mock_response)
        
        analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        # Get the model that was used
        call_args = analyzer.client.models.generate_content.call_args
        model = call_args[1]["model"]
        
        # Verify model name
        assert model == "gemini-2.5-flash"
    
    # Test edge cases
    
    def test_analyze_compliance_with_empty_legal_context(self, analyzer, sample_invoice):
        """Test analysis with empty legal context"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "review_needed",
            "flags": ["No legal context available"],
            "itc_eligible": False,
            "reasoning": "Cannot determine compliance without legal text"
        })
        analyzer.client.models.generate_content = Mock(return_value=mock_response)
        
        result = analyzer.analyze_compliance(sample_invoice, "")
        
        # Should still work with empty context
        assert result["status"] in ["compliant", "review_needed", "blocked"]
        assert "flags" in result
    
    def test_analyze_compliance_with_invoice_missing_optional_fields(self, analyzer, sample_legal_context):
        """Test analysis with invoice missing optional fields"""
        minimal_invoice = InvoiceData(
            vendor_name="Test Vendor",
            total_amount=5000.0,
            category=ExpenseCategory.OFFICE_SUPPLIES,
            item_description="Office supplies"
        )
        
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "compliant",
            "flags": [],
            "itc_eligible": False,
            "reasoning": "Basic office expense"
        })
        analyzer.client.models.generate_content = Mock(return_value=mock_response)
        
        result = analyzer.analyze_compliance(minimal_invoice, sample_legal_context)
        
        # Should handle missing optional fields gracefully
        assert result["status"] in ["compliant", "review_needed", "blocked"]
        
        # Verify prompt handles None values
        call_args = analyzer.client.models.generate_content.call_args
        prompt = call_args[1]["contents"]
        assert "Not provided" in prompt  # Should show "Not provided" for missing fields
    
    def test_analyze_compliance_returns_all_required_fields(self, analyzer, sample_invoice, sample_legal_context):
        """Test that response always contains all required fields"""
        mock_response = Mock()
        mock_response.text = json.dumps({
            "status": "compliant",
            "flags": ["Test flag"],
            "itc_eligible": True,
            "reasoning": "Test reasoning"
        })
        analyzer.client.models.generate_content = Mock(return_value=mock_response)
        
        result = analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        # Verify all required fields are present
        assert "status" in result
        assert "flags" in result
        assert "itc_eligible" in result
        assert "reasoning" in result
    
    def test_analyze_compliance_fallback_returns_all_required_fields(self, analyzer, sample_invoice, sample_legal_context):
        """Test that fallback response contains all required fields"""
        analyzer.client.models.generate_content = Mock(side_effect=Exception("Test error"))
        
        result = analyzer.analyze_compliance(sample_invoice, sample_legal_context)
        
        # Verify all required fields are present in fallback
        assert "status" in result
        assert "flags" in result
        assert "itc_eligible" in result
        assert "reasoning" in result
