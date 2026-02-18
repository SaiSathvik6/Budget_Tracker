import streamlit as st
import pandas as pd
import config
from datetime import datetime
from components.expense_form import render_expense_form
from components.income_form import render_income_form
from database.models import ExpenseModel
from database.category_model import CategoryModel
from database.income_model import IncomeModel
from database.income_source_model import IncomeSourceModel
from utils.helpers import format_currency, get_month_name, get_month_start_end


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
        # st.divider() # Removed extra divider to clean up UI
        render_expense_form()
    
    with tab2:
        st.subheader("Add New Income")
        st.markdown("Record your income sources to track your earnings.")
        # st.divider()
        render_income_form()
        
    st.divider()
    
    # History Section
    st.subheader("📜 Transaction History")
    
    # Year and Month selectors for filtering history
    col1, col2 = st.columns(2)
    
    # Get available years and year-months from database
    available_years = ExpenseModel.get_available_years()
    available_year_months = ExpenseModel.get_available_year_months()
    
    with col1:
        # Year selector
        current_year = datetime.now().year
        if current_year not in available_years:
            available_years.insert(0, current_year)
        
        selected_year = st.selectbox(
            "📅 Select Year",
            options=available_years,
            index=0,
            help="Select year to view",
            key="trans_year_select"
        )
    
    with col2:
        # Month selector - filter by selected year
        available_months_for_year = sorted([ym[1] for ym in available_year_months if ym[0] == selected_year])
        
        # Add current month if selected year is current year and month not in list
        current_month = datetime.now().month
        if selected_year == current_year and current_month not in available_months_for_year:
            available_months_for_year.insert(0, current_month)
            available_months_for_year = sorted(available_months_for_year, reverse=True)
        
        if available_months_for_year:
            # Default to current month if available, otherwise first item (latest)
            default_index = 0
            if selected_year == current_year:
                try:
                    default_index = available_months_for_year.index(current_month)
                except ValueError:
                    default_index = 0
            
            selected_month = st.selectbox(
                "📅 Select Month",
                options=available_months_for_year,
                format_func=lambda m: get_month_name(m),
                index=default_index,
                help="Select month to view",
                key="trans_month_select"
            )
        else:
            # No data for selected year, default to current month
            selected_month = current_month
            st.info(f"No data available for {selected_year}. Showing current month.")
    
    # Get date range for selected month
    start_date, end_date = get_month_start_end(selected_year, selected_month)
    filter_label = f"{get_month_name(selected_month)} {selected_year}"
    
    # Render tables in tabs
    tab_exp, tab_inc = st.tabs(["📝 Expenses", "💰 Income"])
    
    with tab_exp:
        render_recent_expenses(start_date, end_date, filter_label)
        
    with tab_inc:
        render_recent_income(start_date, end_date, filter_label)


