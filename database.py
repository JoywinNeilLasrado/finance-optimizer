import sqlite3
import pandas as pd
import datetime
from datetime import date

DB_NAME = "budget.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password TEXT,
                    name TEXT
                )''')
    
    # Transactions Table (Income & Expenses)
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    date DATE,
                    amount REAL,
                    category TEXT,
                    type TEXT, -- 'Income' or 'Expense'
                    description TEXT,
                    FOREIGN KEY(username) REFERENCES users(username)
                )''')

    # Budgets Table
    c.execute('''CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    category TEXT,
                    limit_amount REAL,
                    month TEXT, -- Format YYYY-MM
                    FOREIGN KEY(username) REFERENCES users(username)
                )''')
    conn.commit()
    conn.close()

def seed_data(username):
    """Injects sample data for a new user."""
    conn = get_connection()
    c = conn.cursor()
    
    # Check if data exists
    c.execute("SELECT count(*) FROM transactions WHERE username=?", (username,))
    if c.fetchone()[0] > 0:
        conn.close()
        return

    today = date.today()
    current_month = today.strftime("%Y-%m")
    
    # Sample Transactions
    data = [
        (username, today, 50000, 'Salary', 'Income', 'Monthly Salary'),
        (username, today, 5000, 'Freelance', 'Income', 'Side Project'),
        (username, today, 2000, 'Food', 'Expense', 'Grocery'),
        (username, today, 1500, 'Transport', 'Expense', 'Fuel'),
        (username, today, 5000, 'Rent', 'Expense', 'House Rent'),
        (username, today, 3000, 'Entertainment', 'Expense', 'Weekend Party'),
    ]
    
    c.executemany("INSERT INTO transactions (username, date, amount, category, type, description) VALUES (?, ?, ?, ?, ?, ?)", data)
    
    # Sample Budgets
    budgets = [
        (username, 'Food', 10000, current_month),
        (username, 'Transport', 5000, current_month),
        (username, 'Entertainment', 2000, current_month),
        (username, 'Rent', 6000, current_month)
    ]
    
    c.executemany("INSERT INTO budgets (username, category, limit_amount, month) VALUES (?, ?, ?, ?)", budgets)
    
    conn.commit()
    conn.close()

# --- CRUD Operations ---

def add_transaction(username, date, amount, category, type, description):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO transactions (username, date, amount, category, type, description) VALUES (?, ?, ?, ?, ?, ?)",
              (username, date, amount, category, type, description))
    conn.commit()
    conn.close()

def delete_transaction(trans_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id=?", (trans_id,))
    conn.commit()
    conn.close()

def get_user_data(username):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM transactions WHERE username = '{username}'", conn)
    conn.close()
    return df

def set_budget(username, category, limit, month):
    conn = get_connection()
    c = conn.cursor()
    # Check if exists, if so update, else insert
    c.execute("SELECT id FROM budgets WHERE username=? AND category=? AND month=?", (username, category, month))
    data = c.fetchone()
    if data:
        c.execute("UPDATE budgets SET limit_amount=? WHERE id=?", (limit, data[0]))
    else:
        c.execute("INSERT INTO budgets (username, category, limit_amount, month) VALUES (?, ?, ?, ?)", 
                  (username, category, limit, month))
    conn.commit()
    conn.close()

def get_budgets(username, month):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT category, limit_amount FROM budgets WHERE username = '{username}' AND month = '{month}'", conn)
    conn.close()
    return df