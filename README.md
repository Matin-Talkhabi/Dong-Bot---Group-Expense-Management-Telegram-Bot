# Dong Bot - Group Expense Management Telegram Bot

A powerful Telegram bot designed for managing shared expenses in groups. Built with Python and the python-telegram-bot library, this bot helps groups track expenses, calculate balances, and determine optimal payment distributions.

## 🌟 Features

- **Group Management**: Create and join expense groups with unique codes
- **Expense Tracking**: Add expenses with detailed information (title, amount, participants)
- **Smart Balance Calculation**: Automatically calculate who owes what to whom
- **Optimal Payment Suggestions**: Suggest the most efficient way to settle debts
- **Member Management**: Invite members with approval system
- **Persistent Storage**: SQLite database for reliable data storage
- **User-Friendly Interface**: Intuitive Persian language interface with inline keyboards

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Required Python packages

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "Dong"
   ```

2. **Install dependencies**
   ```bash
   pip install python-telegram-bot sqlite3
   ```

3. **Set up the database**
   ```bash
   cd "telegram bot/tel file"
   python sq_createor.py
   ```

4. **Configure the bot**
   - Edit `my.py` and replace the `TOKEN` variable with your bot token
   ```python
   TOKEN = "YOUR_BOT_TOKEN_HERE"
   ```

5. **Run the bot**
   ```bash
   python my.py
   ```

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/start` | Initialize the bot and show welcome message |
| `/help` | Display comprehensive help guide |
| `/new_dong` | Create a new expense group |
| `/join_dong` | Join an existing group using a code |
| `/add_expense` | Add a new expense to the current group |
| `/show_status` | View financial status and payment suggestions |
| `/members` | List all group members |
| `/cancel` | Cancel current operation |

## 💡 How It Works

### 1. Creating a Group
```
User: /new_dong
Bot: 📝 نام گروه جدید را وارد کنید:
User: Trip to Qom
Bot: ✅ گروه با موفقیت ساخته شد!
     🏠 Trip to Qom (DNG_****)
     ──────────────────────────────
```

### 2. Adding Expenses
```
User: /add_expense
Bot: 📝 عنوان هزینه را وارد کنید:
User: sohan
Bot: 💰 مبلغ هزینه را وارد کنید (تومان):
User: 500000
Bot: 👥 اعضای گروه:
     1. shinomiya 
     2. chika 
     3. Miko
     📝 شماره اعضای شرکت‌کننده را وارد کنید (مثل: 1,2,3):
User: 1,2,3
Bot: 👤 چه کسی هزینه را پرداخت کرده؟
     [Inline buttons for payer selection]
```

### 3. Viewing Financial Status
```
User: /show_status
Bot: 🏠 Trip to Qom (DNG_****)
     ──────────────────────────────
     💰 وضعیت مالی:

     📋 لیست پرداخت‌های لازم:

     1. 💸 chika  → shinomiya 
        💰 مبلغ: 166,667 تومان

     2. 💸 Miko → shinomiya 
        💰 مبلغ: 166,667 تومان

     📊 خلاصه وضعیت:
     ➖ chika : 166,667 تومان بدهی
     ➖ Miko: 166,667 تومان بدهی
     ➕ shinomiya : 333,334 تومان طلب
```

## 🏗️ Architecture

### Database Schema

The bot uses SQLite with the following tables:

- **users**: Stores user information (user_id, username, first_name)
- **dongs**: Stores group information (code, title, owner_id)
- **dong_members**: Manages group membership (code, user_id, status)
- **expenses**: Tracks all expenses (code, title, amount, payer_id, participants)

### Key Components

1. **Database Helpers**: Functions for database operations
2. **Command Handlers**: Process user commands
3. **Step Router**: Manages multi-step operations
4. **Callback Handler**: Handles inline keyboard interactions
5. **Balance Calculator**: Computes optimal payment distributions

## 🔧 Configuration

### Environment Variables
- `TOKEN`: Your Telegram bot token (required)

### Database
- Database file: `dong_bot.db`
- Auto-created on first run
- Stores all user and expense data

## 📱 Usage Examples

### Example 1: Weekend Trip
1. Create group: "Weekend Trip"
2. Add expenses:
   - Hotel: 800,000 تومان (paid by shinomiya )
   - Food: 300,000 تومان (paid by chika )
   - Transportation: 200,000 تومان (paid by Miko)
3. View status to see who owes what

### Example 2: Shared Apartment
1. Create group: "Apartment Expenses"
2. Add monthly expenses:
   - Rent: 2,000,000 تومان
   - Utilities: 500,000 تومان
   - Internet: 200,000 تومان
3. Track payments and balances

## 🛠️ Development

### Project Structure
```
Dong/
├── dong_bot.db
├── main.py (main bot file)
└── README.md
```

### Adding New Features

1. **New Commands**: Add command handlers in the main section
2. **UI Improvements**: Update message formatting and inline keyboards

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the developer: @KMmatin_00

## 🔮 Future Enhancements

- [ ] Export expense reports to PDF
- [ ] Multiple currency support
- [ ] Expense categories and tags
- [ ] Recurring expense tracking
- [ ] Payment history
- [ ] Group statistics and analytics
- [ ] Web dashboard integration

---

**Made with ❤️ for better group expense management** 