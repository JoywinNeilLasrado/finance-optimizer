import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def plot_income_expense_trend(df):
    if df.empty:
        return None
    
    df['date'] = pd.to_datetime(df['date'])
    monthly = df.groupby([pd.Grouper(key='date', freq='M'), 'type'])['amount'].sum().reset_index()
    
    fig = px.line(monthly, x='date', y='amount', color='type', 
                  title="Income vs Expenses Trend",
                  markers=True,
                  color_discrete_map={"Income": "#2ecc71", "Expense": "#e74c3c"})
    return fig

def plot_expense_pie(df):
    expenses = df[df['type'] == 'Expense']
    if expenses.empty:
        return None
    
    fig = px.pie(expenses, values='amount', names='category', 
                 title="Expense Breakdown",
                 hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    return fig

def plot_budget_vs_actual(budget_df, expense_df):
    # Merge budget limits with actual expenses
    expense_sum = expense_df[expense_df['type'] == 'Expense'].groupby('category')['amount'].sum().reset_index()
    merged = pd.merge(budget_df, expense_sum, on='category', how='left').fillna(0)
    merged.rename(columns={'amount': 'Spent', 'limit_amount': 'Limit'}, inplace=True)
    
    # Calculate colors based on usage
    merged['usage'] = merged['Spent'] / merged['Limit']
    colors = ['#e74c3c' if x > 1 else '#f1c40f' if x > 0.8 else '#2ecc71' for x in merged['usage']]

    fig = go.Figure(data=[
        go.Bar(name='Limit', x=merged['category'], y=merged['Limit'], marker_color='#95a5a6'),
        go.Bar(name='Spent', x=merged['category'], y=merged['Spent'], marker_color=colors)
    ])
    fig.update_layout(barmode='group', title="Budget vs Actual Spending (Monthly)")
    return fig