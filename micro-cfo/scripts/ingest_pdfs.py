"""
PDF Ingestion Pipeline for RAG Compliance Engine
Processes legal PDFs and stores chunks with embeddings in Convex
"""
import os
import time
import json
from typing import List, Dict
from pypdf import PdfReader
from google import genai
from convex import ConvexClient
from dotenv import load_dotenv


class PDFIngestionPipeline:
    """Pipeline for ingesting PDF documents into the RAG knowledge base"""
    
    def __init__(self, convex_url: str, api_key: str, progress_file: str = "ingestion_progress.json"):
        """
        Initialize the ingestion pipeline
        
        Args:
            convex_url: Convex deployment URL
            api_key: Google API key for embeddings
            progress_file: File to track ingestion progress
        """
        self.convex = ConvexClient(convex_url)
        self.client = genai.Client(api_key=api_key)
        self.embedding_model = "models/gemini-embedding-001"
        self.chunk_size = 1000
        self.overlap = 100
        self.progress_file = progress_file
        self.requests_per_minute = 90  # Stay under 100/min limit
        self.request_count = 0
        self.minute_start = time.time()

    
    def load_progress(self) -> Dict:
        """Load progress from file"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_progress(self, progress: Dict):
        """Save progress to file"""
        with open(self.progress_file, 'w') as f:
            json.dump(progress, f, indent=2)
    
    def rate_limit(self):
        """Implement rate limiting to stay under 100 requests/minute"""
        self.request_count += 1
        
        # Check if we've hit the per-minute limit
        if self.request_count >= self.requests_per_minute:
            elapsed = time.time() - self.minute_start
            if elapsed < 60:
                sleep_time = 60 - elapsed
                print(f"\n[RATE LIMIT] Sleeping for {sleep_time:.1f}s to respect API limits...")
                time.sleep(sleep_time)
            
            # Reset counter
            self.request_count = 0
            self.minute_start = time.time()

    
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
        Generate embedding with retry logic and rate limiting
        
        Args:
            text: Text to embed
            retries: Number of retry attempts
            
        Returns:
            3072-dimensional embedding vector
        """
        self.rate_limit()
        
        for attempt in range(retries):
            try:
                result = self.client.models.embed_content(
                    model=self.embedding_model,
                    contents=text
                )
                return result.embeddings[0].values
            except Exception as e:
                error_str = str(e)
                # Check if it's a quota error
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    print(f"\n[QUOTA ERROR] Daily quota exceeded. Please retry tomorrow.")
                    raise e
                
                if attempt == retries - 1:
                    raise e
                # Exponential backoff
                time.sleep(2 ** attempt)

    
    def ingest_document(self, pdf_path: str, category: str):
        """
        Complete ingestion pipeline for one PDF with progress tracking
        
        Args:
            pdf_path: Path to PDF file
            category: Document category ("GST" or "Income_Tax")
        """
        print(f"\n[PROCESSING] {pdf_path}...")
        source_file = os.path.basename(pdf_path)
        
        # Load progress
        progress = self.load_progress()
        processed_chunks = progress.get(source_file, 0)
        
        # Extract and chunk
        chunks = self.process_pdf(pdf_path, category)
        total_chunks = len(chunks)
        print(f"Created {total_chunks} chunks (resuming from chunk {processed_chunks + 1})")
        
        # Generate embeddings and store
        for i in range(processed_chunks, total_chunks):
            chunk = chunks[i]
            print(f"Processing chunk {i+1}/{total_chunks}...", end="\r")
            
            try:
                embedding = self.generate_embedding(chunk["text"])
                
                self.convex.mutation("legalDocs:addLegalDocument", {
                    "chunk_text": chunk["text"],
                    "source_file": source_file,
                    "page_number": chunk["page_number"],
                    "category": category,
                    "embedding": embedding,
                })
                
                # Update progress
                progress[source_file] = i + 1
                self.save_progress(progress)
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    print(f"\n[QUOTA EXCEEDED] Processed {i}/{total_chunks} chunks")
                    print(f"Progress saved. Run script again tomorrow to continue from chunk {i+1}")
                    return
                
                print(f"\n[ERROR] Error processing chunk {i+1}: {e}")
                continue
        
        print(f"\n[COMPLETED] {source_file}")
        # Clear progress for this file
        if source_file in progress:
            del progress[source_file]
            self.save_progress(progress)



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
    
    print("\n[SUCCESS] All documents ingested successfully!")


if __name__ == "__main__":
    main()
