"""
Compliance Auditor - RAG-powered compliance checking
Orchestrates hard rules validation and AI-based analysis
"""
from app.schemas import InvoiceData
from app.rules import HardRulesValidator
from app.rag_query import RAGQueryEngine
from app.rag_analyzer import AIComplianceAnalyzer
from convex import ConvexClient
from typing import Dict, List
import os


class ComplianceAuditor:
    """Orchestrates the complete compliance audit workflow"""
    
    def __init__(self):
        """Initialize the compliance auditor with all components"""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.convex_url = os.getenv("CONVEX_URL")
        self.convex = ConvexClient(self.convex_url)
        
        self.hard_rules = HardRulesValidator()
        self.query_engine = RAGQueryEngine(self.api_key)
        self.ai_analyzer = AIComplianceAnalyzer(self.api_key)
    
    def audit_invoice(self, invoice: InvoiceData) -> Dict:
        """
        Complete compliance audit workflow
        
        Args:
            invoice: Invoice data to audit
            
        Returns:
            Compliance report with status, flags, category, citations
        """
        # Step 1: Hard rules validation (fast, always runs)
        hard_rules_result = self.hard_rules.validate(invoice)
        
        # Step 2: RAG-based analysis (intelligent, context-aware)
        try:
            # Generate search query
            search_query = self.query_engine.generate_search_query(invoice)
            
            # Get query embedding
            query_embedding = self.query_engine.generate_query_embedding(search_query)
            
            # Search legal documents
            search_results = self.query_engine.search_legal_docs(
                self.convex, 
                query_embedding,
                limit=3
            )
            
            # Format legal context
            legal_context = self.query_engine.format_legal_context(search_results)
            
            # AI analysis with legal context
            if legal_context:
                ai_result = self.ai_analyzer.analyze_compliance(invoice, legal_context)
            else:
                # No legal context found, skip AI analysis
                ai_result = {
                    "status": "review_needed",
                    "flags": ["⚠️ No relevant legal text found"],
                    "itc_eligible": False,
                }
            
            # Extract citations from search results
            citations = [
                {
                    "source": r["source_file"],
                    "page": r["page_number"],
                }
                for r in search_results
            ]
            
        except Exception as e:
            # Fallback to hard rules only
            print(f"RAG analysis failed: {e}")
            ai_result = {
                "status": "review_needed",
                "flags": ["⚠️ Advanced analysis unavailable"],
                "itc_eligible": False,
            }
            citations = []
        
        # Step 3: Combine results
        combined_flags = hard_rules_result["flags"] + ai_result["flags"]
        
        # Determine final status (most restrictive wins)
        status_priority = {"blocked": 3, "review_needed": 2, "compliant": 1}
        final_status = max(
            [hard_rules_result["status"], ai_result["status"]],
            key=lambda s: status_priority[s]
        )
        
        return {
            "status": final_status,
            "flags": combined_flags,
            "category": invoice.category.value,
            "citations": citations,
            "itc_eligible": ai_result.get("itc_eligible", False),
        }


# Legacy function for backward compatibility - now uses RAG engine
def audit_invoice(invoice: InvoiceData) -> Dict:
    """
    Legacy function for backward compatibility
    Now uses the RAG-powered ComplianceAuditor
    """
    auditor = ComplianceAuditor()
    return auditor.audit_invoice(invoice)
