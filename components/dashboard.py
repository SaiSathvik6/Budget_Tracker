import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import config
from database.models import ExpenseModel
from utils.helpers import format_currency, get_month_name, get_month_start_end


def render_dashboard():
    st.header("📊 Dashboard & Analytics")

    available_years = ExpenseModel.get_available_years()
    available_year_months = ExpenseModel.get_available_year_months()
    current_year = datetime.now().year
    current_month = datetime.now().month

    col1, col2 = st.columns(2)

    with col1:
        if current_year not in available_years:
            available_years.insert(0, current_year)
        selected_year = st.selectbox(
            "📅 Select Year",
            options=available_years,
            index=0,
            key="dashboard_year_select",
        )

    with col2:
        available_months = sorted([ym[1] for ym in available_year_months if ym[0] == selected_year])
        if selected_year == current_year and current_month not in available_months:
            available_months = sorted(available_months + [current_month], reverse=True)

        if available_months:
            default_index = 0
            if selected_year == current_year:
                try:
                    default_index = available_months.index(current_month)
                except ValueError:
                    default_index = 0
            selected_month = st.selectbox(
                "📅 Select Month",
                options=available_months,
                format_func=get_month_name,
                index=default_index,
            )
        else:
            selected_month = current_month
            st.info(f"No data available for {selected_year}. Showing current month.")

    start_date, end_date = get_month_start_end(selected_year, selected_month)
    filter_label = f"{get_month_name(selected_month)} {selected_year}"

    st.divider()
    render_kpi_cards(start_date, end_date, filter_label)
    st.divider()

    chart_tab = st.radio(
        "View",
        options=["📈 Daily Trend", "📊 Monthly Comparison", "📅 Yearly Overview", "🥧 Category Breakdown"],
        horizontal=True,
        key="dashboard_chart_tab",
        label_visibility="collapsed",
    )

    st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

    if chart_tab == "📈 Daily Trend":
        render_daily_trend(start_date, end_date, filter_label)
    elif chart_tab == "📊 Monthly Comparison":
        render_monthly_comparison()
    elif chart_tab == "📅 Yearly Overview":
        render_yearly_overview()
    elif chart_tab == "🥧 Category Breakdown":
        render_category_breakdown(start_date, end_date, filter_label)

    st.divider()


def render_kpi_cards(start_date, end_date, filter_label):
    expenses = ExpenseModel.get_expenses(start_date, end_date) if (start_date and end_date) else ExpenseModel.get_expenses()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💸 Total Expenses", format_currency(sum(e["amount"] for e in expenses)))
    with col2:
        st.metric("📊 Transactions", str(len(expenses)))


def render_daily_trend(start_date, end_date, filter_label):
    st.subheader(f"Daily Expense Trend ({filter_label})")

    if not start_date or not end_date:
        st.info("Daily trend is not available for 'All Time'. Please select a specific period.")
        return

    daily_data = ExpenseModel.get_daily_totals(start_date, end_date)

    if daily_data.empty:
        st.info(f"No expenses recorded for {filter_label}.")
        return

    fig = px.line(
        daily_data,
        x="date",
        y="amount",
        title=f"Daily Spending Pattern - {filter_label}",
        labels={"date": "Date", "amount": f"Amount ({config.CURRENCY_SYMBOL})"},
        markers=True,
    )
    fig.update_traces(line_color="#4ECDC4", line_width=3, marker=dict(size=8))
    fig.update_layout(hovermode="x unified", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)


def render_monthly_comparison():
    st.subheader("Monthly Expense Comparison (Last 6 Months)")

    now = datetime.now()
    monthly_data = []

    for i in range(5, -1, -1):
        month_date = now - timedelta(days=30 * i)
        total = ExpenseModel.get_monthly_total(month_date.year, month_date.month)
        if total > 0:
            monthly_data.append({
                "month": f"{get_month_name(month_date.month)} {month_date.year}",
                "amount": total,
            })

    if not monthly_data:
        st.info("No expense data available for the last 6 months.")
        return

    fig = px.bar(
        pd.DataFrame(monthly_data),
        x="month",
        y="amount",
        title="Monthly Spending Comparison",
        labels={"month": "Month", "amount": f"Amount ({config.CURRENCY_SYMBOL})"},
        color="amount",
        color_continuous_scale="Teal",
    )
    fig.update_layout(showlegend=False, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)


def render_yearly_overview():
    st.subheader("Yearly Expense Overview")

    available_years = ExpenseModel.get_available_years()
    if not available_years:
        st.info("No expense data available yet.")
        return

    year = st.selectbox("Select Year", options=available_years, index=0, key="yearly_overview_year")
    monthly_totals = ExpenseModel.get_yearly_monthly_totals(year)

    yearly_data = [
        {"month": get_month_name(m), "amount": monthly_totals[m]}
        for m in range(1, 13)
        if monthly_totals[m] > 0
    ]

    if not yearly_data:
        st.info(f"No expense data available for {year}.")
        return

    df = pd.DataFrame(yearly_data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["month"], y=df["amount"],
        mode="lines+markers",
        name="Expenses",
        line=dict(color="#45B7D1", width=3),
        marker=dict(size=10),
        fill="tozeroy",
        fillcolor="rgba(69, 183, 209, 0.2)",
    ))
    fig.update_layout(
        title=f"Monthly Expenses for {year}",
        xaxis_title="Month",
        yaxis_title=f"Amount ({config.CURRENCY_SYMBOL})",
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_category_breakdown(start_date, end_date, filter_label):
    st.subheader(f"Category-wise Expense Breakdown ({filter_label})")

    if not start_date or not end_date:
        expenses = ExpenseModel.get_expenses()
        if not expenses:
            st.info("No expenses recorded yet.")
            return
        category_data = {}
        for exp in expenses:
            cat = exp["category"]
            category_data[cat] = category_data.get(cat, 0) + exp["amount"]
    else:
        category_data = ExpenseModel.get_category_breakdown(start_date, end_date)

    category_data = {k: v for k, v in category_data.items() if v > 0}
    if not category_data:
        st.info(f"No expenses recorded for {filter_label}.")
        return

    df = pd.DataFrame(list(category_data.items()), columns=["category", "amount"])

    color_map = config.CHART_COLORS.copy()
    for cat in df["category"].unique():
        if cat not in color_map:
            color_map[cat] = "#95A5A6"

    fig = px.pie(
        df,
        values="amount",
        names="category",
        title=f"Spending by Category - {filter_label}",
        color="category",
        color_discrete_map=color_map,
        hole=0.4,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.2f}<br>Percentage: %{percent}",
    )
    fig.update_layout(showlegend=True, legend=dict(orientation="v", yanchor="middle", y=0.5))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Category Summary")
    df_sorted = df.sort_values("amount", ascending=False).copy()
    df_sorted["amount"] = df_sorted["amount"].apply(format_currency)
    st.dataframe(df_sorted, use_container_width=True, hide_index=True)
