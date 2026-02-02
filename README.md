# Budget Tracking Web Application 💰

A full-featured personal finance tracker built with **Streamlit** and **MongoDB**, providing real-time budget awareness and meaningful visual insights into your spending patterns and income.

![Budget Tracker](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![Streamlit](https://img.shields.io/badge/streamlit-1.31.0-red)
![MongoDB](https://img.shields.io/badge/mongodb-latest-green)

## ✨ Features

### Core Functionality
- 💰 **Monthly Budget Configuration** - Set and modify your monthly budget (default: ₹50,000)
- 💳 **Transactions Page** - Dedicated page for adding expenses and income with tabbed interface
- 📝 **Daily Expense Entry** - Easy-to-use form with validation for adding expenses
- 💸 **Income Tracking** - Record and track your income sources
- 📊 **Live Financial Status** - Real-time updates showing income, expenses, and net balance
- ✏️ **Edit & Delete** - Modify or remove expenses as needed
- 📥 **Export to CSV** - Download your expense data for external analysis

### Analytics Dashboard
- 📈 **Daily Expense Trend** - Line chart showing daily spending patterns
- 📊 **Monthly Comparison** - Bar chart comparing expenses across months
- 📅 **Yearly Overview** - Comprehensive view of annual spending
- 🥧 **Category Breakdown** - Pie chart showing expense distribution by category

### Categories
- 🍔 Food
- 🚗 Transport
- 🏠 Rent
- 🛍️ Shopping
- 💡 Bills
- 📦 Other


## 📦 Installation

### 1. Clone or Navigate to Project Directory

```bash
cd C:\Users\SS\Documents\Expenses
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MongoDB Connection (Optional)

Create a `.env` file in the project root if you need to customize the MongoDB connection:

```env
MONGO_URI=mongodb://localhost:27017/



## 🗂️ Project Structure
Expenses/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                  # This file
├── .gitignore                 # Git ignore file
│
├── database/
│   ├── __init__.py
│   ├── connection.py          # MongoDB connection handler
│   ├── models.py              # Expense database operations (CRUD)
│   ├── income_model.py        # Income database operations (CRUD)
│   └── category_model.py      # Category management
│
├── utils/
│   ├── __init__.py
│   ├── validators.py          # Input validation
│   └── helpers.py             # Helper functions
│
└── components/
    ├── __init__.py
    ├── expense_form.py        # Expense entry form
    ├── income_form.py         # Income entry form
    ├── transactions.py        # Transactions page (expenses & income)
    ├── dashboard.py           # Analytics dashboard
    └── settings.py            # Settings page
```

## 🗄️ Database Schema

### Collection: `budgets`

```javascript
{
  _id: ObjectId,
  month: "2026-02",           // YYYY-MM format
  amount: 50000,              // Monthly budget in ₹
  created_at: ISODate,
  updated_at: ISODate
}
```

**Index**: `{ month: 1 }` (unique)

### Collection: `expenses`

```javascript
{
  _id: ObjectId,
  date: ISODate,              // Expense date
  category: String,           // Food, Transport, Rent, Shopping, Bills, Other
  description: String,        // Expense description
  amount: Number,             // Amount in ₹
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes**: 
- `{ date: -1 }` - For date-based queries
- `{ category: 1, date: -1 }` - For category analytics

### Collection: `income`

```javascript
{
  _id: ObjectId,
  date: ISODate,              // Income date
  source: String,             // Income source (e.g., Salary, Freelance, Investment)
  description: String,        // Income description
  amount: Number,             // Amount in ₹
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes**: 
- `{ date: -1 }` - For date-based queries
- `{ source: 1, date: -1 }` - For source analytics

### Collection: `categories`

```javascript
{
  _id: ObjectId,
  name: String,               // Category name
  created_at: ISODate
}
```

**Index**: `{ name: 1 }` (unique)

## 🛠️ Technology Stack

- **Frontend**: Streamlit 1.31.0
- **Database**: MongoDB with PyMongo 4.6.1
- **Data Processing**: Pandas 2.2.0
- **Visualizations**: Plotly 5.18.0
- **Configuration**: python-dotenv 1.0.1

## 🎨 Features Highlights

### Input Validation
- No negative amounts
- No future dates
- Required field checks
- Description length limits
- Category validation

### Real-time Updates
- Instant budget recalculation after adding expenses
- Live progress bars
- Automatic page refresh on data changes

### Interactive Charts
- Hover tooltips with detailed information
- Responsive design
- Color-coded categories
- Multiple visualization types

### User Experience
- Clean, intuitive interface
- Sidebar navigation
- Success/error messages
- Confirmation dialogs for destructive actions
- Loading states


## 📝 Tips for Better Budget Management

1. 📅 **Record Daily**: Add expenses daily for better accuracy
2. 🎯 **Set Realistic Budgets**: Base budgets on historical spending
3. 📊 **Review Weekly**: Check dashboard weekly to stay on track
4. 🏷️ **Use Correct Categories**: Helps with meaningful analytics
5. 💾 **Export Regularly**: Keep backups of your financial data
6. ⚠️ **Monitor Warnings**: Pay attention to budget alerts
7. 📈 **Analyze Trends**: Use charts to identify spending patterns



## 🎉 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Amazing Python web framework
- [MongoDB](https://www.mongodb.com/) - Flexible NoSQL database
- [Plotly](https://plotly.com/) - Interactive visualization library
- [Pandas](https://pandas.pydata.org/) - Data manipulation library

---

💡 **Happy Budgeting!** Track wisely, spend smartly! 💰