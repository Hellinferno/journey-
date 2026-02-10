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
 */
export const searchLegalDocs = query({
  args: {
    query_embedding: v.array(v.float64()),
    limit: v.optional(v.number()),
    category: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    // TODO: Implement proper vector search once PDFs are ingested
    // For now, return empty results to allow hard rules validation to work
    // The system will gracefully fall back to hard rules only
    
    // Check if there are any documents in the database
    const count = await ctx.db.query("legal_docs").take(1);
    
    if (count.length === 0) {
      // No documents ingested yet, return empty array
      return [];
    }
    
    // If documents exist, return a simple query (not vector search yet)
    // This is a temporary solution until vector search API is properly configured
    const limit = args.limit ?? 3;
    const results = await ctx.db
      .query("legal_docs")
      .filter((q) => 
        args.category ? q.eq(q.field("category"), args.category) : true
      )
      .take(limit);

    return results.map((doc) => ({
      chunk_text: doc.chunk_text,
      source_file: doc.source_file,
      page_number: doc.page_number,
      category: doc.category,
      score: 0, // Placeholder score
    }));
  },
});
