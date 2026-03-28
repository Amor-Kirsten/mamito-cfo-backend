from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

import models
import schemas
from database import engine, get_db
from pdf_report import generate_daily_report, generate_receipt

# Table creation moved to setup_db.py to prevent Vercel Serverless boot crashing
# from DDL queries via Supabase Transaction Pooler.

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Removed os.makedirs("static", exist_ok=True) for Vercel compatibility
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_index():
    return FileResponse("static/index.html")

@app.get("/api/sales", response_model=List[schemas.SaleResponse])
def read_sales(response: Response, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    sales = db.query(models.Sale).offset(skip).limit(limit).all()
    
    response_list = []
    for s in sales:
        s_dict = {
            "id": s.id,
            "date": s.date,
            "total": s.total,
            "large": None,
            "small": None
        }
        for item in s.items:
            item_data = {
                "qty": item.qty,
                "total": item.total,
                "cash": item.cash,
                "mpesa": item.mpesa,
                "credit": item.credit
            }
            if item.tin_size == "800g":
                s_dict["large"] = item_data
            elif item.tin_size == "400g":
                s_dict["small"] = item_data
        response_list.append(s_dict)
    
    return response_list

@app.post("/api/sales")
def create_sale(sale: schemas.SaleCreate, db: Session = Depends(get_db)):
    db_sale = models.Sale(date=sale.date, total=sale.total)
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)

    if sale.large and sale.large.qty > 0:
        db_item = models.SaleItem(
            sale_id=db_sale.id,
            tin_size="800g",
            qty=sale.large.qty,
            cash=sale.large.cash or 0,
            mpesa=sale.large.mpesa or 0,
            credit=sale.large.credit or 0,
            total=sale.large.total
        )
        db.add(db_item)
    
    if sale.small and sale.small.qty > 0:
        db_item = models.SaleItem(
            sale_id=db_sale.id,
            tin_size="400g",
            qty=sale.small.qty,
            cash=sale.small.cash or 0,
            mpesa=sale.small.mpesa or 0,
            credit=sale.small.credit or 0,
            total=sale.small.total
        )
        db.add(db_item)
    
    db.commit()
    return {"message": "Success", "id": db_sale.id}

@app.delete("/api/sales/{sale_id}")
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    db_sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not db_sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    
    db.delete(db_sale)
    db.commit()
    return {"message": "Deleted"}

@app.get("/api/sales/report/daily")
def get_daily_pdf(date: str, db: Session = Depends(get_db)):
    sales = db.query(models.Sale).filter(models.Sale.date == date).all()
    pdf_bytes = generate_daily_report(date, sales)
    
    headers = {
        'Content-Disposition': f'attachment; filename="mamito_report_{date}.pdf"'
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)

@app.get("/api/sales/{sale_id}/receipt")
def get_receipt_pdf(sale_id: int, db: Session = Depends(get_db)):
    sale = db.query(models.Sale).filter(models.Sale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
        
    pdf_bytes = generate_receipt(sale)
    
    headers = {
        'Content-Disposition': f'attachment; filename="mamito_receipt_{sale_id}.pdf"'
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
