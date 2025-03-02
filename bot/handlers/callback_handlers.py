# bot/handlers/callback_handlers.py
import logging
from telegram.error import BadRequest
from telegram import InputMediaPhoto as telegramInputMediaPhoto

from .db_handlers import *
from .keyboard_handlers import *
from ..config import BASE_URL
from ..globals import *

logger = logging.getLogger(__name__)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data.split("_")
    user = await get_user(query.from_user.id)
    lang_id = user.lang_id

    try:
        await query.answer()
        if data[0] == "category":
            category_id = int(data[1])
            context.user_data['current_category'] = category_id  # Store for back navigation
            products = await get_products_by_category(category_id)
            new_text = TEXT_ORDER[lang_id]
            new_markup = get_product_keyboard(products, lang_id, category_id)
            if query.message.text != new_text or str(query.message.reply_markup) != str(new_markup):
                await query.message.edit_text(new_text, reply_markup=new_markup)
        elif data[0] == "product":
            product = await get_product(int(data[1]))
            caption = f"{TEXT_PRODUCT_PRICE[lang_id]} {product.price}\n{TEXT_PRODUCT_DESC[lang_id]}{getattr(product, f'description_{LANGUAGE_CODE[lang_id]}') or ''}"
            await query.message.delete()
            image_url = f"{BASE_URL}{product.image.url}" if product.image else "https://via.placeholder.com/150"
            print("Image URL:", image_url)
            if 'quantities' not in context.user_data:
                logger.debug(f"Initializing quantities for user {user.chat_id}")
                context.user_data['quantities'] = {}
            quantity = context.user_data['quantities'].get(product.id, 0)
            logger.debug(f"Product {product.id} quantity: {quantity}")
            await query.message.reply_photo(
                photo=image_url,
                caption=caption,
                reply_markup=get_quantity_keyboard(product.id, quantity, lang_id)
            )
        elif data[0] == "increase":
            product_id = int(data[1])
            if 'quantities' not in context.user_data:
                context.user_data['quantities'] = {}
            context.user_data['quantities'][product_id] = context.user_data['quantities'].get(product_id, 0) + 1
            product = await get_product(product_id)
            caption = f"{TEXT_PRODUCT_PRICE[lang_id]} {product.price}\n{TEXT_PRODUCT_DESC[lang_id]}{getattr(product, f'description_{LANGUAGE_CODE[lang_id]}') or ''}"
            image_url = f"{BASE_URL}{product.image.url}" if product.image else "https://via.placeholder.com/150"
            await query.message.edit_media(
                media=telegramInputMediaPhoto(media=image_url, caption=caption),
                reply_markup=get_quantity_keyboard(product_id, context.user_data['quantities'][product_id], lang_id)
            )
        elif data[0] == "decrease":
            product_id = int(data[1])
            if 'quantities' in context.user_data and product_id in context.user_data['quantities'] and context.user_data['quantities'][product_id] > 0:
                context.user_data['quantities'][product_id] -= 1
            product = await get_product(product_id)
            caption = f"{TEXT_PRODUCT_PRICE[lang_id]} {product.price}\n{TEXT_PRODUCT_DESC[lang_id]}{getattr(product, f'description_{LANGUAGE_CODE[lang_id]}') or ''}"
            image_url = f"{BASE_URL}{product.image.url}" if product.image else "https://via.placeholder.com/150"
            await query.message.edit_media(
                media=telegramInputMediaPhoto(media=image_url, caption=caption),
                reply_markup=get_quantity_keyboard(product_id, context.user_data['quantities'][product_id], lang_id)
            )
        elif data[0] == "addtocart":
            product_id = int(data[1])
            quantity = context.user_data['quantities'].get(product_id, 0)
            if quantity > 0:
                carts = context.user_data.get("carts", {})
                carts[product_id] = carts.get(product_id, 0) + quantity
                context.user_data["carts"] = carts
                context.user_data['quantities'][product_id] = 0  # Reset quantity after adding to cart
            await query.message.delete()
            categories = await get_categories()
            text = f"{AT_KORZINKA[lang_id]}:\n\n"
            lang_code = LANGUAGE_CODE[lang_id]
            total_price = 0
            for cart, val in context.user_data["carts"].items():
                product = await get_product(cart)
                text += f"{val} x {getattr(product, f'name_{lang_code}')}\n"
                total_price += product.price * val
            text += f"\n{ALL[lang_id]}: {total_price}"
            await query.message.reply_text(
                text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(BTN_KORZINKA[lang_id], callback_data="cart")],
                    *get_category_keyboard(categories, lang_id).inline_keyboard
                ])
            )
        elif data[0] == "back":
            product_id = int(data[1])
            await query.message.delete()
            category_id = context.user_data.get('current_category')
            if category_id:
                products = await get_products_by_category(category_id)
                await query.message.reply_text(TEXT_ORDER[lang_id],
                                               reply_markup=get_product_keyboard(products, lang_id, category_id))
            else:
                categories = await get_categories()
                await query.message.reply_text(TEXT_ORDER[lang_id],
                                               reply_markup=get_category_keyboard(categories, lang_id))
        elif data[0] == "backtocategories":
            await query.message.delete()
            categories = await get_categories()
            await query.message.reply_text(TEXT_ORDER[lang_id],
                                           reply_markup=get_category_keyboard(categories, lang_id))
        elif data[0] == "cart":
            carts = context.user_data.get("carts", {})
            text = f"{AT_KORZINKA[lang_id]}:\n\n"
            lang_code = LANGUAGE_CODE[lang_id]
            total_price = 0
            for cart, val in carts.items():
                product = await get_product(cart)
                text += f"{val} x {getattr(product, f'name_{lang_code}')}\n"
                total_price += product.price * val
            text += f"\n{ALL[lang_id]}: {total_price}"
            new_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Buyurtma berish", callback_data="order"),
                 InlineKeyboardButton("Savatchani bo'shatish", callback_data="cartclear")],
                [InlineKeyboardButton("Orqaga", callback_data="cartback")]
            ])
            if query.message.text != text or str(query.message.reply_markup) != str(new_markup):
                await query.message.edit_text(text, reply_markup=new_markup)
        elif data[0] == "cartclear":
            context.user_data["carts"] = {}
            categories = await get_categories()
            new_text = TEXT_ORDER[lang_id]
            new_markup = get_category_keyboard(categories, lang_id)
            if query.message.text != new_text or str(query.message.reply_markup) != str(new_markup):
                await query.message.edit_text(new_text, reply_markup=new_markup)
        elif data[0] == "cartback":
            categories = await get_categories()
            new_text = TEXT_ORDER[lang_id]
            new_markup = get_category_keyboard(categories, lang_id)
            if query.message.text != new_text or str(query.message.reply_markup) != str(new_markup):
                await query.message.edit_text(new_text, reply_markup=new_markup)
        elif data[0] == "mainmenu":
            await query.message.delete()
            await send_main_menu(query, context, user)
        elif data[0] == "order":
            await query.message.delete()
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="To'lov turini tanlang:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Naqd pul", callback_data="orderpayment_1"),
                     InlineKeyboardButton("Karta", callback_data="orderpayment_2")]
                ])
            )
        elif data[0] == "orderpayment":
            context.user_data['paymenttype'] = int(data[1])
            await query.message.delete()
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=SEND_LOCATION[lang_id],
                reply_markup=get_location_keyboard(lang_id)
            )
        elif data[0] == "orderstatus":
            if data[1] == "pending":
                orders = await get_my_order_pending(user.chat_id)
                status_text = BTN_ORDER_PENDING[lang_id]
            elif data[1] == "delivered":
                orders = await get_my_order_delivered(user.chat_id)
                status_text = BTN_ORDER_DELIVERED[lang_id]
            elif data[1] == "canceled":
                orders = await get_my_order_canceled(user.chat_id)
                status_text = BTN_ORDER_CANCELED[lang_id]

            if orders:
                response_text = f"<b>{ORDER_STATUS_HEADER[lang_id]}: {status_text}</b>\n\n"
                response_text += f"👤 <b>Ism-familiya:</b> {user.first_name} {user.last_name}\n"
                response_text += f"📞 <b>Telefon raqam:</b> {user.phone_number}\n\n"
                lang_code = LANGUAGE_CODE[lang_id]
                buttons = []
                for order in orders:
                    order_products = await get_order_products(order)
                    text = "\n"
                    total_price = 0
                    for order_product in order_products:
                        product = await get_product(order_product.product_id)
                        text += f"{order_product.amount} x {getattr(product, f'name_{lang_code}')}\n"
                        total_price += product.price * order_product.amount
                    text += f"\n{ALL[lang_id]}: {total_price} {SUM[lang_id]}"
                    response_text += f"📥 <b>Buyurtma #{order.id}:</b>\n{text}\n"
                    if order.status == 1:  # Add Cancel button only for pending orders
                        buttons.append([InlineKeyboardButton(
                            f"Bekor qilish #{order.id}" if lang_id == 1 else "Отменить",
                            callback_data=f"cancelorder_{order.id}"
                        )])
                await query.message.reply_text(response_text, parse_mode='HTML',
                                               reply_markup=InlineKeyboardMarkup(buttons))
            else:
                await query.message.reply_text(NO_ORDER_IN_STATUS[lang_id])
            context.user_data['state'] = 'main_menu'
            await send_main_menu(query, context, user)

        elif data[0] == "cancelorder":
            order_id = int(data[1])
            order = await cancel_order(order_id)
            cancel_text = "Buyurtma bekor qilindi!" if lang_id == 1 else "Заказ отменен!"
            await query.message.reply_text(cancel_text)
            context.user_data['state'] = 'main_menu'
            await send_main_menu(query, context, user)

    except BadRequest as e:
        if "message is not modified" in str(e).lower():
            logger.info("Message not modified, skipping edit.")
        else:
            logger.error(f"BadRequest in callback_handler: {e}")
            await query.message.reply_text("An error occurred. Please try again.")
    except Exception as e:
        logger.error(f"Error in callback_handler: {e}")
        await query.message.reply_text("An error occurred. Please try again.")