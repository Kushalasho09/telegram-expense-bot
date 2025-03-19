from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
import asyncio

TOKEN = "8105165579:AAFeayPJmbFfJS5nImHC7uJ222-6sa7m5Yo"

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! Welcome to the Family Expense Bot. Use /addexpense to log an expense.")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
