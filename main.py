import os
import logging
from flask import Flask
from threading import Thread
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Fetch API keys from environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
generation_config = {"temperature": 0.7}
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

# Keep-Alive Web Server for Replit
app = Flask('')

@app.route('/')
def home():
    return "DS-Menza Bot is alive!"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()

# Telegram Bot Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text:
        return
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        response = model.generate_content(user_text)
        reply_text = response.text
    except Exception as e:
        reply_text = f"Oops, something went wrong with the AI brain: {e}"
        
    await update.message.reply_text(reply_text)

def main():
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        print("Error: Missing Telegram Token or Gemini API Key!")
        return

    # Start Flask ping server in background
    keep_alive()

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is starting up...")
    application.run_polling()

if __name__ == '__main__':
    main()
