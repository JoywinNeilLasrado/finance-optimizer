import streamlit as st
import sqlite3
import bcrypt
import database as db

def register_user(username, password, name):
    conn = db.get_connection()
    c = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        c.execute("INSERT INTO users (username, password, name) VALUES (?, ?, ?)", (username, hashed_pw, name))
        conn.commit()
        db.seed_data(username) # Seed data for new users
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def login_user(username, password):
    conn = db.get_connection()
    c = conn.cursor()
    c.execute("SELECT password, name FROM users WHERE username=?", (username,))
    data = c.fetchone()
    conn.close()
    
    if data:
        stored_hash = data[0]
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return data[1] # Return name
    return None

def login_page():
    st.title("🔐 Budget Optimizer Login")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        username = st.text_input("Username (Email)")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            name = login_user(username, password)
            if name:
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['name'] = name
                st.rerun()
            else:
                st.error("Invalid Username or Password")

    with tab2:
        new_user = st.text_input("New Username (Email)")
        new_name = st.text_input("Full Name")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Register"):
            if register_user(new_user, new_pass, new_name):
                st.success("Account created! Please login.")
            else:
                st.error("Username already exists.")