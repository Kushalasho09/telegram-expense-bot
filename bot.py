import logging
import gspread
from google.oauth2.service_account import Credentials
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from datetime import datetime

# ✅ Enable logging for debugging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ✅ Telegram Bot Token
TOKEN = "8105165579:AAFeayPJmbFfJS5nImHC7uJ222-6sa7m5Yo"

# ✅ Google Sheets Configuration
SERVICE_ACCOUNT_FILE = "C:\\Users\\ASUS\\Desktop\\ExpenseShareBot\\credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SHEET_ID = "1UHSoyJ7VDXWsMc-qjEw81YpGCaFZ3NSA_X7ncZcs0FY"

# ✅ Authenticate and connect to Google Sheets
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1  # Select the first sheet

# ✅ Function to Calculate Total Expense of the Day
def calculate_daily_total(user_name):
    """Fetches all today's expenses from Google Sheets and sums them up."""
    today_date = datetime.now().strftime("%d-%m-%Y")
    records = sheet.get_all_values()  # Fetch all data from the sheet

    total = 0
    detailed_expenses = []
    for row in records[1:]:  # Skip header row
        if row[0] == today_date and row[1].lower() == user_name.lower():  # Match today's date and user's name
            try:
                amount = float(row[2])
                total += amount  # Add the amount
                detailed_expenses.append(f"{row[2]} - {row[3]}")
            except ValueError:
                logger.warning(f"Skipping invalid amount: {row[2]}")

    return total, detailed_expenses

# ✅ Function to Calculate Home Total Expense
def calculate_home_total():
    """Fetches all today's expenses from Google Sheets and sums them up for all users."""
    today_date = datetime.now().strftime("%d-%m-%Y")
    records = sheet.get_all_values()

    home_total = 0
    for row in records[1:]:  # Skip header row
        if row[0] == today_date:
            try:
                home_total += float(row[2])
            except ValueError:
                logger.warning(f"Skipping invalid amount: {row[2]}")

    return home_total

# ✅ /start Command
async def start(update: Update, context: CallbackContext) -> None:
    """Handles the /start command."""
    logger.info("User started the bot.")
    await update.message.reply_text("You're already logged in, Kushal! Use /addexpense to log an expense.")

# ✅ /addexpense Command
async def add_expense(update: Update, context: CallbackContext) -> None:
    """Handles the /addexpense command."""
    logger.info("User entered /addexpense")
    await update.message.reply_text("tamaro kharcho lakho. Aa rehte ralkhva no che : Amount-Item (50-Maggie)")

# ✅ Message Handler for Expenses
async def log_expense(update: Update, context: CallbackContext) -> None:
    """Processes user expense input and adds it to Google Sheets."""
    message_text = update.message.text.strip().lower()
    user_name = update.message.from_user.first_name  # Get user's first name

    logger.info(f"Received message: {message_text}")

    # ✅ If user types "bas", return today's total expense
    if message_text == "bas":
        total_expense, details = calculate_daily_total(user_name)
        home_total = calculate_home_total()
        
        # Format the message
        formatted_expenses = "\n".join(details) if details else "No expenses recorded."
        message = f"{formatted_expenses}\n-------------------\n💰 Total {user_name}'s expenses: ₹{total_expense}\n\n💰 Your home total expense today is: ₹{home_total}"
        
        # ✅ Add buttons for all users
        keyboard = [[InlineKeyboardButton("Kushal", callback_data="kushal"),
                     InlineKeyboardButton("Manish", callback_data="manish")],
                    [InlineKeyboardButton("Jagruti", callback_data="jagruti"),
                     InlineKeyboardButton("Hirva", callback_data="hirva")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(message, reply_markup=reply_markup)
        return

    try:
        # Validate message format (e.g., "400-Kapda")
        if "-" not in message_text:
            await update.message.reply_text("❌ Invalid format! Use: Amount-Item (e.g., 50-Maggie)")
            return

        amount, item = message_text.split("-", 1)
        amount = amount.strip()
        item = item.strip()
        today_date = datetime.now().strftime("%d-%m-%Y")  # Get today's date

        # Insert into Google Sheets
        sheet.append_row([today_date, user_name, amount, item])
        logger.info(f"✅ Expense added for {user_name}: {amount}-{item}")

        await update.message.reply_text(f"✅ Expense added for {user_name}: {amount}-{item}")
    except Exception as e:
        logger.error(f"Error adding expense: {e}")
        await update.message.reply_text("❌ Error adding expense. Please try again.")

# ✅ Main Function to Start the Bot
def main():
    """Starts the bot using polling."""
    app = Application.builder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addexpense", add_expense))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, log_expense))

    # Start polling
    logger.info("🤖 Bot is running...")
    app.run_polling()

# ✅ Run the bot
if __name__ == "__main__":
    main()
