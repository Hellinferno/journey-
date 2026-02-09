import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const add = mutation({
    args: {
        telegram_id: v.string(),
        vendor: v.string(),
        amount: v.number(),
        gstin: v.optional(v.string()),
        date: v.optional(v.string()),
        status: v.string(),
        // New Phase 3 Args
        category: v.optional(v.string()),
        compliance_flags: v.optional(v.array(v.string())),
    },
    handler: async (ctx, args) => {
        await ctx.db.insert("invoices", {
            ...args,
            timestamp: new Date().toISOString(),
        });
    },
});
