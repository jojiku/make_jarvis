from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext 
from src.utils.config import TELEGRAM_PARAMS 
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

 
TOKEN = TELEGRAM_PARAMS['telegram_token']

PROMPT_PARAMS = { 
    "help_message": "Better to ask @goooooooosh for help",
    "new_chat": "I've successfully forgotten our previous interactions 😊 *bows* Reply with 'new' to me please"
}
 
async def help(update: Update, context: CallbackContext):
    await update.message.reply_text(PROMPT_PARAMS["help_message"])
 
async def new(update: Update, context: CallbackContext):
   
    user_id = update.message.from_user.id
    await update.message.reply_text(f"Attempting to delete history for user_name: {str(user_id)}")
    try:
        context.bot_data['clear_messages'](str(user_id))
        await update.message.reply_text(PROMPT_PARAMS["new_chat"])
    except Exception as e:
 
        await update.message.reply_text(f"Failed to clear history: {str(e)}")

 
async def message_handler(update: Update, context: CallbackContext):
    user_message = update.message.text
    chat_id = update.message.chat_id
    try:
        response = context.bot_data['handle_conversation'](str(chat_id), user_message)
        await context.bot.send_message(chat_id=chat_id, text=response["text"])
    except Exception as e:
        
        await context.bot.send_message(chat_id=chat_id, text="Error processing your request: " + str(e))

 
def init_telegram_bot(handle_ai_conversation, handle_clear_history):
    application = Application.builder().token(TOKEN).build()

    application.bot_data['handle_conversation'] = handle_ai_conversation
    application.bot_data['clear_history'] = handle_clear_history

    application.add_handler(CommandHandler("help", help)) 
    application.add_handler(CommandHandler("new", new))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    application.run_polling()

async def new(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    try:
        result = context.bot_data['clear_history'](str(user_id))
        await update.message.reply_text(result)
    except Exception as e:
        await update.message.reply_text(f"Failed to clear history: {str(e)}")



