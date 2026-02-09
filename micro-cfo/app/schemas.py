from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class ExpenseCategory(str, Enum):
    OFFICE_SUPPLIES = "Office Supplies"
    TRAVEL = "Travel"
    FOOD_BEVERAGE = "Food & Beverage"  # High risk for blocked ITC
    ELECTRONICS = "Electronics"
    PROFESSIONAL_FEES = "Professional Fees"
    UTILITIES = "Utilities"
    RENT = "Rent"
    OTHER = "Other"

class InvoiceData(BaseModel):
    vendor_name: str = Field(..., description="Name of the shop/business")
    invoice_number: Optional[str] = Field(None, description="Invoice number if visible")
    date: Optional[str] = Field(None, description="Date of issue")
    total_amount: float = Field(..., description="Final total amount to pay")
    tax_amount: float = Field(0.0, description="Total GST amount")
    gstin: Optional[str] = Field(None, description="GSTIN (15 chars) if visible")
    currency: str = Field("INR", description="Currency code (INR/USD)")
    # New Fields for Phase 3
    category: ExpenseCategory = Field(..., description="Type of expense")
    item_description: str = Field(..., description="Brief summary of items bought")
