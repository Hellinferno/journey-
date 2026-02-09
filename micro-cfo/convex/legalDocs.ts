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
    // Validate embedding dimensions
    if (args.embedding.length !== 768) {
      throw new Error(
        `Invalid embedding dimensions: expected 768, got ${args.embedding.length}`
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
    const limit = args.limit ?? 3;

    // Build filter if category specified
    const filter = args.category
      ? (q: any) => q.eq("category", args.category)
      : undefined;

    const results = await ctx.db
      .query("legal_docs")
      .withSearchIndex("by_embedding", (q) =>
        q
          .similar("embedding", args.query_embedding, limit)
          .filter(filter)
      )
      .collect();

    return results.map((doc) => ({
      chunk_text: doc.chunk_text,
      source_file: doc.source_file,
      page_number: doc.page_number,
      category: doc.category,
      score: doc._score, // Similarity score from vector search
    }));
  },
});
