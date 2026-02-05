"""
Settings component
"""
import streamlit as st
from datetime import datetime
import pandas as pd
import config
from database.models import ExpenseModel
from database.category_model import CategoryModel
from database.income_source_model import IncomeSourceModel
from database.connection import get_db
from utils.helpers import format_currency


def render_settings():
    """Render settings page"""
    st.header("⚙️ Settings")
    
    # Create tabs for different settings sections
    tab1, tab2, tab3 = st.tabs(["📦 Expense Categories", "💰 Income Sources", "📥 Export Data"])
    
    with tab1:
        render_category_management()
    
    with tab2:
        render_income_source_management()
    
    with tab3:
        render_export_section()


def render_category_management():
    """Render category management section"""
    
    # Get all categories (default + custom)
    all_categories = CategoryModel.get_all_categories()
    
    # Display current categories
    st.info(f"**Current Categories ({len(all_categories)}):**")
    
    cols = st.columns(3)
    for idx, category in enumerate(all_categories):
        with cols[idx % 3]:
            # Mark default categories
            if category in config.CATEGORIES:
                st.markdown(f"• {category} ⭐")
            else:
                st.markdown(f"• {category}")
    
    st.caption("⭐ = Default categories")
    st.divider()
    
    # Add new category
    st.markdown("### ➕ Add New Category")
    
    with st.form("add_category_form"):
        new_category = st.text_input(
            "Category Name",
            placeholder="e.g., Healthcare, Education, Entertainment",
            help="Enter a new category name (will be capitalized automatically)"
        )
        
        submitted = st.form_submit_button("➕ Add Category", use_container_width=True)
        
        if submitted:
            if not new_category or not new_category.strip():
                st.error("❌ Category name cannot be empty!")
            elif new_category.strip().capitalize() in all_categories:
                st.error(f"❌ Category '{new_category.strip().capitalize()}' already exists!")
            elif len(new_category.strip()) > 30:
                st.error("❌ Category name is too long (max 30 characters)!")
            else:
                # Add new category to database
                new_cat_name = new_category.strip().capitalize()
                if CategoryModel.add_category(new_cat_name):
                    st.success(f"✅ Category '{new_cat_name}' added successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to add category. Please try again.")
    
    st.divider()
    
    # Remove category
    st.markdown("### 🗑️ Remove Category")
    
    # Get custom categories only (not default ones)
    db = get_db()
    custom_cats = db["categories"].find_one({"_id": "custom_categories"})
    custom_categories = custom_cats.get("categories", []) if custom_cats else []
    
    if len(custom_categories) == 0:
        st.info("ℹ️ No custom categories to remove. Default categories cannot be removed.")
    else:
        with st.form("remove_category_form"):
            category_to_remove = st.selectbox(
                "Select Custom Category to Remove",
                options=custom_categories,
                help="Only custom categories can be removed. Existing expenses will be preserved."
            )
            
            remove_submitted = st.form_submit_button("🗑️ Remove Category", type="primary", use_container_width=True)
            
            if remove_submitted:
                if CategoryModel.remove_category(category_to_remove):
                    st.success(f"✅ Category '{category_to_remove}' removed!")
                    st.info("ℹ️ Note: Existing expenses with this category are preserved in the database.")
                    st.rerun()
                else:
                    st.error("❌ Failed to remove category. Default categories cannot be removed.")


