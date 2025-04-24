import json
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

TOKEN = "7173685474:AAGQvbOfTv7bcevZQ_NPWGOcQuAMJiMu6UY"
OWNER_ID = 6411315434
BOT_USERNAME = "@WorldUpiCashBot"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    with open("users.json", "r") as file:
        users = json.load(file)
except:
    users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    username = user.username or user.first_name

    if user_id not in users:
        users[user_id] = {
            "name": username,
            "referral_code": f"{user_id}",
            "referred_by": None,
            "coins": 0,
        }

        if context.args:
            referred_by = context.args[0]
            if referred_by != user_id and referred_by in users:
                users[user_id]["referred_by"] = referred_by
                users[referred_by]["coins"] += 1
                await context.bot.send_message(
                    chat_id=referred_by,
                    text=f"{username} joined using your referral! You earned 1 coin.",
                )

        with open("users.json", "w") as file:
            json.dump(users, file, indent=4)

    keyboard = [
        [InlineKeyboardButton("My Coins", callback_data="coins")],
        [InlineKeyboardButton("Refer Friends", callback_data="refer")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Welcome! Use the buttons below:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    data = query.data

    if data == "coins":
        coins = users.get(user_id, {}).get("coins", 0)
        await query.edit_message_text(text=f"You have {coins} coins.")
    elif data == "refer":
        referral_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        await query.edit_message_text(
            text=f"Share this link with friends to earn coins:\n{referral_link}"
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
