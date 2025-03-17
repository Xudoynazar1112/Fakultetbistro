import logging

from .db_handlers import *
from .keyboard_handlers import *
from ..config import ADMIN_GROUP_ID
from ..globals import *

logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_user.id
    try:
        user, created = await get_or_create_user(chat_id)
        if created or not user.lang_id:
            await update.message.reply_text(WELCOME_TEXT)
            await update.message.reply_text(CHOOSE_LANG, reply_markup=get_language_keyboard())
            context.user_data['state'] = 'registration'
        else:
            await send_main_menu(update, context, user)
        logger.info(f"User {chat_id} started the bot")
    except Exception as e:
        logger.error(f"Error in start_handler: {e}")
        await update.message.reply_text("An error occurred. Please try again.")

async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = await get_user(update.effective_user.id)
        if update.message.contact:
            user.phone_number = update.message.contact.phone_number
            await save_user(user)
            await send_main_menu(update, context, user)
            logger.info(f"User {user.chat_id} shared contact: {user.phone_number}")
    except Exception as e:
        logger.error(f"Error in contact_handler: {e}")
        await update.message.reply_text("Failed to process your contact. Try again.")

async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = await get_user(update.effective_user.id)
        location = update.message.location
        carts = context.user_data.get("carts", {})
        await create_order(user, carts, status=1, payment_type=context.user_data.get("paymenttype"), longitude=location.longitude, latitude=location.latitude)

        text = "\n" if carts else "No items in cart."
        if carts:
            lang_code = LANGUAGE_CODE[user.lang_id]
            total_price = 0
            for cart, val in carts.items():
                product = await get_product(cart)
                text += f"{val} x {getattr(product, f'name_{lang_code}')}\n"
                total_price += product.price * val
            text += f"\n{ALL[user.lang_id]}: {total_price} {SUM[user.lang_id]}"

        await context.bot.send_message(
            chat_id=ADMIN_GROUP_ID,
            text=f"<b>Yangi buyurtma:</b>\n\n"
                 f"👤 <b>Ism-familiya:</b> {user.first_name} {user.last_name}\n"
                 f"📞 <b>Telefon raqam:</b> {user.phone_number}\n\n"
                 f"📥 <b>Buyurtma:</b>\n{text}",
            parse_mode='HTML'
        )
        await context.bot.send_location(ADMIN_GROUP_ID, latitude=location.latitude, longitude=location.longitude)
        await update.message.reply_text(SUCCESS_MESSAGE[user.lang_id])
        context.user_data['carts'] = {}  # Clear cart after order
        await send_main_menu(update, context, user)
    except Exception as e:
        logger.error(f"Error in location_handler: {e}")
        await update.message.reply_text("An error occurred while processing your order.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        user = await get_user(update.effective_user.id)
        state = context.user_data.get('state', 'registration')
        text = update.message.text

        if state == 'registration':
            if not user.lang_id:
                if text == BTN_LANG_UZ:
                    user.lang_id = 1
                elif text == BTN_LANG_RU:
                    user.lang_id = 2
                else:
                    await update.message.reply_text(TEXT_LANG_WARNING)
                    return
                await save_user(user)
                await update.message.reply_text(TEXT_ENTER_FIRST_NAME[user.lang_id])
            elif not user.first_name:
                user.first_name = text
                await save_user(user)
                # await update.message.reply_text(TEXT_ENTER_LAST_NAME[user.lang_id])
                await update.message.reply_text(TEXT_ENTER_CONTACT[user.lang_id], reply_markup=get_contact_keyboard(user.lang_id))
            # elif not user.last_name:
            #     user.last_name = text
            #     await save_user(user)
            #     await update.message.reply_text(TEXT_ENTER_CONTACT[user.lang_id],
            #                                     reply_markup=get_contact_keyboard(user.lang_id))
            elif not user.phone_number:
                await update.message.reply_text("Please use the button to send your contact.",
                                                reply_markup=get_contact_keyboard(user.lang_id))
            else:
                await send_main_menu(update, context, user)

        elif state == 'main_menu':
            if text == BTN_ORDER[user.lang_id]:
                categories = await get_categories()
                await update.message.reply_text(TEXT_ORDER[user.lang_id],
                                                reply_markup=get_category_keyboard(categories, user.lang_id))
                context.user_data['state'] = 'ordering'
            elif text == BTN_MY_ORDERS[user.lang_id]:
                orders = await get_my_orders(user.chat_id)
                # response_text = f"<b>{ORDER_STATUS_HEADER[user.lang_id]}: {status_text}</b>\n\n"
                response_text = f"👤 <b>{NAME[user.lang_id]}</b> {user.first_name} {user.last_name}\n"
                response_text += f"📞 <b>{PHONE[user.lang_id]}</b> {user.phone_number}\n\n"
                lang_code = LANGUAGE_CODE[user.lang_id]
                buttons = []
                for order in orders:
                    order_products = await get_order_products(order)
                    text = "\n"
                    total_price = 0
                    for order_product in order_products:
                        product = await get_product(order_product.product_id)
                        text += f"{order_product.amount} x {getattr(product, f'name_{lang_code}')}\n"
                        total_price += product.price * order_product.amount
                    # text += f"\n{ALL[user.lang_id]}: {total_price} {SUM[user.lang_id]}"
                    response_text += f"📥 <b>Buyurtma #{order.id}:</b>\n{text}\n" if user.lang_id == 1 else f""
                    if order.status == 1:  # Add Cancel button only for pending orders
                        buttons.append([InlineKeyboardButton(
                            f"Bekor qilish #{order.id}" if user.lang_id == 1 else "Отменить",
                            callback_data=f"cancelorder_{order.id}"
                        )])
                await update.message.reply_text(response_text, parse_mode='HTML')
                context.user_data['state'] = 'my_orders'
            elif text == BTN_ABOUT_US[user.lang_id]:
                await update.message.reply_text(ABOUT_COMPANY[user.lang_id], parse_mode="HTML")
            elif text == BTN_SETTINGS[user.lang_id]:
                await update.message.reply_text(CHOOSE_LANG, reply_markup=get_language_keyboard())
                context.user_data['state'] = 'settings'
            elif text == BTN_COMMENTS[user.lang_id]:
                await update.message.reply_text(
                    text=COMMENTS[user.lang_id]
                )
                # context.user_data['state'] = 'comments'

        elif state == 'settings':
            if text == BTN_LANG_UZ:
                user.lang_id = 1
                await save_user(user)
                await send_main_menu(update, context, user)
            elif text == BTN_LANG_RU:
                user.lang_id = 2
                await save_user(user)
                await send_main_menu(update, context, user)
            else:
                await update.message.reply_text(TEXT_LANG_WARNING)
        elif state == 'comments':
            await save_comment(text, user)
            await update.message.reply_text(text=f"<i>{ANSWER_COMMENTS[user.lang_id]}</i>", parse_mode="HTML")
            context.user_data['state'] = 'main_menu'
            await send_main_menu(update, context, user)
    except Exception as e:
        logger.error(f"Error in message_handler: {e}")
        await update.message.reply_text("An error occurred. Please try again.")

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, user: CustomUser) -> None:
    keyboard = ReplyKeyboardMarkup(
        [
            [KeyboardButton(BTN_ORDER[user.lang_id])],
            [KeyboardButton(BTN_MY_ORDERS[user.lang_id]), KeyboardButton(BTN_ABOUT_US[user.lang_id])],
            [KeyboardButton(BTN_COMMENTS[user.lang_id]), KeyboardButton(BTN_SETTINGS[user.lang_id])]
        ],
        resize_keyboard=True
    )
    await update.message.reply_text(TEXT_MAIN_MENU[user.lang_id], reply_markup=keyboard)
    context.user_data['state'] = 'main_menu'
