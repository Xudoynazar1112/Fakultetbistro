# bot/handlers/chat_restriction_decorator.py
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from ..config import ADMIN_GROUP_ID
from ..handlers.db_handlers import get_user, create_order, get_product
from ..handlers.main_handlers import send_main_menu
from ..globals import *

def restrict_to_private(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if not chat or chat.type != "private":
            if update.message:
                await update.message.reply_text("This bot works only in private chats.")
            elif update.callback_query:
                await update.callback_query.answer("This bot works only in private chats.")
            return  # Stop processing non-private chats
        return await func(update, context)  # Continue with the handler
    return wrapper

async def process_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.location:
        return

    user = await context.application.bot.get_chat_member(update.effective_chat.id, update.effective_user.id).user
    user_instance = await get_user(user.id)
    location = update.message.location
    carts = context.user_data.get("carts", {})
    order = await create_order(user_instance, carts, status=1, payment_type=context.user_data.get("paymenttype"), longitude=location.longitude, latitude=location.latitude)

    text = "\n" if carts else "No items in cart."
    if carts:
        lang_code = LANGUAGE_CODE[user_instance.lang_id]
        total_price = 0
        for cart, val in carts.items():
            product = await get_product(cart)
            text += f"{val} x {getattr(product, f'name_{lang_code}')}\n"
            total_price += product.price * val
        text += f"\n{ALL[user_instance.lang_id]}: {total_price} {SUM[user_instance.lang_id]}"

    if ADMIN_GROUP_ID and ADMIN_GROUP_ID != -1:
        await context.bot.send_message(
            chat_id=ADMIN_GROUP_ID,
            text=f"<b>Yangi buyurtma:</b>\n\n"
                 f"👤 <b>Ism-familiya:</b> {user_instance.first_name} {user_instance.last_name}\n"
                 f"📞 <b>Telefon raqam:</b> {user_instance.phone_number}\n\n"
                 f"📥 <b>Buyurtma:</b>\n{text}",
            parse_mode='HTML'
        )
        await context.bot.send_location(ADMIN_GROUP_ID, latitude=location.latitude, longitude=location.longitude)
    await update.message.reply_text("Your order has been placed successfully!")
    context.user_data['carts'] = {}  # Clear cart after order
    await send_main_menu(update, context, user_instance)

# Helper to register handlers with the decorator
def register_decorated_handlers(application):
    from .main_handlers import start_handler
    from .callback_handlers import callback_handler

    application.add_handler(CommandHandler('start', restrict_to_private(start_handler)))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, restrict_to_private(handle_text)))
    application.add_handler(MessageHandler(filters.CONTACT, restrict_to_private(handle_contact)))
    application.add_handler(MessageHandler(filters.LOCATION, restrict_to_private(process_order)))
    application.add_handler(CallbackQueryHandler(restrict_to_private(handle_callback)))

# Placeholder handlers (delegate to existing ones, removing private chat checks)
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from .main_handlers import message_handler
    await message_handler(update, context)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from .main_handlers import contact_handler
    await contact_handler(update, context)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    from .callback_handlers import callback_handler
    await callback_handler(update, context)