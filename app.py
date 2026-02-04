import streamlit as st
import pandas as pd
from datetime import date
import database as db
import auth
import charts
import optimizer

# --- Page Config ---
st.set_page_config(page_title="Budget Optimizer", page_icon="💰", layout="wide")

# --- VISUAL STYLING (CSS) ---
def load_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }

        /* App Background */
        .stApp {
            background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%);
        }

        /* Sidebar Background */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1A237E 0%, #0D47A1 100%);
        }

        /* --- FIX: Force Sidebar Text to White --- */
        section[data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        
        /* Specific fix for Radio Button Text (Navigation) */
        div[data-testid="stSidebar"] label p {
            font-size: 16px; 
            font-weight: 500;
        }

        /* Custom Metric Cards */
        .metric-container {
            background: linear-gradient(135deg, #ffffff, #f0f2f5);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.05);
            text-align: center;
            transition: transform 0.3s ease;
            border: 1px solid rgba(255,255,255,0.5);
        }
        .metric-container:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 25px rgba(0,0,0,0.1);
        }
        
        /* Specific Card Gradients */
        .card-income { border-bottom: 5px solid #00C853; }
        .card-expense { border-bottom: 5px solid #FF3D00; }
        .card-balance { border-bottom: 5px solid #2979FF; }

        .metric-label { font-size: 14px; font-weight: 500; color: #546E7A; text-transform: uppercase; letter-spacing: 1px; }
        .metric-value { font-size: 32px; font-weight: 700; color: #263238; margin: 10px 0; }
        .metric-delta { font-size: 14px; font-weight: 600; padding: 4px 8px; border-radius: 8px; display: inline-block;}
        
        .delta-pos { background-color: #E8F5E9; color: #2E7D32; }
        .delta-neg { background-color: #FFEBEE; color: #C62828; }

        /* Form & Container Styling */
        .form-container {
            background-color: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }

        /* Styled Buttons */
        div.stButton > button {
            background: linear-gradient(90deg, #2979FF 0%, #1565C0 100%);
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 50px;
            font-weight: 600;
            box-shadow: 0 4px 10px rgba(41, 121, 255, 0.3);
            transition: all 0.3s;
        }
        div.stButton > button:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 15px rgba(41, 121, 255, 0.4);
        }

        /* Budget Progress Bar Styling */
        .progress-bar-bg {
            background-color: #eee;
            border-radius: 10px;
            height: 20px;
            width: 100%;
            overflow: hidden;
        }
        .progress-bar-fill {
            height: 100%;
            text-align: center;
            color: white;
            font-size: 12px;
            line-height: 20px;
            transition: width 0.5s ease-in-out;
        }
        </style>
    """, unsafe_allow_html=True)

load_css()

# --- Initialize DB ---
db.init_db()

# --- Authentication Check ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    auth.login_page()
    st.stop()

# --- Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    # Using explicit white color for the title just in case CSS misses it
    st.markdown(f"<h1 style='color: white;'>Hello, {st.session_state['name'].split()[0]}!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #E0E0E0;'>Your financial command center.</p>", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("Navigate", ["Dashboard", "Add Transaction", "Budget Planner", "Reports"])
    st.markdown("---")
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- Data Loading ---
username = st.session_state['username']
df = db.get_user_data(username)
current_month = date.today().strftime("%Y-%m")
budget_df = db.get_budgets(username, current_month)

# --- Pages ---

if menu == "Dashboard":
    st.title("🚀 Financial Dashboard")
    st.markdown("### Overview for this month")
    
    # Calculate Metrics
    income = df[df['type'] == 'Income']['amount'].sum()
    expense = df[df['type'] == 'Expense']['amount'].sum()
    balance = income - expense
    
    # --- COLORFUL CARDS ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-container card-income">
                <div class="metric-label">Total Income</div>
                <div class="metric-value">₹{income:,.2f}</div>
                <div class="metric-delta delta-pos">↗ +12% vs last month</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="metric-container card-expense">
                <div class="metric-label">Total Expenses</div>
                <div class="metric-value">₹{expense:,.2f}</div>
                <div class="metric-delta delta-neg">↘ Alert</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="metric-container card-balance">
                <div class="metric-label">Remaining Balance</div>
                <div class="metric-value">₹{balance:,.2f}</div>
                <div class="metric-delta delta-pos">Savings Active</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts Area
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("##### 📅 Income & Expense Trend")
        fig_trend = charts.plot_income_expense_trend(df)
        if fig_trend:
            st.plotly_chart(fig_trend, use_container_width=True)
    with c2:
        st.markdown("##### 💸 Where is money going?")
        fig_pie = charts.plot_expense_pie(df)
        if fig_pie:
            st.plotly_chart(fig_pie, use_container_width=True)
        
    st.markdown("---")
    st.subheader("🤖 AI Smart Insights")
    
    # Styled Suggestions
    suggestions = optimizer.generate_suggestions(df, budget_df)
    if suggestions:
        for s in suggestions:
            # Check content to decide color
            color = "#D1C4E9" if "Insight" in s else "#FFCDD2" if "Breach" in s or "Warning" in s else "#C8E6C9"
            icon = "💡" if "Insight" in s else "🚨" if "Breach" in s else "✅"
            
            st.markdown(f"""
                <div style="background-color: {color}; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid rgba(0,0,0,0.1);">
                    <span style="font-size: 18px; margin-right: 10px;">{icon}</span> {s.replace('⚠️', '').replace('🚨', '').replace('✅', '').replace('💡', '')}
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No sufficient data for insights yet.")

elif menu == "Add Transaction":
    st.title("➕ Add New Transaction")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        with st.form("transaction_form", clear_on_submit=True):
            st.markdown("#### 📝 Transaction Details")
            c1, c2 = st.columns(2)
            t_date = c1.date_input("Date")
            t_type = c2.selectbox("Type", ["Expense", "Income"])
            
            c3, c4 = st.columns(2)
            t_amount = c3.number_input("Amount (₹)", min_value=0.0, step=100.0)
            t_category = c4.selectbox("Category", ["Food", "Transport", "Rent", "Entertainment", "Salary", "Freelance", "Health", "Shopping", "Other"])
            
            t_desc = st.text_input("Description (Optional)")
            
            submitted = st.form_submit_button("💾 Save Transaction")
            if submitted:
                db.add_transaction(username, t_date, t_amount, t_category, t_type, t_desc)
                st.balloons()
                st.success("Transaction Saved!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown("#### 🕒 Recent Activity")
        if not df.empty:
            recent = df.sort_values(by='date', ascending=False).head(5)
            for index, row in recent.iterrows():
                color = "#e8f5e9" if row['type'] == "Income" else "#ffebee"
                icon = "💰" if row['type'] == "Income" else "🛒"
                st.markdown(f"""
                    <div style="background-color: {color}; padding: 10px; border-radius: 8px; margin-bottom: 8px; font-size: 14px;">
                        <strong>{icon} {row['category']}</strong><br>
                        <span style="color: #666;">{row['date']}</span>
                        <span style="float: right; font-weight: bold;">₹{row['amount']}</span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent activity.")

    with st.expander("🗑️ Delete History"):
         t_id = st.number_input("Transaction ID", step=1)
         if st.button("Delete Transaction"):
             db.delete_transaction(t_id)
             st.warning(f"Deleted ID: {t_id}")
             st.rerun()

elif menu == "Budget Planner":
    st.title("🎯 Monthly Budget Targets")
    st.markdown(f"Set your limits for: **{current_month}**")
    
    with st.expander("➕ Set New Budget", expanded=True):
        with st.form("budget_form"):
            c1, c2 = st.columns(2)
            cat = c1.selectbox("Category", ["Food", "Transport", "Rent", "Entertainment", "Health", "Shopping", "Other"])
            limit = c2.number_input("Monthly Limit (₹)", min_value=1000.0, step=500.0)
            if st.form_submit_button("Set Budget"):
                db.set_budget(username, cat, limit, current_month)
                st.success(f"Budget for {cat} updated!")
                st.rerun()

    st.markdown("### 📊 Budget Progress")
    
    if not budget_df.empty and not df.empty:
        expense_sum = df[df['type'] == 'Expense'].groupby('category')['amount'].sum().reset_index()
        merged = pd.merge(budget_df, expense_sum, on='category', how='left').fillna(0)
        
        for _, row in merged.iterrows():
            cat = row['category']
            limit = row['limit_amount']
            spent = row['amount']
            pct = (spent / limit) * 100 if limit > 0 else 0
            pct_clamped = min(pct, 100)
            
            bar_color = "#4CAF50" # Green
            if pct > 75: bar_color = "#FFC107" # Yellow
            if pct > 100: bar_color = "#F44336" # Red
            
            st.markdown(f"""
                <div style="margin-bottom: 15px; background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <strong>{cat}</strong>
                        <span>₹{spent:,.0f} / ₹{limit:,.0f}</span>
                    </div>
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" style="width: {pct_clamped}%; background-color: {bar_color};">
                            {pct:.0f}%
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No budgets or expenses found yet.")

    fig_budget = charts.plot_budget_vs_actual(budget_df, df)
    if fig_budget:
        st.plotly_chart(fig_budget, use_container_width=True)

elif menu == "Reports":
    st.title("📑 Export & Reports")
    st.markdown("Download your data for offline analysis.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown("#### 📄 CSV Report")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download CSV", csv, "report.csv", "text/csv")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown("#### 📕 PDF Report")
        pdf_bytes = optimizer.generate_pdf_report(df, st.session_state['name'])
        st.download_button("📥 Download PDF", pdf_bytes, "report.pdf", "application/pdf")
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown("### Raw Data")
    st.dataframe(df, use_container_width=True)