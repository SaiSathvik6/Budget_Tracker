"""
Budget Tracking Web Application
Main Streamlit application
"""
import streamlit as st
import config
from components.dashboard import render_dashboard
from components.settings import render_settings
from components.transactions import render_transactions
from components.events import render_events
from database.event_model import EventModel


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

VALID_PAGES = {"Dashboard", "Transactions", "Settings", "Events"}

# ── Page state: seed from URL query param so reloads land on the right page ──
if "page" not in st.session_state:
    qp = st.query_params.get("page", "Dashboard")
    st.session_state.page = qp if qp in VALID_PAGES else "Dashboard"

# Keep URL in sync with session state (handles the initial load case)
st.query_params["page"] = st.session_state.page

# ── Run scheduler on every app load (idempotent – skips already-done events) ──
try:
    EventModel.run_due_events()
except Exception:
    pass  # Never block the UI for scheduler errors


def navigate(page: str):
    """Switch page, update URL param, and rerun."""
    st.session_state.page = page
    st.query_params["page"] = page
    if "editing_expense" in st.session_state:
        del st.session_state.editing_expense
    st.rerun()


# Sidebar navigation
with st.sidebar:
    st.title(f"{config.PAGE_ICON} Expense Tracker")
    st.markdown("---")

    current = st.session_state.page

    if st.button("📊 Dashboard", use_container_width=True,
                 type="primary" if current == "Dashboard" else "secondary"):
        navigate("Dashboard")

    if st.button("💳 Transactions", use_container_width=True,
                 type="primary" if current == "Transactions" else "secondary"):
        navigate("Transactions")

    if st.button("⚙️ Settings", use_container_width=True,
                 type="primary" if current == "Settings" else "secondary"):
        navigate("Settings")

    if st.button("🗓️ Events", use_container_width=True,
                 type="primary" if current == "Events" else "secondary"):
        navigate("Events")

    st.markdown("---")

# Main content area
try:
    if st.session_state.page == "Dashboard":
        render_dashboard()
    elif st.session_state.page == "Transactions":
        render_transactions()
    elif st.session_state.page == "Settings":
        render_settings()
    elif st.session_state.page == "Events":
        render_events()
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.exception(e)
    st.stop()