def render_recent_expenses(start_date, end_date, filter_label):
    """Render recent expenses table with edit/delete options"""
    st.subheader(f"📝 Expenses ({filter_label})")
    
    # Get filtered expenses
    if start_date and end_date:
        expenses = ExpenseModel.get_expenses(start_date, end_date)
        total_expenses_count = len(ExpenseModel.get_expenses(start_date, end_date))
    else:
        expenses = ExpenseModel.get_expenses()
        total_expenses_count = len(ExpenseModel.get_expenses())
    
    if not expenses:
        st.info(f"No expenses recorded for {filter_label}.")
        return
    
    # Limit to 50 for display
    display_count = min(len(expenses), 50)
    expenses = expenses[:display_count]
    
    st.caption(f"Showing {display_count} of {total_expenses_count} expenses")
    
    # Convert to DataFrame
    df = pd.DataFrame(expenses)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%d %b %Y")
    df["amount"] = df["amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
    
    # Select columns to display
    display_df = df[["date", "category", "description", "amount"]].copy()
    display_df.columns = ["Date", "Category", "Description", "Amount"]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Edit/Delete section
    with st.expander("✏️ Edit or Delete Expense"):
        if len(expenses) > 0:
            # Create selection dropdown
            expense_options = [
                f"{exp['date'].strftime('%d %b %Y')} - {exp['category']} - {exp['description']} - {config.CURRENCY_SYMBOL}{exp['amount']:,.2f}"
                for exp in expenses
            ]
            
            selected_idx = st.selectbox(
                "Select expense to edit/delete",
                options=range(len(expense_options)),
                format_func=lambda x: expense_options[x]
            )
            
            selected_expense = expenses[selected_idx]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✏️ Edit", type="primary", use_container_width=True, key="edit_expense_btn"):
                    st.session_state.editing_expense = selected_expense
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Delete", type="primary", use_container_width=True, key="delete_expense_btn"):
                    if ExpenseModel.delete_expense(str(selected_expense["_id"])):
                        st.success("Expense deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete expense.")
    
    # Edit form (if editing)
    if "editing_expense" in st.session_state:
        render_edit_form(st.session_state.editing_expense)


def render_edit_form(expense):
    """Render edit form for an expense"""
    st.divider()
    st.subheader("✏️ Edit Expense")
    
    with st.form("edit_expense_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_date = st.date_input(
                "Date",
                value=expense["date"],
                max_value=datetime.now()
            )
        
        with col2:
            all_categories = CategoryModel.get_all_categories()
            # Find index of current category
            try:
                cat_index = all_categories.index(expense["category"])
            except ValueError:
                cat_index = 0
            
            new_category = st.selectbox(
                "Category",
                options=all_categories,
                index=cat_index
            )
        
        new_description = st.text_input(
            "Description",
            value=expense["description"]
        )
        
        new_amount = st.number_input(
            f"Amount ({config.CURRENCY_SYMBOL})",
            value=float(expense["amount"]),
            min_value=0.0,
            step=10.0,
            format="%.2f"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
        
        with col2:
            cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submitted:
            new_datetime = datetime.combine(new_date, datetime.min.time())
            
            if ExpenseModel.update_expense(
                str(expense["_id"]),
                new_datetime,
                new_category,
                new_description,
                new_amount
            ):
                st.success("Expense updated successfully!")
                del st.session_state.editing_expense
                st.rerun()
            else:
                st.error("Failed to update expense.")
        
        if cancelled:
            del st.session_state.editing_expense
            st.rerun()


def render_recent_income(start_date, end_date, filter_label):
    """Render recent income table with edit/delete options"""
    st.subheader(f"💰 Income ({filter_label})")
    
    # Get filtered income
    if start_date and end_date:
        incomes = IncomeModel.get_incomes(start_date, end_date)
        total_income_count = len(IncomeModel.get_incomes(start_date, end_date))
    else:
        incomes = IncomeModel.get_incomes()
        total_income_count = len(IncomeModel.get_incomes())
    
    if not incomes:
        st.info(f"No income recorded for {filter_label}.")
        return
    
    # Limit to 50 for display
    display_count = min(len(incomes), 50)
    incomes = incomes[:display_count]
    
    st.caption(f"Showing {display_count} of {total_income_count} entries")
    
    # Convert to DataFrame
    df = pd.DataFrame(incomes)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%d %b %Y")
    df["amount"] = df["amount"].apply(lambda x: f"{config.CURRENCY_SYMBOL}{x:,.2f}")
    
    # Select columns to display
    display_df = df[["date", "source", "description", "amount"]].copy()
    display_df.columns = ["Date", "Source", "Description", "Amount"]
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Edit/Delete section
    with st.expander("✏️ Edit or Delete Income"):
        if len(incomes) > 0:
            # Create selection dropdown
            income_options = [
                f"{inc['date'].strftime('%d %b %Y')} - {inc['source']} - {inc['description']} - {config.CURRENCY_SYMBOL}{inc['amount']:,.2f}"
                for inc in incomes
            ]
            
            selected_idx = st.selectbox(
                "Select income to edit/delete",
                options=range(len(income_options)),
                format_func=lambda x: income_options[x],
                key="select_income_edit"
            )
            
            selected_income = incomes[selected_idx]
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✏️ Edit", type="primary", use_container_width=True, key="edit_income_btn"):
                    st.session_state.editing_income = selected_income
                    st.rerun()
            
            with col2:
                if st.button("🗑️ Delete", type="primary", use_container_width=True, key="delete_income_btn"):
                    if IncomeModel.delete_income(str(selected_income["_id"])):
                        st.success("Income deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete income.")
    
    # Edit form (if editing)
    if "editing_income" in st.session_state:
        render_edit_income_form(st.session_state.editing_income)


def render_edit_income_form(income):
    """Render edit form for an income entry"""
    st.divider()
    st.subheader("✏️ Edit Income")
    
    with st.form("edit_income_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_date = st.date_input(
                "Date",
                value=income["date"],
                max_value=datetime.now(),
                key="edit_income_date"
            )
        
        with col2:
            all_sources = IncomeSourceModel.get_all_sources()
            # Find index of current source
            try:
                source_index = all_sources.index(income["source"])
            except ValueError:
                source_index = 0
            
            new_source = st.selectbox(
                "Source",
                options=all_sources,
                index=source_index,
                key="edit_income_source"
            )
        
        new_description = st.text_input(
            "Description",
            value=income["description"],
            key="edit_income_desc"
        )
        
        new_amount = st.number_input(
            f"Amount ({config.CURRENCY_SYMBOL})",
            value=float(income["amount"]),
            min_value=0.0,
            step=10.0,
            format="%.2f",
            key="edit_income_amount"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
        
        with col2:
            cancelled = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if submitted:
            new_datetime = datetime.combine(new_date, datetime.min.time())
            
            if IncomeModel.update_income(
                str(income["_id"]),
                new_datetime,
                new_source,
                new_description,
                new_amount
            ):
                st.success("Income updated successfully!")
                del st.session_state.editing_income
                st.rerun()
            else:
                st.error("Failed to update income.")
        
        if cancelled:
            del st.session_state.editing_income
            st.rerun()
