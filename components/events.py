"""
Events component – manage and monitor recurring monthly expense events.
"""
import calendar
import streamlit as st
from datetime import datetime, date
from database.event_model import EventModel
from database.category_model import CategoryModel
from utils.helpers import format_currency
import config


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def render_events():
    """Render the Events management page."""
    st.header("🗓️ Recurring Events")
    st.markdown(
        "Schedule recurring expense entries that are **automatically posted** "
        "on a chosen day every month."
    )

    # ── Run due events automatically on page load ────────────────────────────
    _auto_run_scheduler()

    st.divider()

    tab1, tab2, tab3 = st.tabs(
        ["📋 My Events", "➕ Add Event", "⚡ Scheduler"]
    )

    with tab1:
        render_event_list()

    with tab2:
        render_add_event_form()

    with tab3:
        render_scheduler_panel()


# ─────────────────────────────────────────────────────────────────────────────
# Scheduler auto-run (called once per page load)
# ─────────────────────────────────────────────────────────────────────────────

def _auto_run_scheduler():
    """Silently execute any events that are due today (idempotent)."""
    results = EventModel.run_due_events()
    executed = [r for r in results if r["status"] == "executed"]
    if executed:
        names = ", ".join(r["event"]["title"] for r in executed)
        st.success(
            f"✅ **Auto-executed {len(executed)} event(s) this month:** {names}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1 – Event List
# ─────────────────────────────────────────────────────────────────────────────

def render_event_list():
    """Display all recurring events with inline controls."""
    events = EventModel.get_all_events()

    if not events:
        st.info("No recurring events yet. Go to **Add Event** to create one.")
        return

    now = datetime.now()
    today = now.date()

    for event in events:
        event_id = str(event["_id"])
        day = event["day_of_month"]
        last_day = calendar.monthrange(today.year, today.month)[1]
        effective_day = min(day, last_day)
        due_date = date(today.year, today.month, effective_day)

        already_done = EventModel.has_been_executed(event_id, today.year, today.month)
        is_active = event.get("is_active", True)

        # ── Card header colour ───────────────────────────────────────────────
        if not is_active:
            badge = "⏸️ Paused"
            border_color = "#555"
        elif already_done:
            badge = "✅ Done this month"
            border_color = "#2ecc71"
        elif today == due_date:
            badge = "🔄 Executing today"
            border_color = "#f39c12"
        elif today < due_date:
            badge = f"⏳ Due on {due_date.strftime('%d %b')} (this month)"
            border_color = "#3498db"
        else:
            # today > due_date and not yet executed — window passed
            import calendar as _cal
            if today.month == 12:
                nd = date(today.year + 1, 1, min(day, 31))
            else:
                nm_last = _cal.monthrange(today.year, today.month + 1)[1]
                nd = date(today.year, today.month + 1, min(day, nm_last))
            badge = f"🔜 Next month ({nd.strftime('%d %b %Y')})"
            border_color = "#9b59b6"

        with st.container():
            st.markdown(
                f"""
                <div style="border-left: 4px solid {border_color};
                            padding: 0.6rem 1rem;
                            margin-bottom: 0.5rem;
                            border-radius: 6px;
                            background: rgba(255,255,255,0.04);">
                    <span style="font-size:1.05rem; font-weight:600;">
                        {event['title']}
                    </span>
                    &nbsp;&nbsp;
                    <span style="font-size:0.82rem; color:#aaa;">
                        {badge}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            col_info, col_actions = st.columns([3, 1])

            with col_info:
                desc = event.get("description", "") or "—"
                st.markdown(
                    f"**Amount:** {format_currency(event['amount'])}  |  "
                    f"**Category:** {event['category']}  |  "
                    f"**Day:** {day}{_ordinal(day)} of every month  |  "
                    f"**Note:** {desc}"
                )

                # Execution history (collapsed)
                history = EventModel.get_execution_history(event_id)
                if history:
                    with st.expander(f"📜 Execution history ({len(history)} entries)"):
                        for h in history[:12]:
                            yr, mo = h["year"], h["month"]
                            month_name = calendar.month_abbr[mo]
                            executed_at = h.get("executed_at", "")
                            if isinstance(executed_at, datetime):
                                executed_at = executed_at.strftime("%d %b %Y %H:%M")
                            st.markdown(
                                f"- **{month_name} {yr}** — executed at {executed_at}"
                            )

            with col_actions:
                toggle_label = "⏸️ Pause" if is_active else "▶️ Resume"
                if st.button(toggle_label, key=f"toggle_{event_id}", use_container_width=True):
                    EventModel.toggle_event(event_id, not is_active)
                    st.rerun()

                if st.button("✏️ Edit", key=f"edit_{event_id}", use_container_width=True):
                    st.session_state["editing_event"] = event_id
                    st.rerun()

                if st.button("🗑️ Delete", key=f"del_{event_id}", use_container_width=True):
                    st.session_state[f"confirm_del_{event_id}"] = True
                    st.rerun()

                # Confirm delete
                if st.session_state.get(f"confirm_del_{event_id}"):
                    st.warning("Are you sure?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Yes", key=f"yes_{event_id}"):
                            EventModel.delete_event(event_id)
                            if f"confirm_del_{event_id}" in st.session_state:
                                del st.session_state[f"confirm_del_{event_id}"]
                            st.rerun()
                    with c2:
                        if st.button("No", key=f"no_{event_id}"):
                            del st.session_state[f"confirm_del_{event_id}"]
                            st.rerun()

        # ── Inline edit form ─────────────────────────────────────────────────
        if st.session_state.get("editing_event") == event_id:
            _render_edit_form(event)

        st.markdown("---")


def _render_edit_form(event):
    """Inline edit form for an existing event."""
    event_id = str(event["_id"])
    categories = CategoryModel.get_all_categories()

    st.markdown("#### ✏️ Edit Event")
    with st.form(f"edit_form_{event_id}"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Event Name", value=event["title"])
            amount = st.number_input(
                f"Amount ({config.CURRENCY_SYMBOL})",
                min_value=0.01,
                value=float(event["amount"]),
                step=0.01,
                format="%.2f",
            )
        with col2:
            cat_idx = categories.index(event["category"]) if event["category"] in categories else 0
            category = st.selectbox("Category", categories, index=cat_idx)
            day_of_month = st.number_input(
                "Day of Month (1–28)",
                min_value=1,
                max_value=28,
                value=int(event["day_of_month"]),
                help="Use 28 max so it works in February too.",
            )
        description = st.text_input("Description / Note", value=event.get("description", ""))
        is_active = st.checkbox("Active", value=event.get("is_active", True))

        c1, c2 = st.columns(2)
        with c1:
            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
        with c2:
            cancelled = st.form_submit_button("✖ Cancel", use_container_width=True)

    if submitted:
        if not title.strip():
            st.error("Event name cannot be empty.")
        elif amount <= 0:
            st.error("Amount must be positive.")
        else:
            ok = EventModel.update_event(
                event_id, title, category, amount, day_of_month, description, is_active
            )
            if ok:
                st.success("✅ Event updated!")
                del st.session_state["editing_event"]
                st.rerun()
            else:
                st.error("Failed to update event.")

    if cancelled:
        del st.session_state["editing_event"]
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Tab 2 – Add Event Form
# ─────────────────────────────────────────────────────────────────────────────

def render_add_event_form():
    """Form to create a new recurring event."""
    st.subheader("➕ Create Recurring Event")
    st.markdown(
        "Every event you create will **automatically generate an expense entry** "
        "on the chosen day of each month."
    )

    categories = CategoryModel.get_all_categories()

    with st.form("add_event_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input(
                "Event Name *",
                placeholder="e.g. Monthly Rent, Netflix",
                help="A short, descriptive label for this recurring expense.",
            )
            amount = st.number_input(
                f"Amount ({config.CURRENCY_SYMBOL}) *",
                min_value=0.01,
                value=500.0,
                step=0.01,
                format="%.2f",
            )

        with col2:
            category = st.selectbox("Category *", categories)
            day_of_month = st.number_input(
                "Day of Month *",
                min_value=1,
                max_value=28,
                value=1,
                help=(
                    "The day each month this expense is posted. "
                    "Max 28 so it's valid every month including February."
                ),
            )

        description = st.text_input(
            "Description / Note",
            placeholder="Optional extra detail",
        )

        submitted = st.form_submit_button("🗓️ Create Event", use_container_width=True, type="primary")

    if submitted:
        if not title.strip():
            st.error("❌ Event name cannot be empty.")
        elif amount <= 0:
            st.error("❌ Amount must be greater than zero.")
        else:
            ok = EventModel.create_event(title, category, amount, int(day_of_month), description)
            if ok:
                st.success(f"✅ Recurring event **'{title.strip()}'** created successfully!")
                st.balloons()
            else:
                st.error("❌ Failed to create event. Please try again.")


# ─────────────────────────────────────────────────────────────────────────────
# Tab 3 – Scheduler Panel
# ─────────────────────────────────────────────────────────────────────────────

def render_scheduler_panel():
    """Show scheduler status and allow manual trigger."""
    st.subheader("⚡ Scheduler Status")

    now = datetime.now()
    today = now.date()
    st.markdown(
        f"**Today:** {today.strftime('%A, %d %B %Y')}  |  "
        f"**Time:** {now.strftime('%H:%M')}"
    )
    st.divider()

    results = EventModel.run_due_events()

    if not results:
        st.info("No active recurring events found. Add one in the **Add Event** tab.")
        return

    # Summary counts
    counts = {"executed": 0, "skipped": 0, "pending": 0, "next_month": 0, "failed": 0}
    for r in results:
        counts[r["status"]] += 1

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("✅ Executed", counts["executed"])
    c2.metric("⏭️ Skipped", counts["skipped"])
    c3.metric("⏳ Pending", counts["pending"])
    c4.metric("🔜 Next Month", counts["next_month"])
    c5.metric("❌ Failed", counts["failed"])

    st.divider()
    st.markdown("#### Event-by-Event Status")

    status_icon = {
        "executed": "✅",
        "skipped": "⏭️",
        "pending": "⏳",
        "next_month": "🔜",
        "failed": "❌",
    }

    for r in results:
        ev = r["event"]
        icon = status_icon.get(r["status"], "❓")
        due = r["due_date"].strftime("%d %b")
        next_due = r.get("next_due")
        next_due_str = (
            f" · next: {next_due.strftime('%d %b %Y')}" if next_due else ""
        )
        st.markdown(
            f"{icon} **{ev['title']}** — {r['reason']}  "
            f"<span style='color:#888;font-size:0.85rem;'>"
            f"(scheduled {due}{next_due_str}, {format_currency(ev['amount'])} / month)</span>",
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown("#### 🔁 Force Re-run This Month")
    st.warning(
        "⚠️ This will re-create expense entries for **all active events** even if they "
        "already ran this month. Use only to correct missing entries."
    )
    if st.button("🔁 Force Execute All Events Now", type="primary"):
        force_results = EventModel.run_due_events(force=True)
        executed = [r for r in force_results if r["status"] == "executed"]
        failed = [r for r in force_results if r["status"] == "failed"]
        if executed:
            st.success(f"✅ Re-executed {len(executed)} event(s).")
        if failed:
            st.error(f"❌ {len(failed)} event(s) failed.")
        if not executed and not failed:
            st.info("No events to execute.")
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ordinal(n: int) -> str:
    """Return ordinal suffix for a number (1→'st', 2→'nd', etc.)."""
    if 11 <= (n % 100) <= 13:
        return "th"
    return {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
