from sqlmodel import Session, select
from db.models import Business, Product, Sale, SaleProduct, Finance, Budget, User
from faker import Faker
from datetime import datetime
import random
from uuid import uuid4

fake = Faker()

PRODUCTS = 10
SALES = 15
FINANCES = 10
BUDGETS = 2

from datetime import timezone, timedelta

def create_random_date(start_date='-6M', end_date='now'):
    dt = fake.date_time_between(start_date=start_date, end_date=end_date)
    return dt.replace(tzinfo=timezone(timedelta(hours=-5)))


def generate_dummy_products(business: Business, session: Session, quantity: int = 10) -> list[Product]:
    products = []
    for _ in range(quantity):
        cost = round(random.uniform(5, 100), 2)
        sale_price = round(cost * random.uniform(1.2, 1.8), 2)
        product = Product(
            sku=fake.unique.lexify("PRD????"),
            business_id=business.id,
            name=fake.word().capitalize(),
            type=random.choice(["physical", "digital"]),
            cost=cost,
            sale_price=sale_price,
            stock=random.randint(10, 100),
            description=fake.sentence(),
            discount=round(random.uniform(0, 0.3), 2),
            min_stock_alert=random.randint(5, 20),
            supplier=fake.company(),
            status=random.choice(["active", "inactive"]),
            color=random.choice(["red", "blue", "green", "black"]),
            width=round(random.uniform(1.0, 10.0), 2),
            height=round(random.uniform(1.0, 10.0), 2),
            depth=round(random.uniform(1.0, 10.0), 2),
            weight=round(random.uniform(0.1, 5.0), 2),
            tax_rate=random.choice([0.07, 0.10]),
            created_at=str(datetime.now()),
            updated_at=str(datetime.now()),
            rating=round(random.uniform(1.0, 5.0), 1),
            image_path=fake.image_url()
        )
        session.add(product)
        products.append(product)
    session.commit()
    return products

def generate_dummy_sales(business: Business, products: list[Product], session: Session, quantity: int = 15):
    for _ in range(quantity):
        sale_date = create_random_date()
        selected_products = random.sample(products, k=random.randint(1, 4))
        total = 0.0

        invoice_id = f"{business.invoice_prefix}{business.invoice_counter}"
        business.invoice_counter += 1
        session.add(business)

        sale = Sale(
            business_id=business.id,
            sale_date=sale_date,
            invoice_id=invoice_id,
            total=0.0
        )
        session.add(sale)
        session.commit()
        session.refresh(sale)

        for prod in selected_products:
            qty = random.randint(1, 5)
            subtotal = round(prod.sale_price * qty, 2)
            sale_product = SaleProduct(
                sale_id=sale.id,
                product_id=prod.sku,
                quantity=qty,
                subtotal=subtotal,
                discount=round(random.uniform(0, 0.2), 2),
                product_name=prod.name,
                sale_price=prod.sale_price
            )
            total += subtotal
            session.add(sale_product)

        sale.total = round(total, 2)
        session.add(sale)

    session.commit()


def generate_dummy_finances(business: Business, session: Session, quantity: int = 10):
    for _ in range(quantity):
        finance = Finance(
            business_id=business.id,
            date=create_random_date(),
            type=random.choice(["income", "expense"]),
            category=random.choice(["marketing", "logistics", "admin", "operations"]),
            subcategory=fake.word(),
            amount=round(random.uniform(50, 1500), 2),
            description=fake.sentence()
        )
        session.add(finance)
    session.commit()


def generate_dummy_budgets(business: Business, session: Session, quantity: int = 2):
    for _ in range(quantity):
        budget = Budget(
            business_id=business.id,
            category=random.choice(["marketing", "logistics", "admin"]),
            subcategory=random.choice([None, fake.word()]),
            amount=round(random.uniform(1000, 5000), 2)
        )
        session.add(budget)
    session.commit()


def generate_dummy_data_for_user(
    user_id: str,
    session: Session,
    products_count,
    sales_count,
    finances_count,
    budgets_count
) -> str:
    business = session.exec(select(Business).where(Business.owner_id == user_id)).first()
    if not business:
        raise ValueError("No se encontró ningún negocio asociado a este usuario.")

    # Obtener productos existentes
    existing_products = session.exec(
        select(Product).where(Product.business_id == business.id)
    ).all()

    # Generar nuevos si se pidió
    new_products = []
    if products_count > 0:
        new_products = generate_dummy_products(business, session, products_count)

    # Combinar todos los productos
    all_products = existing_products + new_products

    # Solo generar ventas si hay productos
    if all_products and sales_count > 0:
        generate_dummy_sales(business, all_products, session, sales_count)

    if finances_count > 0:
        generate_dummy_finances(business, session, finances_count)

    if budgets_count > 0:
        generate_dummy_budgets(business, session, budgets_count)

    return str(business.id)

