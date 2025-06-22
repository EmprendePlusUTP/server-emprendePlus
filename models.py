from datetime import date
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
    sale_date: date
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
    sale_date: date
    products: List[SaleProductInput]
    
class SaleUpdateInput(BaseModel):
    sale_date: Optional[date]
    products: Optional[List[SaleProductInput]]
    
class ProductUpdateInput(BaseModel):
    name: Optional[str]
    type: Optional[str]
    cost: Optional[float]
    sale_price: Optional[float]
    stock: Optional[int]
    
class FinanceCreate(BaseModel):
    date: date
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