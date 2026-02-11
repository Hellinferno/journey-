"""
AI Compliance Analyzer
Uses Gemini with legal context to determine invoice compliance
"""
from google import genai
from app.schemas import InvoiceData
from typing import Dict, List
import json


class AIComplianceAnalyzer:
    """AI-powered compliance analyzer using Gemini"""
    
    def __init__(self, api_key: str):
        """
        Initialize the AI compliance analyzer
        
        Args:
            api_key: Google API key
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.0-flash-exp"

    
    def analyze_compliance(self, invoice: InvoiceData, legal_context: str) -> Dict:
        """
        Use AI with legal context to determine compliance
        
        Args:
            invoice: Invoice data
            legal_context: Retrieved legal text
            
        Returns:
            Dictionary with status, flags, itc_eligible, reasoning
        """
        prompt = f"""You are a tax compliance expert analyzing an invoice against Indian GST and Income Tax laws.

**Invoice Details:**
- Vendor: {invoice.vendor_name}
- Amount: ₹{invoice.total_amount}
- Tax: ₹{invoice.tax_amount}
- GSTIN: {invoice.gstin or 'Not provided'}
- Category: {invoice.category.value}
- Items: {invoice.item_description}
- Date: {invoice.date or 'Not provided'}

**Relevant Legal Text:**
{legal_context}

**Task:**
Analyze this invoice for compliance issues. Consider:
1. Input Tax Credit (ITC) eligibility based on the category and legal text
2. Any violations of GST or Income Tax provisions
3. Whether the expense is allowable as a business deduction

Return JSON with this structure:
{{
  "status": "compliant" | "review_needed" | "blocked",
  "flags": ["list of specific compliance issues or notes"],
  "itc_eligible": true | false,
  "reasoning": "brief explanation of the decision"
}}

Rules:
- Use "blocked" only if ITC is explicitly disallowed by law
- Use "review_needed" if there are concerns or ambiguities
- Use "compliant" only if clearly allowed
- Base decisions on the provided legal text when available
- Be specific in flags, citing sections when possible
"""
        
        try:
            from google.genai import types
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                )
            )
            result = json.loads(response.text)
            
            # Validate response structure
            if "status" not in result or result["status"] not in ["compliant", "review_needed", "blocked"]:
                result["status"] = "review_needed"
            
            if "flags" not in result:
                result["flags"] = []
            
            return result
            
        except Exception as e:
            # Fallback on error
            return {
                "status": "review_needed",
                "flags": [f"⚠️ AI analysis failed: {str(e)}"],
                "itc_eligible": False,
                "reasoning": "Unable to complete AI analysis"
            }
