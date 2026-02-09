"""
PDF Ingestion Pipeline for RAG Compliance Engine
Processes legal PDFs and stores chunks with embeddings in Convex
"""
import os
import time
from typing import List, Dict
from pypdf import PdfReader
from google import genai
from convex import ConvexClient
from dotenv import load_dotenv


class PDFIngestionPipeline:
    """Pipeline for ingesting PDF documents into the RAG knowledge base"""
    
    def __init__(self, convex_url: str, api_key: str):
        """
        Initialize the ingestion pipeline
        
        Args:
            convex_url: Convex deployment URL
            api_key: Google API key for embeddings
        """
        self.convex = ConvexClient(convex_url)
        self.client = genai.Client(api_key=api_key)
        self.embedding_model = "text-embedding-004"
        self.chunk_size = 1000
        self.overlap = 100

    
    def process_pdf(self, pdf_path: str, category: str) -> List[Dict]:
        """
        Extract text from PDF and create chunks
        
        Args:
            pdf_path: Path to the PDF file
            category: Document category ("GST" or "Income_Tax")
            
        Returns:
            List of chunk dictionaries with text and page numbers
        """
        reader = PdfReader(pdf_path)
        chunks = []
        
        for page_num, page in enumerate(reader.pages, start=1):
            text = page.extract_text()
            
            # Skip empty or whitespace-only pages
            if not text or text.strip() == "":
                continue
            
            # Chunk the page text
            page_chunks = self.chunk_text(text, page_num)
            chunks.extend(page_chunks)
        
        return chunks

    
    def chunk_text(self, text: str, page_num: int) -> List[Dict]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            page_num: Page number for metadata
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        start = 0
        
        while start < len(text):
            # Calculate end position
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end]
            
            # Skip empty chunks and chunks with only whitespace/control characters
            # Check if chunk has any printable or non-whitespace characters
            if chunk.strip() and any(c.isprintable() and not c.isspace() for c in chunk):
                chunks.append({
                    "text": chunk,
                    "page_number": page_num,
                })
            
            # If this chunk reached the end of the text, we're done
            if end >= len(text):
                break
            
            # Move forward by (chunk_size - overlap) to create overlap
            start += (self.chunk_size - self.overlap)
        
        return chunks

    
    def generate_embedding(self, text: str, retries: int = 3) -> List[float]:
        """
        Generate embedding with retry logic
        
        Args:
            text: Text to embed
            retries: Number of retry attempts
            
        Returns:
            768-dimensional embedding vector
        """
        for attempt in range(retries):
            try:
                result = self.client.models.embed_content(
                    model=self.embedding_model,
                    contents=text
                )
                return result.embeddings[0].values
            except Exception as e:
                if attempt == retries - 1:
                    raise e
                # Exponential backoff
                time.sleep(2 ** attempt)

    
    def ingest_document(self, pdf_path: str, category: str):
        """
        Complete ingestion pipeline for one PDF
        
        Args:
            pdf_path: Path to PDF file
            category: Document category ("GST" or "Income_Tax")
        """
        print(f"\n📘 Processing {pdf_path}...")
        source_file = os.path.basename(pdf_path)
        
        # Extract and chunk
        chunks = self.process_pdf(pdf_path, category)
        print(f"Created {len(chunks)} chunks")
        
        # Generate embeddings and store
        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i+1}/{len(chunks)}...", end="\r")
            
            try:
                embedding = self.generate_embedding(chunk["text"])
                
                self.convex.mutation("legalDocs:addLegalDocument", {
                    "chunk_text": chunk["text"],
                    "source_file": source_file,
                    "page_number": chunk["page_number"],
                    "category": category,
                    "embedding": embedding,
                })
            except Exception as e:
                print(f"\n⚠️ Error processing chunk {i+1}: {e}")
                continue
        
        print(f"\n✅ Completed {source_file}")



def main():
    """Main function to ingest both PDF documents"""
    # Load environment variables
    load_dotenv()
    
    convex_url = os.getenv("CONVEX_URL")
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not convex_url or not api_key:
        raise ValueError("Missing required environment variables: CONVEX_URL and GOOGLE_API_KEY")
    
    pipeline = PDFIngestionPipeline(convex_url, api_key)
    
    # Get the parent directory (workspace root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.dirname(os.path.dirname(script_dir))
    
    # Ingest both PDFs from workspace root
    pdf1_path = os.path.join(workspace_root, "a2017-12.pdf")
    pdf2_path = os.path.join(workspace_root, "Income-tax-Act-2025.pdf")
    
    pipeline.ingest_document(pdf1_path, "GST")
    pipeline.ingest_document(pdf2_path, "Income_Tax")
    
    print("\n🎉 All documents ingested successfully!")


if __name__ == "__main__":
    main()
