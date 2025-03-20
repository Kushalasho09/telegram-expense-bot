import logging
from pymongo import MongoClient
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, CallbackContext
from datetime import datetime

# ✅ Enable logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ✅ Telegram Bot Token
TOKEN = "8105165579:AAFeayPJmbFfJS5nImHC7uJ222-6sa7m5Yo"

# ✅ MongoDB Connection Setup
MONGO_URI = "mongodb+srv://expenseBotUser:Xis7IuLADOEN6vq4@cluster0.k40ou.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["expensesDB"]
users_collection = db["users"]
expenses_collection = db["expenses"]

VALID_NAMES = {"Kushal", "Manish", "Jagruti"}

# ✅ /start Command
async def start(update: Update, context: CallbackContext) -> None:
    """Handles the /start command."""
    user_id = update.message.chat_id
    user = users_collection.find_one({"user_id": user_id})

    if user:
        keyboard = [[InlineKeyboardButton("📊 View Expenses", callback_data="view_expenses")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
    f"Welcome back, {user['name']}! ✅\n🚬 Mama ni Moj 🚬\nMama na ashirwad 🙏", 
    reply_markup=reply_markup
)
    else:
        await update.message.reply_text("🌹 Tamaru Shubh Naam Lakho 🌹")


# ✅ Show Expense Options (View Expenses Button Click)
async def view_expense_options(update: Update, context: CallbackContext) -> None:
    """Show buttons for Kushal, Manish, Jagruti."""
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("Kushal", callback_data="expenses_Kushal")],
        [InlineKeyboardButton("Manish", callback_data="expenses_Manish")],
        [InlineKeyboardButton("Jagruti", callback_data="expenses_Jagruti")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.reply_text("Select a user to view expenses:", reply_markup=reply_markup)

# ✅ Show Expenses for Selected User
async def show_user_expenses(update: Update, context: CallbackContext) -> None:
    """Fetch and show expenses for a selected user along with total expenses."""
    query = update.callback_query
    _, selected_user = query.data.split("_")  # Extract username from callback data
    
    user = users_collection.find_one({"name": selected_user})
    if not user:
        await query.message.reply_text(f"❌ User {selected_user} not found.")
        return

    today_date = datetime.now().strftime("%Y-%m-%d")

    # ✅ Fetch user's expenses for today
    expenses = list(expenses_collection.find({"user_id": user["user_id"], "date": today_date}))
    
    expense_list = [f"💰 {exp['amount']} - {exp['item']} ({exp['date']})" for exp in expenses]
    total_user_expense = sum(exp["amount"] for exp in expenses) if expenses else 0

    user_expense_text = (
        f"📊 Expenses for {selected_user}:\n" + "\n".join(expense_list) +
        f"\n🔹 Total Expense: ₹{total_user_expense}"
    ) if expenses else f"📊 No expenses recorded for {selected_user} today."

    # ✅ Fetch total expenses for all users
    all_users_expenses = expenses_collection.aggregate([
        {"$match": {"date": today_date}},
        {"$group": {"_id": "$user_id", "total": {"$sum": "$amount"}}}
    ])

    total_all_users = 0
    all_users_text = "\n📊 Bdha No Total Kharach:\n"

    
    for entry in all_users_expenses:
        user_name = users_collection.find_one({"user_id": entry["_id"]})["name"]
        all_users_text += f"💰 {user_name}: ₹{entry['total']}\n"
        total_all_users += entry["total"]
    
    all_users_text += f"🔹 Grand Total: ₹{total_all_users}"

    # ✅ Send the message
    await query.message.reply_text(user_expense_text + "\n\n" + all_users_text)

# ✅ Main Function to Start the Bot
def main():
    """Starts the bot using polling."""
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(view_expense_options, pattern="view_expenses"))
    app.add_handler(CallbackQueryHandler(show_user_expenses, pattern="expenses_.*"))

    logger.info("🤖 Bot is running and connected to MongoDB...")
    app.run_polling()

# ✅ Run the bot
if __name__ == "__main__":
    main()
