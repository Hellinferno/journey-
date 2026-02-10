import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
    users: defineTable({
        telegram_id: v.string(),
        full_name: v.string(),
        joined_at: v.string(),
        role: v.string(),
    }).index("by_telegram_id", ["telegram_id"]),
    messages: defineTable({
        user_id: v.id("users"),
        text: v.string(),
        direction: v.string(), // "inbound" | "outbound"
        timestamp: v.string(),
    }),
    invoices: defineTable({
        telegram_id: v.string(),
        vendor: v.string(),
        amount: v.number(),
        gstin: v.optional(v.string()), // Optional fields
        date: v.optional(v.string()),
        // New Phase 3 Fields
        category: v.optional(v.string()),
        compliance_flags: v.optional(v.array(v.string())),
        status: v.string(),
        timestamp: v.string(),
    }),
    // RAG Knowledge Base
    legal_docs: defineTable({
        chunk_text: v.string(),
        source_file: v.string(),
        page_number: v.number(),
        category: v.string(), // "GST" or "Income_Tax"
        embedding: v.array(v.float64()),
    })
        .vectorIndex("by_embedding", {
            vectorField: "embedding",
            dimensions: 3072, // gemini-embedding-001 (3072 dimensions)
            filterFields: ["category", "source_file"],
        })
        .index("by_source", ["source_file"])
        .index("by_category", ["category"]),
});
