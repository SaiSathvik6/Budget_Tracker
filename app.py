"""
Budget Tracking Web Application
Main Streamlit application
"""
import streamlit as st
import config
from components.expense_form import render_expense_form
from components.income_form import render_income_form
from components.dashboard import render_dashboard
from components.settings import render_settings
from components.transactions import render_transactions


# Page configuration
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout=config.LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #000000;
        color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #333;
    }
    [data-testid="stMetricLabel"] {
        color: #cccccc !important;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        font-weight: 600;
    }
    div[data-testid="stExpander"] {
        background-color: #1e1e1e;
        border-radius: 0.5rem;
        border: 1px solid #333;
    }
    div[data-testid="stExpander"] details {
        background-color: #1e1e1e;
    }
    div[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background-color: #1e1e1e;
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# Sidebar navigation
with st.sidebar:
    st.title(f"{config.PAGE_ICON} Expense Tracker")
    st.markdown("---")
    
    # Navigation buttons
    if st.button("📊 Dashboard", use_container_width=True, 
                 type="primary" if st.session_state.page == "Dashboard" else "secondary"):
        st.session_state.page = "Dashboard"
        if "editing_expense" in st.session_state:
            del st.session_state.editing_expense
        st.rerun()
    
    if st.button("💳 Transactions", use_container_width=True,
                 type="primary" if st.session_state.page == "Transactions" else "secondary"):
        st.session_state.page = "Transactions"
        if "editing_expense" in st.session_state:
            del st.session_state.editing_expense
        st.rerun()
    
    if st.button("⚙️ Settings", use_container_width=True,
                 type="primary" if st.session_state.page == "Settings" else "secondary"):
        st.session_state.page = "Settings"
        if "editing_expense" in st.session_state:
            del st.session_state.editing_expense
        st.rerun()
    
    st.markdown("---")

# Main content area
try:
    if st.session_state.page == "Dashboard":
        render_dashboard()
    elif st.session_state.page == "Transactions":
        render_transactions()
    elif st.session_state.page == "Add Expense":
        render_expense_form()
    elif st.session_state.page == "Add Income":
        render_income_form()
    elif st.session_state.page == "Settings":
        render_settings()
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.exception(e)
