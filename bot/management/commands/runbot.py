# bot/management/commands/runbot.py
import logging
import os
from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from bot.handlers.main_handlers import start_handler
from bot.handlers.chat_restriction_decorator import register_decorated_handlers  # Or your handler registration
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
        register_decorated_handlers(application)  # Or your handler registration method

        logger.info("Bot is starting...")
        with open(pid_file, "w") as f:
            f.write(str(os.getpid()))

        application.run_polling(allowed_updates=Update.ALL_TYPES)

        # Clean up PID file on exit
        if os.path.exists(pid_file):
            os.remove(pid_file)