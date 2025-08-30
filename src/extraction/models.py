from typing import Optional
from pydantic import BaseModel


class Product(BaseModel):
    """Represents a single product extracted from a receipt."""
    product_type: str
    product: str
    price: float
    quantity: float
    discount: Optional[float] = None
    discount2: Optional[float] = None


class Receipt(BaseModel):
    """Represents a complete receipt with all extracted products."""
    market: str
    branch: str
    invoice: Optional[str] = None
    total: Optional[float] = None
    date: Optional[str] = None
    products: list[Product]


class ExtractionResult(BaseModel):
    """Result of PDF extraction operation."""
    success: bool
    receipt: Optional[Receipt] = None
    error_message: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str