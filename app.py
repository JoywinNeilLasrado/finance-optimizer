import streamlit as st
import pandas as pd
from datetime import date
import database as db
import auth
import charts
import optimizer

# --- Page Config ---
st.set_page_config(page_title="Budget Optimizer", page_icon="💰", layout="wide")

# --- CUSTOM CSS & HTML STYLING ---
def load_css():
    st.markdown("""
        <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }

        /* Gradient Background for the App */
        .stApp {
            background: linear-gradient(to right, #f8f9fa, #e9ecef);
        }

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #1e293b;
        }
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label {
            color: #f1f5f9 !important;
        }

        /* Custom Card Styling for Dashboard Metrics */
        .metric-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            border-left: 5px solid #3b82f6;
            transition: transform 0.2s;
        }
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
        }
        .metric-label {
            font-size: 14px;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #1e293b;
            margin: 10px 0;
        }
        .metric-delta {
            font-size: 14px;
            font-weight: 500;
        }

        /* Color variations for cards */
        .border-green { border-left-color: #10b981; }
        .border-red { border-left-color: #ef4444; }
        .border-blue { border-left-color: #3b82f6; }

        .text-green { color: #10b981; }
        .text-red { color: #ef4444; }
        .text-blue { color: #3b82f6; }

        /* Headers */
        h1, h2, h3 {
            color: #0f172a;
        }

        /* Custom Button Styling (Targeting Streamlit's Button) */
        div.stButton > button {
            background-color: #3b82f6;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
        }
        div.stButton > button:hover {
            background-color: #2563eb;
            color: white;
        }
        
        /* Table Styling */
        div[data-testid="stDataFrame"] {
            background-color: white;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        </style>
    """, unsafe_allow_html=True)

# Load the CSS
load_css()

# --- Initialize DB ---
db.init_db()

# --- Authentication Check ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    auth.login_page()
    st.stop()

# --- Sidebar & Navigation ---
st.sidebar.title(f"👋 Welcome, {st.session_state['name']}")
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navigation", ["Dashboard", "Add Transaction", "Budget Planner", "Reports"])
st.sidebar.markdown("---")

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
    st.markdown("Here is an overview of your financial health this month.")
    st.markdown("---")
    
    # Logic for Metrics
    income = df[df['type'] == 'Income']['amount'].sum()
    expense = df[df['type'] == 'Expense']['amount'].sum()
    balance = income - expense
    
    # --- CUSTOM HTML CARDS ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card border-green">
                <div class="metric-label">Total Income</div>
                <div class="metric-value">₹{income:,.2f}</div>
                <div class="metric-delta text-green">↗ Inflow</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-card border-red">
                <div class="metric-label">Total Expenses</div>
                <div class="metric-value">₹{expense:,.2f}</div>
                <div class="metric-delta text-red">↘ Outflow</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-card border-blue">
                <div class="metric-label">Remaining Balance</div>
                <div class="metric-value">₹{balance:,.2f}</div>
                <div class="metric-delta text-blue">{'Healthy' if balance > 0 else 'Critical'}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts with Container Styling
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📈 Trends")
        trend_fig = charts.plot_income_expense_trend(df)
        if trend_fig:
            st.plotly_chart(trend_fig, use_container_width=True)
    with c2:
        st.markdown("### 🍩 Breakdown")
        pie_fig = charts.plot_expense_pie(df)
        if pie_fig:
            st.plotly_chart(pie_fig, use_container_width=True)
        
    # Budget Progress
    st.subheader("🎯 Budget Status")
    budget_fig = charts.plot_budget_vs_actual(budget_df, df)
    if budget_fig:
        st.plotly_chart(budget_fig, use_container_width=True)

    # AI Suggestions
    st.markdown("---")
    st.subheader("🤖 AI Smart Suggestions")
    suggestions = optimizer.generate_suggestions(df, budget_df)
    for s in suggestions:
        st.info(s)

elif menu == "Add Transaction":
    st.title("➕ Add Transaction")
    
    # Styled container for form
    with st.container():
        st.markdown('<div style="background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">', unsafe_allow_html=True)
        
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
        
        st.markdown('</div>', unsafe_allow_html=True)
            
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("📜 Recent Transactions")
    st.dataframe(df.sort_values(by='date', ascending=False).head(10), use_container_width=True)
    
    # Simple Delete Mechanism
    with st.expander("🗑️ Delete a Transaction"):
        t_id_to_del = st.number_input("Enter Transaction ID to Delete", step=1)
        if st.button("Delete"):
            db.delete_transaction(t_id_to_del)
            st.warning("Deleted!")
            st.rerun()

elif menu == "Budget Planner":
    st.title("📅 Monthly Budget Planner")
    
    st.info(f"Setting budgets for: **{current_month}**")
    
    with st.form("budget_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            cat = st.selectbox("Category", ["Food", "Transport", "Rent", "Entertainment", "Health", "Shopping", "Other"])
        with col2:
            limit = st.number_input("Monthly Limit (₹)", min_value=0.0)
        
        if st.form_submit_button("Set Budget"):
            db.set_budget(username, cat, limit, current_month)
            st.success(f"Budget set for {cat}")
            st.rerun()
            
    st.subheader("Current Budgets")
    st.dataframe(budget_df, use_container_width=True)

elif menu == "Reports":
    st.title("📑 Export Reports")
    
    st.dataframe(df, use_container_width=True)
    
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