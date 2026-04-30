import streamlit as st
import pandas as pd
import config
from datetime import datetime
from components.expense_form import render_expense_form
from database.models import ExpenseModel
from database.category_model import CategoryModel
from utils.helpers import format_currency, get_month_name, get_month_start_end


def render_transactions():
    """Render the transactions page with expense form"""
    st.header("💳 Add Transactions")
    st.markdown("Add your expense entries here.")
    
    st.divider()
    
    st.subheader("Add New Expense")
    st.markdown("Record your expenses to track your spending.")
    render_expense_form()

    # Handle post-submit success OUTSIDE the form to avoid st.rerun() widget corruption
    if st.session_state.get("expense_added"):
        amount = st.session_state.get("expense_added_amount", 0)
        st.success(f"✅ Expense of {config.CURRENCY_SYMBOL}{amount:,.2f} added successfully!")
        st.balloons()
        st.session_state.expense_added = False
        st.session_state.expense_added_amount = 0
        st.rerun()
        
    st.divider()
    
    # History Section
    st.subheader("📜 Expense History")
    
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
    
    render_recent_expenses(start_date, end_date, filter_label)


def render_recent_expenses(start_date, end_date, filter_label):
    """Render recent expenses table with inline edit/delete buttons per row"""
    st.subheader(f"📝 Expenses ({filter_label})")

    # Get filtered expenses
    if start_date and end_date:
        expenses = ExpenseModel.get_expenses(start_date, end_date)
        total_expenses_count = len(expenses)
    else:
        expenses = ExpenseModel.get_expenses()
        total_expenses_count = len(expenses)

    if not expenses:
        st.info(f"No expenses recorded for {filter_label}.")
        return

    # Limit to 50 for display
    display_count = min(len(expenses), 50)
    expenses = expenses[:display_count]

    st.caption(f"Showing {display_count} of {total_expenses_count} expenses")

    # ── Table styles (scoped to .txn-table container) ─────────────────────────
    st.markdown("""
    <style>
    .txn-header {
        font-size: 0.75rem;
        font-weight: 700;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.3rem 0.2rem;
        border-bottom: 1px solid #333;
    }
    /* Target only horizontal blocks that are children of .txn-table */
    .txn-table [data-testid="stHorizontalBlock"] {
        gap: 0 !important;
        align-items: center;
        margin-bottom: -0.55rem !important;
        border-bottom: 1px solid #1e1e1e;
    }
    .txn-table [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    .txn-table small {
        line-height: 1.1;
        display: block;
        padding: 0.15rem 0;
    }
    /* Compact emoji action buttons */
    .txn-table [data-testid="stButton"] > button {
        padding: 0 !important;
        font-size: 0.85rem !important;
        height: 1.5rem !important;
        min-height: unset !important;
        line-height: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Open the scoped container
    st.markdown("<div class='txn-table'>", unsafe_allow_html=True)

    # Header row  [Date | Category | Description | Amount | Actions]
    h1, h2, h3, h4, h5 = st.columns([2, 2, 4, 2, 2])
    with h1:
        st.markdown("<div class='txn-header'>Date</div>", unsafe_allow_html=True)
    with h2:
        st.markdown("<div class='txn-header'>Category</div>", unsafe_allow_html=True)
    with h3:
        st.markdown("<div class='txn-header'>Description</div>", unsafe_allow_html=True)
    with h4:
        st.markdown("<div class='txn-header'>Amount</div>", unsafe_allow_html=True)
    with h5:
        st.markdown("<div class='txn-header'>Actions</div>", unsafe_allow_html=True)

    # ── Data rows ─────────────────────────────────────────────────────────────
    for exp in expenses:
        row_id = str(exp["_id"])
        date_str = exp["date"].strftime("%d %b %Y") if hasattr(exp["date"], "strftime") else str(exp["date"])
        amount_str = f"{config.CURRENCY_SYMBOL}{exp['amount']:,.2f}"
        desc = exp.get("description", "") or "—"

        c1, c2, c3, c4, c5 = st.columns([2, 2, 4, 2, 2])
        with c1:
            st.markdown(f"<small>{date_str}</small>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<small>{exp['category']}</small>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<small>{desc}</small>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<small><b>{amount_str}</b></small>", unsafe_allow_html=True)
        with c5:
            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button("✏️", key=f"edit_{row_id}", help="Edit this expense"):
                    st.session_state.editing_expense = exp
                    st.rerun()
            with btn2:
                if st.button("🗑️", key=f"del_{row_id}", help="Delete this expense"):
                    if ExpenseModel.delete_expense(row_id):
                        st.success("Expense deleted!")
                        st.rerun()
                    else:
                        st.error("Failed to delete expense.")

    # Close the scoped container
    st.markdown("</div>", unsafe_allow_html=True)


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



