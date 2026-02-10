"""
RAG Query Engine for Compliance Analysis
Generates search queries and retrieves relevant legal text
"""
from app.schemas import InvoiceData, ExpenseCategory
from typing import Dict, List
from google import genai


class RAGQueryEngine:
    """Engine for generating queries and searching legal documents"""
    
    def __init__(self, api_key: str):
        """
        Initialize the RAG query engine
        
        Args:
            api_key: Google API key for embeddings
        """
        self.client = genai.Client(api_key=api_key)
        self.embedding_model = "models/gemini-embedding-001"

    
    def generate_search_query(self, invoice: InvoiceData) -> str:
        """
        Create search query based on invoice context
        
        Args:
            invoice: Invoice data
            
        Returns:
            Consolidated search query string
        """
        query_parts = []
        
        # Base query with category and description
        query_parts.append(f"GST compliance for {invoice.category.value}")
        query_parts.append(invoice.item_description)
        
        # Add ITC eligibility if GSTIN present
        if invoice.gstin:
            query_parts.append("input tax credit eligibility")
        
        # Add cash limit context for high-value transactions
        if invoice.total_amount > 10000:
            query_parts.append("cash payment limits Section 40A(3)")
        
        # Add category-specific context
        if invoice.category == ExpenseCategory.FOOD_BEVERAGE:
            query_parts.append("Section 17(5) blocked credits")
        elif invoice.category == ExpenseCategory.TRAVEL:
            query_parts.append("travel expense deduction rules")
        elif invoice.category == ExpenseCategory.PROFESSIONAL_FEES:
            query_parts.append("professional fees TDS requirements")
        
        return " ".join(query_parts)

    
    def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for search query
        
        Args:
            query: Search query text
            
        Returns:
            3072-dimensional embedding vector
        """
        result = self.client.models.embed_content(
            model=self.embedding_model,
            contents=query
        )
        return result.embeddings[0].values
    
    def search_legal_docs(self, convex_client, query_embedding: List[float], 
                         limit: int = 3) -> List[Dict]:
        """
        Execute vector search and return results
        
        Args:
            convex_client: Convex client instance
            query_embedding: Query embedding vector
            limit: Maximum number of results
            
        Returns:
            List of search results
        """
        results = convex_client.query("legalDocs:searchLegalDocs", {
            "query_embedding": query_embedding,
            "limit": limit,
        })
        return results
    
    def format_legal_context(self, search_results: List[Dict]) -> str:
        """
        Format retrieved chunks into context string
        
        Args:
            search_results: List of search results
            
        Returns:
            Formatted legal context string with citations
        """
        if not search_results:
            return ""
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(
                f"[Source: {result['source_file']}, Page {result['page_number']}]\n"
                f"{result['chunk_text']}\n"
            )
        
        return "\n---\n".join(context_parts)
