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
import logging

# Setup logging
logger = logging.getLogger(__name__)


class ComplianceAuditor:
    """Orchestrates the complete compliance audit workflow"""
    
    def __init__(self):
        """Initialize the compliance auditor with all components"""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.convex_url = os.getenv("CONVEX_URL")
        
        # Validate required environment variables
        if not self.api_key:
            raise ValueError(
                "Missing required environment variable: GOOGLE_API_KEY\n"
                "Please set GOOGLE_API_KEY in your .env file"
            )
        if not self.convex_url:
            raise ValueError(
                "Missing required environment variable: CONVEX_URL\n"
                "Please set CONVEX_URL in your .env file"
            )
        
        # Get configurable parameters
        search_limit = int(os.getenv("SEARCH_LIMIT", "3"))
        
        self.convex = ConvexClient(self.convex_url)
        
        self.hard_rules = HardRulesValidator()
        self.query_engine = RAGQueryEngine(self.api_key, search_limit=search_limit)
        self.ai_analyzer = AIComplianceAnalyzer(self.api_key)
    
    def audit_invoice(self, invoice: InvoiceData) -> Dict:
        """
        Complete compliance audit workflow
        
        Args:
            invoice: Invoice data to audit
            
        Returns:
            Compliance report with status, flags, category, citations
        """
        logger.info(f"Starting compliance audit for invoice: {invoice.vendor_name}, Amount: ₹{invoice.total_amount}")
        
        # Step 1: Hard rules validation (fast, always runs)
        hard_rules_result = self.hard_rules.validate(invoice)
        logger.info(f"Hard rules validation complete: {hard_rules_result['status']}, Flags: {len(hard_rules_result['flags'])}")
        
        # Step 2: RAG-based analysis (intelligent, context-aware)
        try:
            # Generate search query
            search_query = self.query_engine.generate_search_query(invoice)
            logger.info(f"Generated search query: {search_query[:100]}...")
            
            # Get query embedding
            query_embedding = self.query_engine.generate_query_embedding(search_query)
            logger.info(f"Generated query embedding: {len(query_embedding)} dimensions")
            
            # Search legal documents
            search_results = self.query_engine.search_legal_docs(
                self.convex, 
                query_embedding,
                limit=3
            )
            logger.info(f"Vector search returned {len(search_results)} results")
            
            # Format legal context
            legal_context = self.query_engine.format_legal_context(search_results)
            
            # AI analysis with legal context
            if legal_context:
                logger.info("Running AI compliance analysis with legal context")
                ai_result = self.ai_analyzer.analyze_compliance(invoice, legal_context)
                logger.info(f"AI analysis complete: {ai_result['status']}")
            else:
                # No legal context found, skip AI analysis
                logger.warning("No relevant legal text found, skipping AI analysis")
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
            logger.error(f"RAG analysis failed: {e}", exc_info=True)
            logger.warning("Falling back to hard rules validation only")
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
        
        logger.info(f"Audit complete: Final status={final_status}, Total flags={len(combined_flags)}, Citations={len(citations)}")
        
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
