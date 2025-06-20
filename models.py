from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tagline: Optional[str] = None
    logo_url: Optional[str] = None
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    fiscal_address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    currency: Optional[str] = None
    invoice_prefix: Optional[str] = None
    invoice_counter: Optional[int] = None
    payment_terms_amount: Optional[int] = None
    payment_terms_unit: Optional[str] = None
    bank_details: Optional[str] = None
    tax_rates: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    date_format: Optional[str] = None
    number_format: Optional[str] = None
    
class ProductCreate(BaseModel):
    name: str
    sku: str
    sale_price: float
    type: Optional[str] = None
    cost: Optional[float] = None
    stock: Optional[int] = None

class ProductRead(BaseModel):
    sku: str
    type: str
    cost: float
    name: str
    sale_price: float
    stock: int

    class Config:
        orm_mode = True
        
class ProductCreateFromUser(BaseModel):
    user_id: str
    type: str
    cost: float
    name: str
    sale_price: float
    stock: int