import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

/**
 * Add a legal document chunk to the database with vector embedding
 */
export const addLegalDocument = mutation({
  args: {
    chunk_text: v.string(),
    source_file: v.string(),
    page_number: v.number(),
    category: v.string(),
    embedding: v.array(v.float64()),
  },
  handler: async (ctx, args) => {
    // Validate embedding dimensions (Gemini text-embedding-004 uses 3072 dimensions)
    if (args.embedding.length !== 3072) {
      throw new Error(
        `Invalid embedding dimensions: expected 3072, got ${args.embedding.length}`
      );
    }

    await ctx.db.insert("legal_docs", args);
  },
});

/**
 * Search legal documents using vector similarity
 * 
 * Performs semantic search over legal document chunks using vector embeddings.
 * Returns the most similar documents ordered by similarity score (descending).
 * 
 * @param query_embedding - 3072-dimensional embedding vector for the search query
 * @param limit - Maximum number of results to return (default: 3)
 * @param category - Optional filter by document category ("GST" or "Income_Tax")
 * @returns Array of matching documents with similarity scores, ordered by relevance
 */
export const searchLegalDocs = query({
  args: {
    query_embedding: v.array(v.float64()),
    limit: v.optional(v.number()),
    category: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    const limit = args.limit ?? 3;
    
    // Validate embedding dimensions
    if (args.query_embedding.length !== 3072) {
      throw new Error(
        `Invalid query embedding dimensions: expected 3072, got ${args.query_embedding.length}`
      );
    }
    
    // Build the vector search query
    const results = await ctx.db
      .query("legal_docs")
      .withSearchIndex("by_embedding", (q) => {
        // Start with vector similarity search
        let search = q.similar("embedding", args.query_embedding, limit);
        
        // Apply category filter if specified
        if (args.category) {
          search = search.filter((q) => q.eq("category", args.category));
        }
        
        return search;
      })
      .collect();
    
    // Map results to include all required fields and similarity score
    return results.map((doc) => ({
      chunk_text: doc.chunk_text,
      source_file: doc.source_file,
      page_number: doc.page_number,
      category: doc.category,
      score: doc._score, // Similarity score from vector search
    }));
  },
});
