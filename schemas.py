from pydantic import BaseModel
from typing import List, Optional

class SaleItemBase(BaseModel):
    qty: int
    total: float
    cash: Optional[float] = 0
    mpesa: Optional[float] = 0
    credit: Optional[float] = 0

class SaleItem(SaleItemBase):
    id: int
    sale_id: int
    tin_size: str

    class Config:
        orm_mode = True

class SaleSizeInput(BaseModel):
    qty: int
    total: float
    cash: Optional[float] = 0
    mpesa: Optional[float] = 0
    credit: Optional[float] = 0

class SaleCreate(BaseModel):
    date: str
    large: Optional[SaleSizeInput] = None
    small: Optional[SaleSizeInput] = None
    total: float

class SaleBase(BaseModel):
    id: int
    date: str
    total: float

class SaleResponse(SaleBase):
    large: Optional[SaleSizeInput] = None
    small: Optional[SaleSizeInput] = None

    class Config:
        orm_mode = True
