# Phase 3 Compliance Testing Guide

## Pre-Testing Setup

### 1. Deploy Convex Schema
```bash
cd micro-cfo
npx convex dev
```
Wait for the message: "Schema migration complete"

### 2. Restart the Bot
```bash
START_BOT_CLEAN.bat
```

## Test Cases

### Test 1: Food & Beverage (ITC Blocked)
**Expected Behavior**: Should flag Section 17(5) ITC blocking

**Test Invoice**: Any restaurant/cafe bill
- Send a photo of a food invoice
- Expected flags:
  - 🚫 ITC Blocked: Food & Beverages (Sec 17(5))
  - Status: `blocked`

### Test 2: Invalid GSTIN Format
**Expected Behavior**: Should detect invalid GSTIN

**Test Invoice**: Create/modify an invoice with wrong GSTIN
- Valid format: `29AABCT1332L1ZV` (15 chars)
- Invalid format: `123456789` (too short)
- Expected flags:
  - ❌ Invalid GSTIN Format
  - Status: `review_needed`

### Test 3: Unusual Tax Rate
**Expected Behavior**: Should warn about non-standard GST rates

**Test Invoice**: Invoice with 10% tax (not 5/12/18/28%)
- Expected flags:
  - ⚠️ Unusual Tax Rate: 10.0% (Expected 5/12/18/28%)

### Test 4: High-Value Cash Payment
**Expected Behavior**: Should flag Section 40A(3) concern

**Test Invoice**: Any invoice > ₹10,000
- Expected flags:
  - ⚠️ Cash Payment > ₹10k? Verify Section 40A(3) compliance.

### Test 5: High-Value "Other" Expense
**Expected Behavior**: Should request business purpose verification

**Test Invoice**: Miscellaneous expense > ₹5,000
- Category: Other
- Expected flags:
  - ⚠️ Verify business purpose for 'Other' expense > ₹5k

### Test 6: Compliant Invoice
**Expected Behavior**: No flags, clean approval

**Test Invoice**: Office supplies with valid GSTIN and standard tax
- Category: Office Supplies
- GSTIN: Valid format
- Tax: 18%
- Amount: < ₹10,000
- Expected: ✅ Status: `compliant`, No flags

## Verification Checklist

After each test, verify:
- [ ] Category is correctly identified
- [ ] Compliance flags appear in bot response
- [ ] Status icon matches severity (✅ vs ⚠️)
- [ ] Data is saved to Convex with compliance_flags array
- [ ] Item description is extracted

## Database Verification

Check Convex dashboard:
```
https://dashboard.convex.dev
```

Navigate to: `invoices` table

Verify new fields exist:
- `category` (string)
- `compliance_flags` (array)
- `status` (should be: compliant/review_needed/blocked)

## Common Issues

### Issue: "category field missing" error
**Solution**: Redeploy Convex schema with `npx convex dev`

### Issue: AI not extracting category
**Solution**: Check Gemini API key has access to gemini-2.5-flash

### Issue: Compliance flags not showing
**Solution**: Verify `app/compliance.py` is imported in `bot.py`

## Success Criteria

✅ All 6 test cases pass
✅ Compliance flags appear correctly
✅ Data persists in Convex
✅ No Python errors in bot_debug.log
✅ Status reflects compliance state

---
**Ready to Test**: Yes ✅
