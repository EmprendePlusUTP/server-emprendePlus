from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
import uuid
from datetime import date

# ---------------------------
# Tabla de enlace muchos a muchos entre Business y Product
# ---------------------------
class BusinessProductLink(SQLModel, table=True):
    business_id: uuid.UUID = Field(foreign_key="business.id", primary_key=True)
    product_id: uuid.UUID = Field(foreign_key="product.id", primary_key=True)


# ---------------------------
# Usuario (User)
# ---------------------------
class User(SQLModel, table=True):
    id: str = Field(primary_key=True)  # ID proveniente de Auth0
    name: str
    businesses: List["Business"] = Relationship(back_populates="owner")
    


# ---------------------------
# Negocio (Business)
# ---------------------------
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from uuid import UUID, uuid4

class Business(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    description: Optional[str] = ""
    owner_id: str = Field(foreign_key="user.id")

    # Identidad
    tagline: Optional[str] = ""
    logo_url: Optional[str] = None  # (recomendado subir a S3 o similar)

    # Datos fiscales
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    fiscal_address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    # Configuración de facturación
    currency: str = "USD"
    invoice_prefix: Optional[str] = ""
    invoice_counter: int = 1
    payment_terms_amount: int = 30
    payment_terms_unit: str = "días"
    bank_details: Optional[str] = None
    tax_rates: Optional[str] = None  # ejemplo: "IVA:21%, IGV:18%"

    # Ajustes avanzados
    timezone: str = "America/Panama"
    language: str = "es"
    date_format: str = "dd/mm/yyyy"
    number_format: str = "1.234,56"

    
    # Relación muchos a muchos con Product a través del link table
    products: List["Product"] = Relationship(
        back_populates="business", link_model=BusinessProductLink
    )
    
    sales: List["Sale"] = Relationship(back_populates="business")
    owner: Optional[User] = Relationship(back_populates="businesses")


# ---------------------------
# Producto (Product)
# Nota: Se ha quitado el campo business_id
# ---------------------------
class Product(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    Tipo: str
    Costo: float
    name: str
    precioVenta: float
    stock: int

    # Relación muchos a muchos con Business mediante la tabla de asociación.
    business: List[Business] = Relationship(
        back_populates="products", link_model=BusinessProductLink
    )
    
    # Relación: Un producto puede estar en muchas entradas de ventas (SaleProduct)
    sale_products: List["SaleProduct"] = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )


# ---------------------------
# Venta (Sale)
# ---------------------------
class Sale(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    # La venta sigue vinculándose a un negocio directamente
    business_id: uuid.UUID = Field(foreign_key="business.id")
    sale_date: date
    total: float

    business: Optional[Business] = Relationship(back_populates="sales")
    sale_products: List["SaleProduct"] = Relationship(
        back_populates="sale",
        sa_relationship_kwargs={"cascade": "all, delete"}
    )


# ---------------------------
# Producto de Venta (SaleProduct)
# ---------------------------
class SaleProduct(SQLModel, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    sale_id: uuid.UUID = Field(foreign_key="sale.id")
    product_id: uuid.UUID = Field(foreign_key="product.id")
    subtotal: float

    sale: Optional[Sale] = Relationship(back_populates="sale_products")
    product: Optional[Product] = Relationship(back_populates="sale_products")