def render_income_source_management():
    """Render income source management section"""
    
    # Get all income sources (default + custom)
    all_sources = IncomeSourceModel.get_all_sources()
    
    # Display current sources
    st.info(f"**Current Income Sources ({len(all_sources)}):**")
    
    cols = st.columns(3)
    for idx, source in enumerate(all_sources):
        with cols[idx % 3]:
            # Mark default sources
            if source in config.INCOME_SOURCES:
                st.markdown(f"• {source} ⭐")
            else:
                st.markdown(f"• {source}")
    
    st.caption("⭐ = Default income sources")
    st.divider()
    
    # Add new source
    st.markdown("### ➕ Add New Income Source")
    
    with st.form("add_source_form"):
        new_source = st.text_input(
            "Income Source Name",
            placeholder="e.g., Bonus, Rental Income, Dividends",
            help="Enter a new income source name (will be capitalized automatically)"
        )
        
        submitted = st.form_submit_button("➕ Add Income Source", use_container_width=True)
        
        if submitted:
            if not new_source or not new_source.strip():
                st.error("❌ Income source name cannot be empty!")
            elif new_source.strip().capitalize() in all_sources:
                st.error(f"❌ Income source '{new_source.strip().capitalize()}' already exists!")
            elif len(new_source.strip()) > 30:
                st.error("❌ Income source name is too long (max 30 characters)!")
            else:
                # Add new source to database
                new_source_name = new_source.strip().capitalize()
                if IncomeSourceModel.add_source(new_source_name):
                    st.success(f"✅ Income source '{new_source_name}' added successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to add income source. Please try again.")
    
    st.divider()
    
    # Remove source
    st.markdown("### 🗑️ Remove Income Source")
    
    # Get custom sources only (not default ones)
    db = get_db()
    custom_sources_doc = db["income_sources"].find_one({"_id": "custom_income_sources"})
    custom_sources = custom_sources_doc.get("sources", []) if custom_sources_doc else []
    
    if len(custom_sources) == 0:
        st.info("ℹ️ No custom income sources to remove. Default sources cannot be removed.")
    else:
        with st.form("remove_source_form"):
            source_to_remove = st.selectbox(
                "Select Custom Income Source to Remove",
                options=custom_sources,
                help="Only custom income sources can be removed. Existing income entries will be preserved."
            )
            
            remove_submitted = st.form_submit_button("🗑️ Remove Income Source", type="primary", use_container_width=True)
            
            if remove_submitted:
                if IncomeSourceModel.remove_source(source_to_remove):
                    st.success(f"✅ Income source '{source_to_remove}' removed!")
                    st.info("ℹ️ Note: Existing income entries with this source are preserved in the database.")
                    st.rerun()
                else:
                    st.error("❌ Failed to remove income source. Default sources cannot be removed.")


def render_export_section():
    """Render export to CSV section"""
    st.subheader("📥 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_period = st.selectbox(
            "Select Period",
            options=["Current Month", "Last 3 Months", "Last 6 Months", "Current Year", "All Time"]
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        export_button = st.button("📊 Generate CSV", use_container_width=True)
    
    if export_button:
        # Get expenses based on period
        now = datetime.now()
        
        if export_period == "Current Month":
            from utils.helpers import get_current_month_range
            start_date, end_date = get_current_month_range()
        elif export_period == "Last 3 Months":
            from datetime import timedelta
            start_date = now - timedelta(days=90)
            end_date = now
        elif export_period == "Last 6 Months":
            from datetime import timedelta
            start_date = now - timedelta(days=180)
            end_date = now
        elif export_period == "Current Year":
            start_date = datetime(now.year, 1, 1)
            end_date = now
        else:  # All Time
            start_date = None
            end_date = None
        
        expenses = ExpenseModel.get_expenses(start_date, end_date)
        
        if not expenses:
            st.warning("No expenses found for the selected period.")
        else:
            # Convert to DataFrame
            df = pd.DataFrame(expenses)
            
            # Format data
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df = df[["date", "category", "description", "amount"]]
            df.columns = ["Date", "Category", "Description", "Amount"]
            
            # Convert to CSV
            csv = df.to_csv(index=False)
            
            # Download button
            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"expenses_{export_period.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
            st.success(f"✅ Found {len(expenses)} expenses for {export_period.lower()}!")
            
            # Preview
            with st.expander("📋 Preview Data"):
                st.dataframe(df, use_container_width=True, hide_index=True)
