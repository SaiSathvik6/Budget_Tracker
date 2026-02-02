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

## 🚀 Prerequisites

Before running the application, ensure you have:

1. **Python 3.8 or higher** installed
2. **MongoDB** installed and running:
   - **Local MongoDB**: Download from [mongodb.com](https://www.mongodb.com/try/download/community)
   - **MongoDB Atlas**: Free cloud option at [mongodb.com/atlas](https://www.mongodb.com/cloud/atlas)

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
```

For MongoDB Atlas, use your connection string:
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
```

## 🎯 Quick Start

### 1. Start MongoDB

Ensure MongoDB is running:

**Local MongoDB:**
```bash
# Windows (if installed as service, it should already be running)
net start MongoDB

# macOS/Linux
sudo systemctl start mongod
```

**MongoDB Atlas:** No action needed - it's always available

### 2. Insert Sample Data (Optional)

Populate the database with sample expenses for testing:

```bash
python sample_data.py
```

This will create:
- Sample budgets for the last 3 months
- 40+ sample expenses across all categories
- Data spanning multiple months for testing analytics

### 3. Run the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📖 Usage Guide

### Adding Expenses and Income

1. Navigate to **"Transactions"** from the sidebar
2. Choose the appropriate tab:
   - **Add Expense**: For recording expenses
   - **Add Income**: For recording income
   3. Fill in the form:
   - **Date**: Select transaction date (defaults to today)
   - **Category**: Choose from dropdown (for expenses) or enter source (for income)
   - **Description**: Brief description of the transaction
   - **Amount**: Enter amount in ₹
4. Click **"Add Expense"** or **"Add Income"**
5. View instant updates in the sidebar's Financial Status section

### Viewing Dashboard

1. Navigate to **"Dashboard"** from the sidebar
2. Explore different visualizations:
   - **Daily Trend**: See spending patterns over the month
   - **Monthly Comparison**: Compare last 6 months
   - **Yearly Overview**: Select year to view annual data
   - **Category Breakdown**: Choose period (current month, 3 months, 6 months)
3. Scroll down to view recent expenses
4. Use the **"Edit or Delete Expense"** expander to modify entries

### Managing Settings

1. Navigate to **"Settings"** from the sidebar
2. **Budget Configuration**:
   - Update monthly budget amount
   - Optionally apply to future months
3. **Export Data**:
   - Select period (current month, 3 months, 6 months, year, all time)
   - Click "Generate CSV"
   - Download the file
4. **Monthly Reset**:
   - Use with caution - permanently deletes current month expenses

### Live Financial Status

The sidebar always shows:
- Current month's income
- Current month's expenses
- Net balance (income - expenses)
- Visual metrics with color-coded indicators
- Warnings when in deficit

## 🗂️ Project Structure

```
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

## 📊 Sample Screenshots

### Dashboard View
The dashboard displays:
- 4 KPI cards (Budget, Spent, Remaining, Usage %)
- Interactive charts in tabs
- Recent expenses table
- Edit/delete functionality

### Expense Entry
Clean form with:
- Date picker
- Category dropdown
- Description input
- Amount input with validation
- Quick stats below

### Settings
Comprehensive settings including:
- Budget configuration
- CSV export with period selection
- Monthly reset option
- About section

## 🔧 Troubleshooting

### MongoDB Connection Issues

**Error**: "Failed to connect to MongoDB"

**Solutions**:
1. Verify MongoDB is running: `mongod --version`
2. Check connection string in `.env` or `config.py`
3. For Atlas, verify network access and credentials
4. Check firewall settings

### Import Errors

**Error**: "ModuleNotFoundError"

**Solution**:
```bash
pip install -r requirements.txt --upgrade
```

### Port Already in Use

**Error**: "Address already in use"

**Solution**:
```bash
# Run on different port
streamlit run app.py --server.port 8502
```

## 🚀 Advanced Configuration

### Custom MongoDB Database Name

Edit `config.py`:
```python
DATABASE_NAME = "my_custom_budget_db"
```

### Change Default Budget

Edit `config.py`:
```python
DEFAULT_BUDGET = 75000  # ₹75,000
```

### Add Custom Categories

Edit `config.py`:
```python
CATEGORIES = [
    "Food",
    "Transport",
    "Rent",
    "Shopping",
    "Bills",
    "Healthcare",  # New category
    "Education",   # New category
    "Other"
]
```

## 📝 Tips for Better Budget Management

1. 📅 **Record Daily**: Add expenses daily for better accuracy
2. 🎯 **Set Realistic Budgets**: Base budgets on historical spending
3. 📊 **Review Weekly**: Check dashboard weekly to stay on track
4. 🏷️ **Use Correct Categories**: Helps with meaningful analytics
5. 💾 **Export Regularly**: Keep backups of your financial data
6. ⚠️ **Monitor Warnings**: Pay attention to budget alerts
7. 📈 **Analyze Trends**: Use charts to identify spending patterns

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📄 License

This project is open source and available for personal use.

## 🆘 Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify MongoDB connection
3. Ensure all dependencies are installed
4. Check Python version compatibility

## 🎉 Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Amazing Python web framework
- [MongoDB](https://www.mongodb.com/) - Flexible NoSQL database
- [Plotly](https://plotly.com/) - Interactive visualization library
- [Pandas](https://pandas.pydata.org/) - Data manipulation library

---

**Version**: 2.0.0  
**Last Updated**: February 2026  
**Author**: Budget Tracker Team

💡 **Happy Budgeting!** Track wisely, spend smartly! 💰
