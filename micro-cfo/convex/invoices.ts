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
    },
    handler: async (ctx, args) => {
        await ctx.db.insert("invoices", {
            telegram_id: args.telegram_id,
            vendor: args.vendor,
            amount: args.amount,
            gstin: args.gstin,
            date: args.date,
            status: args.status,
            timestamp: new Date().toISOString(),
        });
    },
});
