import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

// This is an "Upsert" operation
export const getOrCreateUser = mutation({
    args: {
        telegram_id: v.string(),
        full_name: v.string()
    },
    handler: async (ctx, args) => {
        // 1. Check if user exists
        const existingUser = await ctx.db
            .query("users")
            .withIndex("by_telegram_id", (q) => q.eq("telegram_id", args.telegram_id))
            .first();

        if (existingUser) {
            return existingUser._id;
        }

        // 2. Create if not exists
        const newUserId = await ctx.db.insert("users", {
            telegram_id: args.telegram_id,
            full_name: args.full_name,
            joined_at: new Date().toISOString(),
            role: "user",
        });

        return newUserId;
    },
});

export const logMessage = mutation({
    args: { userId: v.id("users"), text: v.string(), direction: v.string() },
    handler: async (ctx, args) => {
        await ctx.db.insert("messages", {
            user_id: args.userId,
            text: args.text,
            direction: args.direction as "inbound" | "outbound",
            timestamp: new Date().toISOString(),
        });
    },
});
