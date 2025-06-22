from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
import uuid
from datetime import date


# ---------------------------
# User
# ---------------------------
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)  # Auth0 ID
    name: str

    # One user → one business
    business: Optional["Business"] = Relationship(back_populates="owner")
    
# ---------------------------
# Finance
# ---------------------------
class Finance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: UUID = Field(foreign_key="business.id", index=True)
    date: date
    type: str  # "income" o "expense"
    category: str
    subcategory: str
    amount: float
    description: Optional[str] = None

    # Relación opcional de vuelta a Business
    business: Optional["Business"] = Relationship(back_populates="finances")


class Budget(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID = Field(foreign_key="business.id", index=True)
    category: str
    subcategory: Optional[str] = None
    amount: float

    business: Optional["Business"] = Relationship(back_populates="budgets")

# ---------------------------
# Business
# ---------------------------
class Business(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: Optional[str] = ""
    owner_id: str = Field(foreign_key="user.id")
    
    finances: list[Finance] = Relationship(back_populates="business")
    budgets: List["Budget"] = Relationship(back_populates="business")

    # Identity
    tagline: Optional[str] = ""
    logo_url: Optional[str] = None

    # Tax info
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    fiscal_address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    # Invoicing config
    currency: str = "USD"
    invoice_prefix: Optional[str] = ""
    invoice_counter: int = 1
    payment_terms_amount: int = 30
    payment_terms_unit: str = "days"
    bank_details: Optional[str] = None
    tax_rates: Optional[str] = None

    # Localization
    timezone: str = "America/Panama"
    language: str = "es"
    date_format: str = "dd/mm/yyyy"
    number_format: str = "1.234,56"

    # Relationships
    products: List["Product"] = Relationship(back_populates="business")
    sales: List["Sale"] = Relationship(back_populates="business")
    owner: Optional[User] = Relationship(back_populates="business")


# ---------------------------
# Product
# ---------------------------
class Product(SQLModel, table=True):
    sku: str = Field(primary_key=True)
    business_id: UUID = Field(foreign_key="business.id")

    name: str
    type: Optional[str] = None
    cost: Optional[float] = None
    sale_price: float
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

    business: Optional["Business"] = Relationship(back_populates="products")

    sale_products: List["SaleProduct"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )


# ---------------------------
# Sale
# ---------------------------
class Sale(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID = Field(foreign_key="business.id")
    sale_date: date
    total: float

    business: Optional[Business] = Relationship(back_populates="sales")
    sale_products: List["SaleProduct"] = Relationship(
        back_populates="sale",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )


# ---------------------------
# SaleProduct
# ---------------------------
class SaleProduct(SQLModel, table=True):
    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    sale_id: UUID = Field(foreign_key="sale.id")
    product_id: str = Field(foreign_key="product.sku")
    quantity: int
    subtotal: float
    discount: Optional[float] = 0.0

    sale: Optional["Sale"] = Relationship(back_populates="sale_products")
    product: Optional["Product"] = Relationship(back_populates="sale_products")

    # Campos virtuales solo para serialización
    product_name: Optional[str] = None
    sale_price: Optional[float] = None


