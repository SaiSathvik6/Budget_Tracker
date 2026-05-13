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
    st.divider()
    st.subheader("Add New Expense")
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
    
    # Year, Month, and Category selectors for filtering history
    col1, col2, col3 = st.columns(3)
    
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

    with col3:
        # Category filter
        all_categories = CategoryModel.get_all_categories()
        category_options = ["All Categories"] + all_categories
        selected_category = st.selectbox(
            "🏷️ Filter by Category",
            options=category_options,
            index=0,
            help="Filter expenses by category",
            key="trans_category_select"
        )
    
    # Get date range for selected month
    start_date, end_date = get_month_start_end(selected_year, selected_month)
    filter_label = f"{get_month_name(selected_month)} {selected_year}"
    
    render_recent_expenses(start_date, end_date, filter_label, selected_category)


def render_recent_expenses(start_date, end_date, filter_label, selected_category="All Categories"):
    """Render recent expenses using st.dataframe + action panel (Streamlit 1.31 compatible)"""

    # Get date-filtered expenses
    if start_date and end_date:
        expenses = ExpenseModel.get_expenses(start_date, end_date)
    else:
        expenses = ExpenseModel.get_expenses()

    # Apply category filter
    if selected_category and selected_category != "All Categories":
        expenses = [e for e in expenses if e.get("category") == selected_category]

    total_expenses_count = len(expenses)

    if not expenses:
        if selected_category and selected_category != "All Categories":
            st.info(f"No expenses in **{selected_category}** for {filter_label}.")
        else:
            st.info(f"No expenses recorded for {filter_label}.")
        return

    currency = config.CURRENCY_SYMBOL
    total_amount = sum(e["amount"] for e in expenses)

    # ── Build DataFrame for display ───────────────────────────────────────────
    rows = []
    for exp in expenses:
        date_val = exp["date"].date() if hasattr(exp["date"], "date") else exp["date"]
        rows.append({
            "Date":        date_val,
            "Category":    exp.get("category", "—"),
            "Description": exp.get("description", "") or "—",
            "Amount":      exp["amount"],
        })

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Date", format="DD MMM YYYY", width="small"),
            "Category": st.column_config.TextColumn("Category", width="small"),
            "Description": st.column_config.TextColumn("Description"),
            "Amount": st.column_config.NumberColumn(
                "Amount",
                format=f"{currency}%.2f",
                width="small",
            ),
        },
    )

    # ── Fixed total bar ────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="
        display:flex; justify-content:space-between; align-items:center;
        padding:8px 4px; margin-top:-0.5rem; margin-bottom:0.75rem;
        border-top: 1px solid #2a2a2a;
    ">
      <span style="color:#666; font-size:0.78rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">
        {total_expenses_count} expense(s)
      </span>
      <span style="color:#ff6b35; font-weight:700; font-size:1rem;">
        Total &nbsp; {currency}{total_amount:,.2f}
      </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Row action panel ──────────────────────────────────────────────────────
    st.markdown("**Actions**")

    # Build human-readable labels for each row
    row_labels = []
    for exp in expenses:
        date_str = exp["date"].strftime("%d %b %Y") if hasattr(exp["date"], "strftime") else str(exp["date"])
        row_labels.append(f"{date_str}  ·  {exp.get('category','?')}  ·  {currency}{exp['amount']:,.2f}")

    selected_label = st.selectbox(
        "Select expense",
        options=row_labels,
        index=0,
        label_visibility="collapsed",
        key="txn_row_select",
    )

    selected_idx = row_labels.index(selected_label)
    selected_exp = expenses[selected_idx]
    selected_id  = str(selected_exp["_id"])

    col_edit, col_del, col_spacer = st.columns([1, 1, 6])

    with col_edit:
        if st.button("✏️ Edit", key="txn_edit_btn", use_container_width=True):
            st.session_state.editing_expense = selected_exp
            st.rerun()

    with col_del:
        if st.button("🗑️ Delete", key="txn_del_btn", use_container_width=True):
            if ExpenseModel.delete_expense(selected_id):
                st.success("Expense deleted!")
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



