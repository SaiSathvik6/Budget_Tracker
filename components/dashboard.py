"""
Dashboard component with analytics and visualizations
"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import config
from database.models import ExpenseModel
from database.category_model import CategoryModel
from utils.helpers import format_currency, calculate_percentage, get_current_month_range, get_month_name, get_month_start_end


def render_dashboard():
    """Render the analytics dashboard"""
    st.header("📊 Dashboard & Analytics")
    
    # Action Buttons
    col_fab1, col_fab2 = st.columns([1, 1])
    
    with col_fab1:
        if st.button("💸 Add Expense", use_container_width=True, type="primary", key="add_expense_btn"):
            st.session_state.page = "Transactions"
            st.rerun()
    
    with col_fab2:
        if st.button("💰 Add Income", use_container_width=True, type="secondary", key="add_income_btn"):
            st.session_state.page = "Transactions"
            st.rerun()
    
    st.divider()
    
    # Get available years and year-months from database
    available_years = ExpenseModel.get_available_years()
    available_year_months = ExpenseModel.get_available_year_months()
    
    # Year and Month selectors side by side
    col1, col2 = st.columns(2)
    
    with col1:
        # Year selector
        current_year = datetime.now().year
        if current_year not in available_years:
            available_years.insert(0, current_year)
        
        selected_year = st.selectbox(
            "📅 Select Year",
            options=available_years,
            index=0,
            help="Select year to view"
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
                help="Select month to view"
            )
        else:
            # No data for selected year, default to current month
            selected_month = current_month
            st.info(f"No data available for {selected_year}. Showing current month.")
    
    # Get date range for selected month
    start_date, end_date = get_month_start_end(selected_year, selected_month)
    filter_label = f"{get_month_name(selected_month)} {selected_year}"
    
    # Store filter in session state
    st.session_state.dashboard_filter = {
        "type": "Selected Period",
        "start_date": start_date,
        "end_date": end_date,
        "label": filter_label
    }
    st.divider()
    
    # KPI Cards (updated to use filter)
    render_kpi_cards(start_date, end_date, filter_label)
    
    st.divider()
    
    # Charts in tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Daily Trend", 
        "📊 Monthly Comparison", 
        "📅 Yearly Overview",
        "🥧 Category Breakdown"
    ])
    
    with tab1:
        render_daily_trend(start_date, end_date, filter_label)
    
    with tab2:
        render_monthly_comparison()
    
    with tab3:
        render_yearly_overview()
    
    with tab4:
        render_category_breakdown(start_date, end_date, filter_label)
    
    st.divider()
    
    # Recent expenses table (filtered)
    render_recent_expenses(start_date, end_date, filter_label)


def render_kpi_cards(start_date, end_date, filter_label):
    """Render KPI cards at the top of dashboard"""
    from database.income_model import IncomeModel
    
    # Get expenses and income for the filtered period
    if start_date and end_date:
        expenses = ExpenseModel.get_expenses(start_date, end_date)
        filtered_spent = sum(exp["amount"] for exp in expenses)
        filtered_income = IncomeModel.get_total_income(start_date, end_date)
    else:
        # All time
        expenses = ExpenseModel.get_expenses()
        filtered_spent = sum(exp["amount"] for exp in expenses)
        filtered_income = IncomeModel.get_total_income()
    
    net_balance = filtered_income - filtered_spent
    expense_count = len(expenses)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💰 Income",
            format_currency(filtered_income),
            delta=f"+{filtered_income:,.0f}" if filtered_income > 0 else None
        )
    
    with col2:
        st.metric(
            "💸 Expenses",
            format_currency(filtered_spent),
            delta=f"-{filtered_spent:,.0f}" if filtered_spent > 0 else None,
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "💵 Net Balance",
            format_currency(net_balance),
            delta="Income - Expenses",
            delta_color="normal" if net_balance >= 0 else "inverse"
        )
    
    with col4:
        st.metric(
            "📊 Transactions",
            f"{expense_count}",
            delta=f"{expense_count} expense{'s' if expense_count != 1 else ''}"
        )



def render_daily_trend(start_date, end_date, filter_label):
    """Render daily expense trend chart"""
    st.subheader(f"Daily Expense Trend ({filter_label})")
    
    if not start_date or not end_date:
        st.info("Daily trend is not available for 'All Time'. Please select a specific period.")
        return
    
    daily_data = ExpenseModel.get_daily_totals(start_date, end_date)
    
    if daily_data.empty:
        st.info(f"No expenses recorded for {filter_label}.")
        return
    
    # Create line chart
    fig = px.line(
        daily_data,
        x="date",
        y="amount",
        title=f"Daily Spending Pattern - {filter_label}",
        labels={"date": "Date", "amount": f"Amount ({config.CURRENCY_SYMBOL})"},
        markers=True
    )
    
    fig.update_traces(
        line_color="#4ECDC4",
        line_width=3,
        marker=dict(size=8)
    )
    
    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_monthly_comparison():
    """Render monthly comparison bar chart"""
    st.subheader("Monthly Expense Comparison (Last 6 Months)")
    
    now = datetime.now()
    monthly_data = []
    
    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30 * i)
        year = month_date.year
        month = month_date.month
        total = ExpenseModel.get_monthly_total(year, month)
        
        # Only add months with actual data
        if total > 0:
            monthly_data.append({
                "month": f"{get_month_name(month)} {year}",
                "amount": total
            })
    
    # Check if there's any data
    if not monthly_data:
        st.info("No expense data available for the last 6 months.")
        return
    
    df = pd.DataFrame(monthly_data)
    
    # Create bar chart
    fig = px.bar(
        df,
        x="month",
        y="amount",
        title="Monthly Spending Comparison",
        labels={"month": "Month", "amount": f"Amount ({config.CURRENCY_SYMBOL})"},
        color="amount",
        color_continuous_scale="Teal"
    )
    
    fig.update_layout(
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_yearly_overview():
    """Render yearly overview chart"""
    st.subheader("Yearly Expense Overview")
    
    # Get available years from database
    available_years = ExpenseModel.get_available_years()
    
    year = st.selectbox(
        "Select Year",
        options=available_years,
        index=0,
        key="yearly_overview_year"
    )
    
    monthly_totals = ExpenseModel.get_yearly_monthly_totals(year)
    
    yearly_data = []
    for month in range(1, 13):
        amount = monthly_totals[month]
        if amount > 0:  # Only include months with actual data
            yearly_data.append({
                "month": get_month_name(month),
                "amount": amount
            })
    
    # Check if there's any data
    if not yearly_data:
        st.info(f"No expense data available for {year}.")
        return
    
    df = pd.DataFrame(yearly_data)
    
    # Create line chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df["month"],
        y=df["amount"],
        mode="lines+markers",
        name="Expenses",
        line=dict(color="#45B7D1", width=3),
        marker=dict(size=10),
        fill="tozeroy",
        fillcolor="rgba(69, 183, 209, 0.2)"
    ))
    
    fig.update_layout(
        title=f"Monthly Expenses for {year}",
        xaxis_title="Month",
        yaxis_title=f"Amount ({config.CURRENCY_SYMBOL})",
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_category_breakdown(start_date, end_date, filter_label):
    """Render category-wise breakdown pie chart"""
    st.subheader(f"Category-wise Expense Breakdown ({filter_label})")
    
    if not start_date or not end_date:
        # For "All Time", get all expenses
        expenses = ExpenseModel.get_expenses()
        if not expenses:
            st.info("No expenses recorded yet.")
            return
        # Calculate category breakdown manually
        category_data = {}
        for exp in expenses:
            cat = exp["category"]
            category_data[cat] = category_data.get(cat, 0) + exp["amount"]
    else:
        category_data = ExpenseModel.get_category_breakdown(start_date, end_date)
    
    # Filter out zero values
    category_data = {k: v for k, v in category_data.items() if v > 0}
    
    if not category_data:
        st.info(f"No expenses recorded for {filter_label}.")
        return
    
    df = pd.DataFrame(list(category_data.items()), columns=["category", "amount"])
    
    # Create color map that includes unknown categories
    color_map = config.CHART_COLORS.copy()
    for category in df["category"].unique():
        if category not in color_map:
            # Assign a default color for unknown categories
            color_map[category] = "#95A5A6"  # Gray color for unknown
    
    # Create pie chart
    fig = px.pie(
        df,
        values="amount",
        names="category",
        title=f"Spending by Category - {filter_label}",
        color="category",
        color_discrete_map=color_map,
        hole=0.4
    )
    
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.2f}<br>Percentage: %{percent}"
    )
    
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show category table
    st.subheader("Category Summary")
    df_sorted = df.sort_values("amount", ascending=False)
    df_sorted["amount"] = df_sorted["amount"].apply(format_currency)
    st.dataframe(df_sorted, use_container_width=True, hide_index=True)


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
