from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from db.models import Business, Budget, Finance, Product, Sale, SaleProduct
from db.connection import get_session
from io import StringIO, BytesIO
import csv, zipfile

router = APIRouter()

def to_csv_string(data, headers):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for item in data:
        writer.writerow([getattr(item, h) for h in headers])
    return output.getvalue()

@router.get("/business/export")
def export_business_data(business_id: str, session: Session = Depends(get_session)):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        
        # Exportar Business (uno solo)
        business = session.query(Business).filter(Business.id == business_id).first()
        if business:
            csv_str = to_csv_string([business], [c.name for c in Business.__table__.columns])
            zip_file.writestr("business.csv", csv_str)

        # Exportar Finance
        finances = session.query(Finance).filter(Finance.business_id == business_id).all()
        csv_str = to_csv_string(finances, [c.name for c in Finance.__table__.columns])
        zip_file.writestr("finances.csv", csv_str)

        # Exportar Budget
        budgets = session.query(Budget).filter(Budget.business_id == business_id).all()
        csv_str = to_csv_string(budgets, [c.name for c in Budget.__table__.columns])
        zip_file.writestr("budgets.csv", csv_str)

        # Exportar Product
        products = session.query(Product).filter(Product.business_id == business_id).all()
        csv_str = to_csv_string(products, [c.name for c in Product.__table__.columns])
        zip_file.writestr("products.csv", csv_str)

        # Exportar Sale
        sales = session.query(Sale).filter(Sale.business_id == business_id).all()
        csv_str = to_csv_string(sales, [c.name for c in Sale.__table__.columns])
        zip_file.writestr("sales.csv", csv_str)

        # Exportar SaleProduct (solo los que pertenecen a esas ventas)
        sale_ids = [s.id for s in sales]
        sale_products = session.query(SaleProduct).filter(SaleProduct.sale_id.in_(sale_ids)).all()
        csv_str = to_csv_string(sale_products, [c.name for c in SaleProduct.__table__.columns])
        zip_file.writestr("sale_products.csv", csv_str)

    zip_buffer.seek(0)
    return StreamingResponse(zip_buffer, media_type="application/zip", headers={
        "Content-Disposition": f"attachment; filename=business_{business_id}.zip"
    })