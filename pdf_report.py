from fpdf import FPDF
import models
from typing import List
import os

class PDF(FPDF):
    def header(self):
        logo_path = r"C:\Users\san\Downloads\Mamito Logo.JPG"
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 33)
        self.set_font("helvetica", "B", 15)
        self.cell(80)
        self.cell(40, 10, "Mamito Sales Daily Report", border=0, align="C")
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

def generate_daily_report(date: str, sales: List[models.Sale]) -> bytes:
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    
    pdf.cell(0, 10, f"Date: {date}", ln=1)
    pdf.ln(5)
    
    total_revenue = 0
    total_large = 0
    total_small = 0
    cash_total = 0
    mpesa_total = 0
    credit_total = 0

    # Table Header
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(10, 10, "ID", 1)
    pdf.cell(20, 10, "Size", 1)
    pdf.cell(15, 10, "Qty", 1)
    pdf.cell(25, 10, "Cash", 1)
    pdf.cell(25, 10, "M-Pesa", 1)
    pdf.cell(25, 10, "Credit", 1)
    pdf.cell(30, 10, "Total", 1, ln=1)
    
    pdf.set_font("helvetica", size=9)
    for sale in sales:
        total_revenue += sale.total
        for item in sale.items:
            pdf.cell(10, 8, str(sale.id), 1)
            pdf.cell(20, 8, item.tin_size, 1)
            pdf.cell(15, 8, str(item.qty), 1)
            pdf.cell(25, 8, str(item.cash), 1)
            pdf.cell(25, 8, str(item.mpesa), 1)
            pdf.cell(25, 8, str(item.credit), 1)
            pdf.cell(30, 8, str(item.total), 1, ln=1)
            
            cash_total += item.cash
            mpesa_total += item.mpesa
            credit_total += item.credit
            if item.tin_size == "800g":
                total_large += item.qty
            elif item.tin_size == "400g":
                total_small += item.qty

    pdf.ln(10)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 10, "Summary", ln=1)
    pdf.set_font("helvetica", size=10)
    pdf.cell(0, 8, f"Total Revenue: KES {total_revenue}", ln=1)
    pdf.cell(0, 8, f"800g Tins Sold: {total_large}", ln=1)
    pdf.cell(0, 8, f"400g Tins Sold: {total_small}", ln=1)
    pdf.ln(5)
    pdf.cell(0, 8, f"Total Cash: KES {cash_total}", ln=1)
    pdf.cell(0, 8, f"Total M-Pesa: KES {mpesa_total}", ln=1)
    pdf.cell(0, 8, f"Total Credit: KES {credit_total}", ln=1)
    
    return bytes(pdf.output())

def generate_receipt(sale: models.Sale) -> bytes:
    pdf = PDF()
    pdf.add_page()
    
    pdf.set_font("helvetica", size=12)
    pdf.cell(0, 10, f"Receipt ID: {sale.id}", ln=1)
    pdf.cell(0, 10, f"Date: {sale.date}", ln=1)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(50, 10, "Item", 1)
    pdf.cell(30, 10, "Qty", 1)
    pdf.cell(40, 10, "Amount (KES)", 1, ln=1)
    
    pdf.set_font("helvetica", size=10)
    cash_total = 0
    mpesa_total = 0
    credit_total = 0
    
    for item in sale.items:
        pdf.cell(50, 8, f"{item.tin_size} Tin", 1)
        pdf.cell(30, 8, str(item.qty), 1)
        pdf.cell(40, 8, str(item.total), 1, ln=1)
        
        cash_total += item.cash
        mpesa_total += item.mpesa
        credit_total += item.credit
        
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, f"Grand Total: KES {sale.total}", ln=1)
    
    pdf.set_font("helvetica", size=10)
    pdf.cell(0, 6, "Payment Breakdown:", ln=1)
    pdf.set_font("helvetica", size=9)
    if cash_total > 0:
        pdf.cell(0, 6, f"Cash: KES {cash_total}", ln=1)
    if mpesa_total > 0:
        pdf.cell(0, 6, f"M-Pesa: KES {mpesa_total}", ln=1)
    if credit_total > 0:
        pdf.cell(0, 6, f"Credit: KES {credit_total}", ln=1)
        
    pdf.ln(10)
    pdf.set_font("helvetica", "I", 10)
    pdf.cell(0, 10, "Thank you for shopping with Mamito!", align="C")
    
    return bytes(pdf.output())
