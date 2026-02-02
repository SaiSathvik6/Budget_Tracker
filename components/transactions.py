"""
Transactions page component for adding expenses and income
"""
import streamlit as st
from components.expense_form import render_expense_form
from components.income_form import render_income_form


def render_transactions():
    """Render the transactions page with expense and income forms"""
    st.header("💳 Add Transactions")
    st.markdown("Add your expenses and income entries here.")
    
    st.divider()
    
    # Create tabs for Expense and Income
    tab1, tab2 = st.tabs(["💸 Add Expense", "💰 Add Income"])
    
    with tab1:
        st.subheader("Add New Expense")
        st.markdown("Record your expenses to track your spending.")
        st.divider()
        render_expense_form()
    
    with tab2:
        st.subheader("Add New Income")
        st.markdown("Record your income sources to track your earnings.")
        st.divider()
        render_income_form()
