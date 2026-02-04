import streamlit as st
import pandas as pd
from datetime import date
import database as db
import auth
import charts
import optimizer

# --- Page Config ---
st.set_page_config(page_title="Budget Optimizer", page_icon="💰", layout="wide")

# --- Initialize DB ---
db.init_db()

# --- Authentication Check ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    auth.login_page()
    st.stop()

# --- Sidebar & Navigation ---
st.sidebar.title(f"Welcome, {st.session_state['name']}")
menu = st.sidebar.radio("Navigation", ["Dashboard", "Add Transaction", "Budget Planner", "Reports"])

if st.sidebar.button("Logout"):
    st.session_state['logged_in'] = False
    st.rerun()

# --- Data Loading ---
username = st.session_state['username']
df = db.get_user_data(username)
current_month = date.today().strftime("%Y-%m")
budget_df = db.get_budgets(username, current_month)

# --- Pages ---

if menu == "Dashboard":
    st.title("📊 Financial Dashboard")
    
    # Metrics
    income = df[df['type'] == 'Income']['amount'].sum()
    expense = df[df['type'] == 'Expense']['amount'].sum()
    balance = income - expense
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₹{income:,.2f}", delta_color="normal")
    col2.metric("Total Expenses", f"₹{expense:,.2f}", delta="-"+str(expense), delta_color="inverse")
    col3.metric("Remaining Balance", f"₹{balance:,.2f}", delta_color="normal")
    
    st.markdown("---")
    
    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(charts.plot_income_expense_trend(df), use_container_width=True)
    with c2:
        st.plotly_chart(charts.plot_expense_pie(df), use_container_width=True)
        
    # Budget Progress
    st.subheader("Budget Status")
    st.plotly_chart(charts.plot_budget_vs_actual(budget_df, df), use_container_width=True)

    # AI Suggestions
    st.markdown("---")
    st.subheader("🤖 AI Smart Suggestions")
    suggestions = optimizer.generate_suggestions(df, budget_df)
    for s in suggestions:
        st.info(s)

elif menu == "Add Transaction":
    st.title("➕ Add Transaction")
    
    with st.form("transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            t_date = st.date_input("Date")
            t_amount = st.number_input("Amount (₹)", min_value=0.0)
            t_type = st.selectbox("Type", ["Income", "Expense"])
        with col2:
            t_category = st.selectbox("Category", ["Food", "Transport", "Rent", "Entertainment", "Salary", "Freelance", "Health", "Shopping", "Other"])
            t_desc = st.text_input("Description")
        
        submitted = st.form_submit_button("Save Transaction")
        if submitted:
            db.add_transaction(username, t_date, t_amount, t_category, t_type, t_desc)
            st.success("Transaction Saved!")
            st.rerun()
            
    st.subheader("Recent Transactions")
    st.dataframe(df.sort_values(by='date', ascending=False).head(10), use_container_width=True)
    
    # Simple Delete Mechanism
    with st.expander("Delete a Transaction"):
        t_id_to_del = st.number_input("Enter Transaction ID to Delete", step=1)
        if st.button("Delete"):
            db.delete_transaction(t_id_to_del)
            st.warning("Deleted!")
            st.rerun()

elif menu == "Budget Planner":
    st.title("📅 Monthly Budget Planner")
    
    st.info(f"Setting budgets for: **{current_month}**")
    
    with st.form("budget_form"):
        cat = st.selectbox("Category", ["Food", "Transport", "Rent", "Entertainment", "Health", "Shopping", "Other"])
        limit = st.number_input("Monthly Limit (₹)", min_value=0.0)
        
        if st.form_submit_button("Set Budget"):
            db.set_budget(username, cat, limit, current_month)
            st.success(f"Budget set for {cat}")
            st.rerun()
            
    st.subheader("Current Budgets")
    st.table(budget_df)

elif menu == "Reports":
    st.title("📑 Export Reports")
    
    st.dataframe(df)
    
    col1, col2 = st.columns(2)
    
    # CSV Export
    csv = df.to_csv(index=False).encode('utf-8')
    col1.download_button(
        "📥 Download CSV",
        csv,
        "finance_report.csv",
        "text/csv",
        key='download-csv'
    )
    
    # PDF Export
    pdf_bytes = optimizer.generate_pdf_report(df, st.session_state['name'])
    col2.download_button(
        "📥 Download PDF",
        data=pdf_bytes,
        file_name="finance_report.pdf",
        mime="application/pdf"
    )