import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Define a consistent vibrant color palette
COLORS = {
    'Income': '#00C853',      # Vibrant Green
    'Expense': '#FF3D00',     # Vibrant Red
    'Limit': '#B0BEC5',       # Gray for budget limits
    'Pie': px.colors.qualitative.Prism,  # Bright qualitative colors for categories
    'Background': 'rgba(0,0,0,0)' # Transparent backgrounds
}

def plot_income_expense_trend(df):
    if df.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False, font=dict(size=20, color="gray"))
        fig.update_layout(title="Income vs Expenses Trend", paper_bgcolor=COLORS['Background'])
        return fig
    
    df['date'] = pd.to_datetime(df['date'])
    # Group by date and type
    monthly = df.groupby([pd.Grouper(key='date', freq='M'), 'type'])['amount'].sum().reset_index()
    
    fig = px.area(monthly, x='date', y='amount', color='type', 
                  title="📈 Income vs Expenses Trend",
                  markers=True,
                  color_discrete_map={"Income": COLORS['Income'], "Expense": COLORS['Expense']})
    
    fig.update_layout(
        paper_bgcolor=COLORS['Background'],
        plot_bgcolor=COLORS['Background'],
        hovermode="x unified",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(200,200,200,0.2)'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

def plot_expense_pie(df):
    expenses = df[df['type'] == 'Expense']
    if expenses.empty:
        fig = go.Figure()
        fig.add_annotation(text="No expense data", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False, font=dict(size=20, color="gray"))
        fig.update_layout(title="Expense Breakdown", paper_bgcolor=COLORS['Background'])
        return fig
    
    fig = px.pie(expenses, values='amount', names='category', 
                 title="🍩 Expense Breakdown",
                 hole=0.5,
                 color_discrete_sequence=COLORS['Pie'])
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        paper_bgcolor=COLORS['Background'],
        showlegend=False
    )
    return fig

def plot_budget_vs_actual(budget_df, expense_df):
    if budget_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No budgets set", xref="paper", yref="paper",
                          x=0.5, y=0.5, showarrow=False, font=dict(size=20, color="gray"))
        return fig

    # Merge budget limits with actual expenses
    expense_sum = expense_df[expense_df['type'] == 'Expense'].groupby('category')['amount'].sum().reset_index()
    merged = pd.merge(budget_df, expense_sum, on='category', how='left').fillna(0)
    merged.rename(columns={'amount': 'Spent', 'limit_amount': 'Limit'}, inplace=True)
    
    # Calculate colors based on percentage used
    merged['usage'] = merged['Spent'] / merged['Limit']
    
    # Dynamic colors: Green (<80%), Yellow (80-100%), Red (>100%)
    bar_colors = [
        '#FF1744' if x > 1.0 else 
        '#FFC107' if x > 0.8 else 
        '#00E676' for x in merged['usage']
    ]

    fig = go.Figure(data=[
        go.Bar(name='Limit', x=merged['category'], y=merged['Limit'], 
               marker_color=COLORS['Limit'], opacity=0.3),
        go.Bar(name='Spent', x=merged['category'], y=merged['Spent'], 
               marker_color=bar_colors, text=merged['Spent'], textposition='auto')
    ])
    
    fig.update_layout(
        barmode='overlay', 
        title="🎯 Budget Health (Spent vs Limit)",
        paper_bgcolor=COLORS['Background'],
        plot_bgcolor=COLORS['Background'],
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        showlegend=True
    )
    return fig

#hjdsvcjsavcjyds hbdsjvc vergvdfs ytffthchtc
