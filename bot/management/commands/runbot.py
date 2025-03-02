# bot/management/commands/runbot.py
import logging
from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import ApplicationBuilder
from bot.handlers.chat_restriction_decorator import register_decorated_handlers
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
        application = ApplicationBuilder().token(TOKEN).build()
        register_decorated_handlers(application)

        logger.info("Bot is starting...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)