# bot/handlers/keyboard_handlers.py
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import ContextTypes
from django.contrib.auth import get_user_model
from ..globals import *

CustomUser = get_user_model()

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

def get_language_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(BTN_LANG_UZ), KeyboardButton(BTN_LANG_RU)]],
        resize_keyboard=True, one_time_keyboard=True
    )

def get_contact_keyboard(lang_id: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(BTN_SEND_CONTACT[lang_id], request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )

def get_category_keyboard(categories, lang_id: int) -> InlineKeyboardMarkup:
    buttons = []
    # Pair categories in rows of two
    for i in range(0, len(categories), 2):
        row = [InlineKeyboardButton(categories[i].name_uz if lang_id == 1 else categories[i].name_ru, callback_data=f"category_{categories[i].id}")]
        if i + 1 < len(categories):  # Add second button if available
            row.append(InlineKeyboardButton(categories[i + 1].name_uz if lang_id == 1 else categories[i + 1].name_ru, callback_data=f"category_{categories[i + 1].id}"))
        buttons.append(row)
    # Add "Back" button in its own row
    back_text = "Orqaga" if lang_id == 1 else "Назад"
    buttons.append([InlineKeyboardButton(back_text, callback_data="mainmenu")])
    return InlineKeyboardMarkup(buttons)

def get_product_keyboard(products, lang_id: int, category_id: int) -> InlineKeyboardMarkup:
    buttons = []
    # Pair products in rows of two
    for i in range(0, len(products), 2):
        row = [InlineKeyboardButton(products[i].name_uz if lang_id == 1 else products[i].name_ru, callback_data=f"product_{products[i].id}")]
        if i + 1 < len(products):  # Add second button if available
            row.append(InlineKeyboardButton(products[i + 1].name_uz if lang_id == 1 else products[i + 1].name_ru, callback_data=f"product_{products[i + 1].id}"))
        buttons.append(row)
    # Add "Back" button in its own row
    back_text = "Orqaga" if lang_id == 1 else "Назад"
    buttons.append([InlineKeyboardButton(back_text, callback_data="backtocategories")])
    return InlineKeyboardMarkup(buttons)

def get_quantity_keyboard(product_id: int, quantity: int, lang_id: int) -> InlineKeyboardMarkup:
    add_to_cart_text = "Savatchaga qo'shish" if lang_id == 1 else "Добавить в корзину"
    back_text = "Orqaga" if lang_id == 1 else "Назад"
    if quantity < 1:
        quantity = 1
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("−", callback_data=f"decrease_{product_id}"),
         InlineKeyboardButton(str(quantity), callback_data="noop"),
         InlineKeyboardButton("+", callback_data=f"increase_{product_id}")],
        [InlineKeyboardButton(add_to_cart_text, callback_data=f"addtocart_{product_id}"),
         InlineKeyboardButton(back_text, callback_data=f"back_{product_id}")]
    ])

def get_location_keyboard(lang_id: int) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(SEND_LOCATION[lang_id], request_location=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )