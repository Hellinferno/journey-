from pydantic import BaseModel, Field
from typing import Optional

class InvoiceData(BaseModel):
    vendor_name: str = Field(..., description="Name of the shop/business")
    invoice_number: Optional[str] = Field(None, description="Invoice number if visible")
    date: Optional[str] = Field(None, description="Date of issue")
    total_amount: float = Field(..., description="Final total amount to pay")
    tax_amount: float = Field(0.0, description="Total GST amount")
    gstin: Optional[str] = Field(None, description="GSTIN (15 chars) if visible")
    currency: str = Field("INR", description="Currency code (INR/USD)")
