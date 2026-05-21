# Expense Tracker 📊

A personal finance management app built with Streamlit and MongoDB. Log expenses, track investments, automate recurring payments, and analyze your finances through interactive charts — all in a single dark-themed dashboard.

---

## Pages

### Dashboard
Financial overview filtered by year and month.

- **KPIs:** Total expenses, number of expense entries, total invested, number of investment entries
- **5 interactive charts (Plotly):**
  - *Daily Trend* — line chart of day-by-day spending for the selected month
  - *Monthly Comparison* — bar chart of the last 6 months
  - *Yearly Overview* — area line chart across all 12 months for a selected year
  - *Category Breakdown* — donut chart of expenses by category with a sorted summary table
  - *Investment Breakdown* — donut chart of investments by category with a sorted summary table

### Transactions
Add and manage expense entries.

- **Add Expense** — date picker, category selector, description, and amount
- **History table** — filterable by year, month, and category; shows date, category, description, amount, and inline Edit / Delete buttons
- **Edit form** — modify any field of an existing entry in-place

### Investments
Same structure as Transactions, but for investment entries.

- Supports categories: Mutual Fund, SIP, Stocks, PPF, NPS, Gold, Fixed Deposit, Other Investment
- History filterable by year, month, and category with inline Edit / Delete

### Payments
Schedule recurring monthly payments so they post automatically.

- **My Payments** — lists each scheduled payment as a card showing title, amount, type (Expense or Investment), category, day of month it runs, a color-coded status badge (Pending / Done this month / Executing today / Paused / Next month), and a collapsible execution history of the last 12 runs. Actions per card: *Execute Now*, *Pause / Resume*, *Edit*, *Delete*
- **Add Payment** — choose Expense or Investment, set name, amount, category, day of month (1–28), and an optional note
- **Scheduler Status** — shows current date/time, counts of executed / skipped / pending / next-month / failed payments, per-payment status reasons, and a *Force Execute All* button

### Settings
- **Expense Categories** — view all categories (defaults marked ⭐), add custom ones, remove custom ones
- **Investment Categories** — same controls for investment categories
- **Export Data** — generate and download a CSV of expenses for a chosen period (current month, last 3 months, last 6 months, current year, or all time)
- **Migrate Investments** — scans the Expenses collection for entries that belong to investment categories and bulk-moves them to the Investments collection

---

## Tech Stack

| Layer | Library | Version |
|---|---|---|
| UI | [Streamlit](https://streamlit.io) | 1.31 |
| Database | [MongoDB](https://www.mongodb.com) via PyMongo | 4.6 |
| Charts | [Plotly](https://plotly.com/python/) | 5.18 |
| Data | [Pandas](https://pandas.pydata.org) | 2.2 |

---

## Getting Started

### Prerequisites

- Python 3.9+
- MongoDB running locally (`mongodb://localhost:27017/`) or a remote URI

### Installation

```bash
# 1. Clone the repo
git clone <repo-url>
cd Expenses

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root to override the default MongoDB URI:

```env
MONGO_URI=mongodb://localhost:27017/
```

Other settings (currency symbol, default categories, chart colors) live in [config.py](config.py).

### Run

```bash
streamlit run app.py
```

App opens at `http://localhost:8501`.

---

## Project Structure

```
Expenses/
├── app.py                              # Entry point — page config, navigation, auto-scheduler trigger
├── config.py                           # DB connection, categories, chart colors, page meta
├── requirements.txt
│
├── components/
│   ├── dashboard.py                    # KPI cards and 5 interactive charts
│   ├── transactions.py                 # Add / edit / delete expenses
│   ├── investments.py                  # Add / edit / delete investments
│   ├── payments.py                     # Recurring payment scheduler
│   └── settings.py                     # Categories, CSV export, investment migration
│
├── database/
│   ├── connection.py                   # MongoDB connection singleton
│   ├── models.py                       # Expense CRUD
│   ├── investment_model.py             # Investment CRUD
│   ├── investment_category_model.py    # Investment category management
│   └── event_model.py                  # Recurring event scheduling and execution
│
└── utils/
    ├── helpers.py                      # Formatting and shared utilities
    └── validators.py                   # Input validation
```

---

## Currency

Configured for Indian Rupees (`₹`). To change, update `CURRENCY_SYMBOL` in [config.py](config.py).
