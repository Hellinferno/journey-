"""
Data Schemas
Pydantic models for invoice data and expense categories
"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ExpenseCategory(str, Enum):
    """Expense category classification"""
    OFFICE_SUPPLIES = "Office Supplies"
    TRAVEL = "Travel"
    FOOD_BEVERAGE = "Food & Beverage"
    ELECTRONICS = "Electronics"
    PROFESSIONAL_FEES = "Professional Fees"
    UTILITIES = "Utilities"
    RENT = "Rent"
    OTHER = "Other"


class InvoiceData(BaseModel):
    """Invoice data model"""
    vendor_name: str = Field(..., description="Name of the vendor/business")
    invoice_number: Optional[str] = Field(None, description="Invoice number if visible")
    date: Optional[str] = Field(None, description="Date of issue (YYYY-MM-DD)")
    total_amount: float = Field(..., description="Total amount including tax")
    tax_amount: float = Field(0.0, description="GST amount")
    gstin: Optional[str] = Field(None, description="GSTIN (15 characters)")
    currency: str = Field("INR", description="Currency code")
    category: ExpenseCategory = Field(..., description="Expense category")
    item_description: str = Field(..., description="Brief summary of items")
