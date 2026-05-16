import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import config
from database.models import ExpenseModel
from database.category_model import CategoryModel
from database.connection import get_db
from utils.helpers import get_current_month_range


def render_settings():
    st.header("⚙️ Settings")
    tab1, tab2 = st.tabs(["📦 Expense Categories", "📥 Export Data"])
    with tab1:
        render_category_management()
    with tab2:
        render_export_section()


def render_category_management():
    all_categories = CategoryModel.get_all_categories()

    st.info(f"**Current Categories ({len(all_categories)}):**")
    cols = st.columns(3)
    for idx, category in enumerate(all_categories):
        with cols[idx % 3]:
            if category in config.CATEGORIES:
                st.markdown(f"• {category} ⭐")
            else:
                st.markdown(f"• {category}")
    st.caption("⭐ = Default categories")
    st.divider()

    st.markdown("### ➕ Add New Category")
    with st.form("add_category_form"):
        new_category = st.text_input(
            "Category Name",
            placeholder="e.g., Healthcare, Education, Entertainment",
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
                new_cat_name = new_category.strip().capitalize()
                if CategoryModel.add_category(new_cat_name):
                    st.success(f"✅ Category '{new_cat_name}' added successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to add category. Please try again.")

    st.divider()
    st.markdown("### 🗑️ Remove Category")

    db = get_db()
    custom_cats = db["categories"].find_one({"_id": "custom_categories"})
    custom_categories = custom_cats.get("categories", []) if custom_cats else []

    if not custom_categories:
        st.info("ℹ️ No custom categories to remove. Default categories cannot be removed.")
    else:
        with st.form("remove_category_form"):
            category_to_remove = st.selectbox(
                "Select Custom Category to Remove",
                options=custom_categories,
            )
            remove_submitted = st.form_submit_button("🗑️ Remove Category", type="primary", use_container_width=True)
            if remove_submitted:
                if CategoryModel.remove_category(category_to_remove):
                    st.success(f"✅ Category '{category_to_remove}' removed!")
                    st.info("ℹ️ Existing expenses with this category are preserved.")
                    st.rerun()
                else:
                    st.error("❌ Failed to remove category. Default categories cannot be removed.")


def render_export_section():
    st.subheader("📥 Export Data")

    col1, col2 = st.columns(2)
    with col1:
        export_period = st.selectbox(
            "Select Period",
            options=["Current Month", "Last 3 Months", "Last 6 Months", "Current Year", "All Time"],
        )
    with col2:
        st.write("")
        st.write("")
        export_button = st.button("📊 Generate CSV", use_container_width=True)

    if export_button:
        now = datetime.now()
        if export_period == "Current Month":
            start_date, end_date = get_current_month_range()
        elif export_period == "Last 3 Months":
            start_date, end_date = now - timedelta(days=90), now
        elif export_period == "Last 6 Months":
            start_date, end_date = now - timedelta(days=180), now
        elif export_period == "Current Year":
            start_date, end_date = datetime(now.year, 1, 1), now
        else:
            start_date, end_date = None, None

        expenses = ExpenseModel.get_expenses(start_date, end_date)

        if not expenses:
            st.warning("No expenses found for the selected period.")
        else:
            df = pd.DataFrame(expenses)
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df = df[["date", "category", "description", "amount"]]
            df.columns = ["Date", "Category", "Description", "Amount"]
            csv = df.to_csv(index=False)

            st.download_button(
                label="⬇️ Download CSV",
                data=csv,
                file_name=f"expenses_{export_period.lower().replace(' ', '_')}_{now.strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.success(f"✅ Found {len(expenses)} expenses for {export_period.lower()}!")
            with st.expander("📋 Preview Data"):
                st.dataframe(df, use_container_width=True, hide_index=True)
