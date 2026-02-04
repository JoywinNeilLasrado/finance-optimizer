import pandas as pd
from fpdf import FPDF
import base64

def generate_suggestions(df, budget_df):
    suggestions = []
    
    expenses = df[df['type'] == 'Expense']
    income = df[df['type'] == 'Income']['amount'].sum()
    total_expense = expenses['amount'].sum()
    
    # 1. Savings Rate Check
    savings_rate = (income - total_expense) / income * 100 if income > 0 else 0
    if savings_rate < 20:
        suggestions.append(f"⚠️ **Low Savings Rate**: You are saving only {savings_rate:.1f}%. Aim for at least 20%.")
    else:
        suggestions.append(f"✅ **Good Job**: Your savings rate is healthy at {savings_rate:.1f}%.")

    # 2. Budget Overrun Check
    expense_sum = expenses.groupby('category')['amount'].sum().reset_index()
    if not budget_df.empty:
        merged = pd.merge(budget_df, expense_sum, on='category', how='left').fillna(0)
        for _, row in merged.iterrows():
            if row['amount'] > row['limit_amount']:
                over = row['amount'] - row['limit_amount']
                suggestions.append(f"🚨 **Budget Breach**: You exceeded your **{row['category']}** budget by ₹{over:,.2f}.")
            elif row['amount'] > (row['limit_amount'] * 0.9):
                suggestions.append(f"⚠️ **Warning**: You are near the limit for **{row['category']}**.")

    # 3. High Spending Categories
    if not expense_sum.empty:
        top_cat = expense_sum.sort_values(by='amount', ascending=False).iloc[0]
        suggestions.append(f"💡 **Insight**: Your highest spending is on **{top_cat['category']}** (₹{top_cat['amount']:,.2f}). Try to reduce this by 10% to save ₹{top_cat['amount']*0.1:,.2f}.")

    return suggestions

def generate_pdf_report(df, username):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt=f"Financial Report for {username}", ln=True, align='C')
    pdf.ln(10)
    
    # Summary
    income = df[df['type'] == 'Income']['amount'].sum()
    expense = df[df['type'] == 'Expense']['amount'].sum()
    savings = income - expense
    
    pdf.cell(200, 10, txt=f"Total Income: INR {income}", ln=True)
    pdf.cell(200, 10, txt=f"Total Expenses: INR {expense}", ln=True)
    pdf.cell(200, 10, txt=f"Net Savings: INR {savings}", ln=True)
    pdf.ln(10)
    
    pdf.cell(200, 10, txt="Transaction History:", ln=True)
    
    # Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(40, 10, "Date", 1, 0, 'C', 1)
    pdf.cell(40, 10, "Category", 1, 0, 'C', 1)
    pdf.cell(30, 10, "Type", 1, 0, 'C', 1)
    pdf.cell(40, 10, "Amount", 1, 1, 'C', 1)
    
    # Rows
    for _, row in df.iterrows():
        pdf.cell(40, 10, str(row['date']), 1)
        pdf.cell(40, 10, str(row['category']), 1)
        pdf.cell(30, 10, str(row['type']), 1)
        pdf.cell(40, 10, str(row['amount']), 1, 1)
        
    return pdf.output(dest='S').encode('latin-1')