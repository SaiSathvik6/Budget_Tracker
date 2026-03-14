"""
Database operations for recurring monthly events (scheduled expenses).
Each event fires automatically on a given day-of-month every month.
"""
from datetime import datetime, date
from typing import Dict, List, Optional
from bson import ObjectId
from database.connection import get_db


EVENTS_COLLECTION = "recurring_events"
EXECUTIONS_COLLECTION = "event_executions"   # tracks which months have been executed


class EventModel:
    """Handle recurring event CRUD and monthly execution logic."""

    # ------------------------------------------------------------------ #
    #  CRUD                                                                #
    # ------------------------------------------------------------------ #

    @staticmethod
    def create_event(
        title: str,
        category: str,
        amount: float,
        day_of_month: int,
        description: str = "",
        is_active: bool = True,
    ) -> bool:
        """Create a new recurring event."""
        db = get_db()
        try:
            event = {
                "title": title.strip(),
                "category": category,
                "amount": amount,
                "day_of_month": day_of_month,    # 1-28
                "description": description.strip(),
                "is_active": is_active,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
            db[EVENTS_COLLECTION].insert_one(event)
            return True
        except Exception as e:
            print(f"Error creating event: {e}")
            return False

    @staticmethod
    def get_all_events() -> List[Dict]:
        """Return all recurring events sorted by day_of_month."""
        db = get_db()
        try:
            return list(db[EVENTS_COLLECTION].find().sort("day_of_month", 1))
        except Exception as e:
            print(f"Error fetching events: {e}")
            return []

    @staticmethod
    def get_active_events() -> List[Dict]:
        """Return only active recurring events."""
        db = get_db()
        try:
            return list(
                db[EVENTS_COLLECTION].find({"is_active": True}).sort("day_of_month", 1)
            )
        except Exception as e:
            print(f"Error fetching active events: {e}")
            return []

    @staticmethod
    def update_event(
        event_id: str,
        title: str,
        category: str,
        amount: float,
        day_of_month: int,
        description: str,
        is_active: bool,
    ) -> bool:
        """Update an existing recurring event."""
        db = get_db()
        try:
            result = db[EVENTS_COLLECTION].update_one(
                {"_id": ObjectId(event_id)},
                {
                    "$set": {
                        "title": title.strip(),
                        "category": category,
                        "amount": amount,
                        "day_of_month": day_of_month,
                        "description": description.strip(),
                        "is_active": is_active,
                        "updated_at": datetime.now(),
                    }
                },
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating event: {e}")
            return False

    @staticmethod
    def delete_event(event_id: str) -> bool:
        """Delete a recurring event and its execution records."""
        db = get_db()
        try:
            result = db[EVENTS_COLLECTION].delete_one({"_id": ObjectId(event_id)})
            # Clean up execution history
            db[EXECUTIONS_COLLECTION].delete_many({"event_id": event_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting event: {e}")
            return False

    @staticmethod
    def toggle_event(event_id: str, is_active: bool) -> bool:
        """Enable or disable a recurring event."""
        db = get_db()
        try:
            result = db[EVENTS_COLLECTION].update_one(
                {"_id": ObjectId(event_id)},
                {"$set": {"is_active": is_active, "updated_at": datetime.now()}},
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error toggling event: {e}")
            return False

    # ------------------------------------------------------------------ #
    #  Execution tracking                                                  #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _execution_key(event_id: str, year: int, month: int) -> str:
        return f"{event_id}_{year}_{month:02d}"

    @staticmethod
    def has_been_executed(event_id: str, year: int, month: int) -> bool:
        """Check whether an event has already been executed for a given month."""
        db = get_db()
        try:
            key = EventModel._execution_key(event_id, year, month)
            return db[EXECUTIONS_COLLECTION].find_one({"key": key}) is not None
        except Exception as e:
            print(f"Error checking execution: {e}")
            return False

    @staticmethod
    def mark_executed(event_id: str, year: int, month: int, expense_id=None) -> bool:
        """Record that an event was executed for a given month."""
        db = get_db()
        try:
            key = EventModel._execution_key(event_id, year, month)
            db[EXECUTIONS_COLLECTION].update_one(
                {"key": key},
                {
                    "$set": {
                        "key": key,
                        "event_id": event_id,
                        "year": year,
                        "month": month,
                        "executed_at": datetime.now(),
                        "expense_id": str(expense_id) if expense_id else None,
                    }
                },
                upsert=True,
            )
            return True
        except Exception as e:
            print(f"Error marking execution: {e}")
            return False

    @staticmethod
    def get_execution_history(event_id: str) -> List[Dict]:
        """Return execution history for a specific event (newest first)."""
        db = get_db()
        try:
            return list(
                db[EXECUTIONS_COLLECTION]
                .find({"event_id": event_id})
                .sort("executed_at", -1)
            )
        except Exception as e:
            print(f"Error fetching execution history: {e}")
            return []

    # ------------------------------------------------------------------ #
    #  Scheduler                                                           #
    # ------------------------------------------------------------------ #

    @staticmethod
    def run_due_events(force: bool = False) -> List[Dict]:
        """
        Check all active events and execute any that are due this month.

        Execution rules (per event, per month):
          - today == due_date  AND  not yet executed  →  EXECUTE  ✅
          - today <  due_date                         →  PENDING (upcoming this month) ⏳
          - today >  due_date  AND  not yet executed  →  NEXT MONTH (window passed) 🔜
          - already executed this month               →  SKIPPED ⏭️

        'force=True' overrides the equality check and re-runs everything due this month.

        Returns a list of result dicts describing what happened.
        """
        from database.models import ExpenseModel

        now = datetime.now()
        today = now.date()
        results = []

        active_events = EventModel.get_active_events()

        for event in active_events:
            event_id = str(event["_id"])
            day = event["day_of_month"]

            # Clamp day to actual month length (e.g. Feb 28/29)
            import calendar
            last_day = calendar.monthrange(today.year, today.month)[1]
            effective_day = min(day, last_day)
            due_date = date(today.year, today.month, effective_day)

            # Compute next month's due date for display purposes
            if today.month == 12:
                next_due = date(today.year + 1, 1, min(day, 31))
            else:
                nm_last = calendar.monthrange(today.year, today.month + 1)[1]
                next_due = date(today.year, today.month + 1, min(day, nm_last))

            already_done = EventModel.has_been_executed(event_id, today.year, today.month)

            # ── Already executed this month ──────────────────────────────────
            if already_done and not force:
                results.append({
                    "event": event,
                    "status": "skipped",
                    "reason": "Already executed this month",
                    "due_date": due_date,
                    "next_due": next_due,
                })
                continue

            # ── Upcoming: due date is still in the future this month ─────────
            if today < due_date and not force:
                results.append({
                    "event": event,
                    "status": "pending",
                    "reason": f"Due on {due_date.strftime('%d %b %Y')} (this month)",
                    "due_date": due_date,
                    "next_due": next_due,
                })
                continue

            # ── Missed: scheduled day passed without execution ───────────────
            if today > due_date and not already_done and not force:
                results.append({
                    "event": event,
                    "status": "next_month",
                    "reason": (
                        f"Scheduled day ({due_date.strftime('%d %b')}) already passed — "
                        f"next execution on {next_due.strftime('%d %b %Y')}"
                    ),
                    "due_date": due_date,
                    "next_due": next_due,
                })
                continue

            # ── Execute: today == due_date  OR  force=True ───────────────────
            expense_date = datetime(today.year, today.month, effective_day)
            desc = event.get("description") or event["title"]
            success = ExpenseModel.create_expense(
                date=expense_date,
                category=event["category"],
                description=f"[Auto] {desc}",
                amount=event["amount"],
            )

            if success:
                EventModel.mark_executed(event_id, today.year, today.month)
                results.append({
                    "event": event,
                    "status": "executed",
                    "reason": f"Expense created for {due_date.strftime('%d %b %Y')}",
                    "due_date": due_date,
                    "next_due": next_due,
                })
            else:
                results.append({
                    "event": event,
                    "status": "failed",
                    "reason": "Failed to create expense — will retry next app load",
                    "due_date": due_date,
                    "next_due": next_due,
                })

        return results
