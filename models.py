from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True)
    total = Column(Float, default=0.0)

    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")

class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"))
    tin_size = Column(String) # "800g" or "400g"
    qty = Column(Integer)
    cash = Column(Float, default=0)
    mpesa = Column(Float, default=0)
    credit = Column(Float, default=0)
    total = Column(Float, default=0)

    sale = relationship("Sale", back_populates="items")
