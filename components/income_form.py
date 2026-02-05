"""
Income entry form component
"""
import streamlit as st
from datetime import datetime
import config
from database.income_model import IncomeModel
from database.income_source_model import IncomeSourceModel
from utils.validators import validate_amount, validate_date, validate_description, validate_category


def render_income_form():
    """Render the income entry form"""
    
    with st.form("income_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            income_date = st.date_input(
                "📅 Date",
                value=datetime.now(),
                max_value=datetime.now(),
                help="Select the date of the income"
            )
        
        with col2:
            # Get all income sources (default + custom)
            all_sources = IncomeSourceModel.get_all_sources()
            source = st.selectbox(
                "🏷️ Source",
                options=all_sources,
                help="Select income source"
            )
        
        description = st.text_input(
            "📝 Description (Optional)",
            placeholder="e.g., Monthly salary, Freelance project payment",
            help="Brief description of the income (optional)"
        )
        
        amount = st.number_input(
            f"💵 Amount ({config.CURRENCY_SYMBOL})",
            min_value=0.0,
            value=None,
            step=100.0,
            format="%.2f",
            placeholder="0.0",
            help="Enter the income amount"
        )
        
        st.divider()
        
        submitted = st.form_submit_button("💾 Add Income", use_container_width=True, type="primary")
        
        if submitted:
            # Validate inputs
            errors = []
            
            # Convert date to datetime
            income_datetime = datetime.combine(income_date, datetime.min.time())
            
            # Validate date
            is_valid, error_msg = validate_date(income_datetime)
            if not is_valid:
                errors.append(error_msg)
            
            # Validate source
            is_valid, error_msg = validate_category(source, all_sources)
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
            
            # Display errors or create income
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Create income
                success = IncomeModel.create_income(
                    date=income_datetime,
                    source=source,
                    description=description,
                    amount=amount
                )
                
                if success:
                    st.success(f"✅ Income of {config.CURRENCY_SYMBOL}{amount:,.2f} added successfully!")
                    st.balloons()
                    # Rerun to update the dashboard
                    st.rerun()
                else:
                    st.error("❌ Failed to add income. Please try again.")
