from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# from app.database.requests import
from aiogram.utils.keyboard import InlineKeyboardBuilder


registrationKeyBoard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Войти", callback_data="sign-in")],
        [InlineKeyboardButton(text="Зарегистрироваться", callback_data="sign-up")],
    ]
)

registrationAccessKeyBoard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Согласен", callback_data="access")],
        [InlineKeyboardButton(text="Не согласен", callback_data="not-access")],
    ]
)


# main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='')],
#                                      [KeyboardButton(text='Корзина')],
#                                      [KeyboardButton(text='Контакты'),
#                                      KeyboardButton(text='О нас')]],
#                                      resize_keyboard=True,
#                                      input_field_placeholder='Выберите пункт меню')

# catalog = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text='Футболки', callback_data='t-shirt')],
#     [InlineKeyboardButton(text='Кросовки', callback_data='sneakers')],
#     [InlineKeyboardButton(text='Кепки', callback_data='cap')]
# ])

# get_number = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить номер', request_contact=True)]],
#                                  resize_keyboard=True)

# async def categories():
#     all_categories = await get_categories()
#     keyboard = InlineKeyboardBuilder()
#     for category in all_categories:
#         keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f"category_{category.id}"))
#     keyboard.add(InlineKeyboardButton(text = "На главную", callback_data='to_main'))
#     return keyboard.adjust(2).as_markup()

# async def items(category_id):
#     all_items = await get_category_item(category_id)
#     keyboard = InlineKeyboardBuilder()
#     for item in all_items:
#         keyboard.add(InlineKeyboardButton(text=item.name, callback_data=f"item_{item.id}"))
#     keyboard.add(InlineKeyboardButton(text = "На главную", callback_data='to_main'))
#     return keyboard.adjust(2).as_markup()
