from datetime import date, datetime, time

from typing import List, Optional
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

class ProductRead(BaseModel):
    sku: str
    type: str
    cost: float
    name: str
    sale_price: float
    stock: int

    class Config:
        from_attributes = True
        
class ProductCreateFromUser(BaseModel):
    user_id: str
    type: str
    cost: float
    name: str
    sale_price: float
    stock: int
    
    
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
    
class FinanceCreate(BaseModel):
    date: datetime
    type: str
    category: str
    subcategory: str
    amount: float
    description: Optional[str] = None

class FinanceRead(FinanceCreate):
    id: int

    class Config:
        # Para que Pydantic extraiga atributos de SQLModel/ORM automáticamente
        from_attributes = True
        
class BudgetCreate(BaseModel):
    category: str
    subcategory: Optional[str] = None
    amount: float

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
