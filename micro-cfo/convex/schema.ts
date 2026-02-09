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
});
