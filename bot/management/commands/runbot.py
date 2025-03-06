# bot/management/commands/runbot.py
import logging
import os
from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from bot.handlers import callback_handler
from bot.handlers.main_handlers import start_handler, message_handler, contact_handler, location_handler
from bot.config import TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Runs the Telegram bot'

    def handle(self, *args, **options):
        if not TOKEN:
            logger.error("Telegram token is missing or invalid. Please set TELEGRAM_TOKEN in .env or environment.")
            raise ValueError("Telegram token is required.")

        # Check for existing bot instance using a PID file
        pid_file = "/tmp/foodbot.pid"
        if os.path.exists(pid_file):
            with open(pid_file, "r") as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)  # Check if process exists
                logger.error("Another bot instance is already running with PID %d", pid)
                return
            except OSError:
                pass  # No process, proceed

        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(CommandHandler('start', start_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
        application.add_handler(MessageHandler(filters.CONTACT, contact_handler))
        application.add_handler(MessageHandler(filters.LOCATION, location_handler))
        application.add_handler(CallbackQueryHandler(callback_handler))

        # Add error handler
        async def error_handler(update, context):
            """Handle errors in the bot and log them."""
            logger.error("Exception while handling an update:", exc_info=context.error)

        application.add_error_handler(error_handler)

        logger.info("Bot is starting...")
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))

        application.run_polling(allowed_updates=Update.ALL_TYPES)

        # Clean up PID file on exit
        if os.path.exists(pid_file):
            os.remove(pid_file)