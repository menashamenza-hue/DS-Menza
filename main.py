import os
import logging
import telegram
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import google.generativeai as genai

# Setup logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Fetch API keys from Render environment variables
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
# Using Gemini 1.5 Flash as requested
generation_config = {"temperature": 0.7}
model = genai.GenerativeModel(model_name="gemini-pro", generation_config=generation_config)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    if not user_text:
        return
    
    # Send a quick typing action so you know it's working
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # Ask Gemini to respond
        response = model.generate_content(user_text)
        reply_text = response.text
    except Exception as e:
        reply_text = f"Oops, something went wrong with the AI brain: {e}"
        
    await update.message.reply_text(reply_text)

def main():
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        print("Error: Missing Telegram Token or Gemini API Key in environment variables!")
        return

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    # Listen to any text messages sent to the bot
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is starting up...")
    application.run_polling()

if __name__ == '__main__':
    main()
