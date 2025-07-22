from datetime import date, datetime, time

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from pydantic import field_validator
from utils.sanitization.validator import validate_safe_text

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
    @field_validator(
        "name", "description", "tagline", "legal_name", "tax_id", "fiscal_address",
        "phone", "email", "currency", "invoice_prefix", "payment_terms_unit",
        "bank_details", "tax_rates", "timezone", "language", "date_format", "number_format",
        mode="before")
    
    def sanitize_strings(cls, v, info):
        if v is None:
            return v
        return validate_safe_text(v, info.field_name)
    
class ProductCreate(BaseModel):
    sku: str
    name: str
    sale_price: float
    type: Optional[str] = None
    cost: Optional[float] = None
    stock: Optional[int] = None
    description: Optional[str] = None
    discount: Optional[float] = None
    min_stock_alert: Optional[int] = None
    supplier: Optional[str] = None
    status: Optional[str] = None
    color: Optional[str] = None
    width: Optional[float] = None
    height: Optional[float] = None
    depth: Optional[float] = None
    weight: Optional[float] = None
    tax_rate: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    rating: Optional[float] = None

    @field_validator(
        "sku", "name", "type", "description", "supplier", "status", "color",
        mode="before")
    
    def sanitize_fields(cls, v, info):
        if v is None:
            return v
        return  validate_safe_text(v, info.field_name)
class ProductRead(BaseModel):
    sku: str
    type: str
    cost: float
    name: str
    sale_price: float
    stock: int

    class Config:
        from_attributes = True
            
class SaleProductRead(BaseModel):
    product_id: str
    quantity: int
    subtotal: float
    discount: Optional[float] = 0.0 
    product_name: Optional[str]
    sale_price: Optional[float]

    class Config:
        from_attributes = True

class SaleRead(BaseModel):
    id: UUID
    invoice_id: str
    sale_date: datetime
    total: float
    sale_products: List[SaleProductRead]

    class Config:
        from_attributes = True
        
class SaleProductInput(BaseModel):
    product_id: str
    quantity: int
    subtotal: float
    discount: Optional[float] = 0.0
    

class SaleCreateInput(BaseModel):
    sale_date: datetime
    products: List[SaleProductInput]
    
class SaleUpdateInput(BaseModel):
    sale_date: Optional[datetime]
    products: Optional[List[SaleProductInput]]
    
class ProductUpdateInput(BaseModel):
    name: Optional[str]
    type: Optional[str]
    cost: Optional[float]
    sale_price: Optional[float]
    stock: Optional[int]
    min_stock_alert: Optional[int]
    
    @field_validator("name", "type", mode="before")
    def sanitize_str_fields(cls, v, info):
        if v is None:
            return v
        return  validate_safe_text(v, info.field_name)
    
    
class FinanceCreate(BaseModel):
    date: datetime
    type: str
    category: str
    subcategory: str
    amount: float
    description: Optional[str] = None
    
    @field_validator("type", "category", "subcategory", "description", mode="before")
    def sanitize_str_fields(cls, v, info):
        if v is None:
            return v
        return  validate_safe_text(v, info.field_name)

class FinanceRead(FinanceCreate):
    id: int

    class Config:
        # Para que Pydantic extraiga atributos de SQLModel/ORM automáticamente
        from_attributes = True
        
class BudgetCreate(BaseModel):
    category: str
    subcategory: Optional[str] = None
    amount: float
    
    @field_validator("category", "subcategory", mode="before")
    
    def sanitize_str_fields(cls, v, info):
        if v is None:
            return v
        return  validate_safe_text(v, info.field_name)

class BudgetRead(BudgetCreate):
    id: UUID

    class Config:
        from_attributes = True

class MonthlySalesComparison(BaseModel):
    month: str
    primary: float 
    secondary: float     
class StarProductComparison(BaseModel):
    name: str
    total_value: float
    monthly_comparison: list[MonthlySalesComparison]
