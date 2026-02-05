"""
Expense entry form component
"""
import streamlit as st
from datetime import datetime
import config
from database.models import ExpenseModel
from database.category_model import CategoryModel
from utils.validators import validate_amount, validate_date, validate_description, validate_category


def render_expense_form():
    """Render the expense entry form"""
    
    with st.form("expense_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            expense_date = st.date_input(
                "📅 Date",
                value=datetime.now(),
                max_value=datetime.now(),
                help="Select the date of the expense"
            )
        
        with col2:
            # Get all categories (default + custom)
            all_categories = CategoryModel.get_all_categories()
            category = st.selectbox(
                "🏷️ Category",
                options=all_categories,
                help="Select expense category"
            )
        
        description = st.text_input(
            "📝 Description (Optional)",
            placeholder="e.g., Grocery shopping at supermarket",
            help="Brief description of the expense (optional)"
        )
        
        amount = st.number_input(
            f"💰 Amount ({config.CURRENCY_SYMBOL})",
            min_value=0.0,
            value=None,
            step=10.0,
            format="%.2f",
            placeholder="0.0",
            help="Enter the expense amount"
        )
        st.divider()
        
        submitted = st.form_submit_button("💾 Add Expense", use_container_width=True, type="primary")
        
        if submitted:
            # Validate inputs
            errors = []
            
            # Convert date to datetime
            expense_datetime = datetime.combine(expense_date, datetime.min.time())
            
            # Validate date
            is_valid, error_msg = validate_date(expense_datetime)
            if not is_valid:
                errors.append(error_msg)
            
            # Validate category
            is_valid, error_msg = validate_category(category, all_categories)
            if not is_valid:
                errors.append(error_msg)
            
            # Validate description
            is_valid, error_msg = validate_description(description)
            if not is_valid:
                errors.append(error_msg)
            
            # Validate amount
            is_valid, error_msg = validate_amount(amount)
            if not is_valid:
                errors.append(error_msg)
            
            # Display errors or create expense
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Create expense
                success = ExpenseModel.create_expense(
                    date=expense_datetime,
                    category=category,
                    description=description,
                    amount=amount
                )
                
                if success:
                    st.success(f"✅ Expense of {config.CURRENCY_SYMBOL}{amount:,.2f} added successfully!")
                    st.balloons()
                    # Rerun to update the dashboard
                    st.rerun()
                else:
                    st.error("❌ Failed to add expense. Please try again.")
