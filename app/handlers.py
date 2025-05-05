from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.database.models import User, async_session

import app.keyboards as kb
import app.database.requests as rq

router = Router()

# class Access(StatesGroup):
#     access = State()


@router.message(CommandStart())
async def upload_photo(message: Message):
    with open("./assets/images/logo.jfif", "rb") as image_from_buffer:
        await message.answer_photo(
            BufferedInputFile(image_from_buffer.read(), filename="logo.jfif"),
            caption="Добро пожаловать в wtdBot!\nС помощью данного бота вы сможете организовывать свои проекты, "
            "а также принимать участие в других проектах и регулировать назначеные на вас задачи. Для начала необходимо войти или зарегистрироваться!",
            reply_markup=kb.registrationKeyBoard,
        )


@router.message(Command("my_info"))
async def user(message: Message):
    user_tg_id = message.from_user.id
    data_user = await rq.get_user(user_tg_id)
    if data_user != None:
        user_info_text = (
            f"Информация о вас:\n"
            f"Telegram ID: {data_user.tg_id}\n"
            f"Username: {data_user.username}\n"
            f"Имя: {data_user.first_name}\n"
            f"Фамилия: {data_user.last_name}\n"
        )
        await message.answer(user_info_text)
    else:
        await message.reply(
            "Вы еще не зарегистрировались, введите /start и нажмите зарегистрироваться"
        )


# @router.message(F.text == 'Каталог')
# async def catalog(message: Message):
#     await message.answer('Выберите категорию товара', reply_markup=await kb.categories())

# @router.callback_query(F.data.startswith('category_'))
# async def category(callback: CallbackQuery):
#     await callback.answer('Вы выбрали категорию')
#     await callback.message.answer('Выберите товар по категории',
#                                   reply_markup=await kb.items(callback.data.split('_')[1]))

# @router.callback_query(F.data.startswith('item_'))
# async def category(callback: CallbackQuery):
#     item_data = await rq.get_item(callback.data.split('_')[1])
#     await callback.answer('Вы выбрали товар')
#     await callback.message.answer(f'Название: {item_data.name}\nОписание: {item_data.description}\nЦена: {item_data.price} долларов',
#                                   reply_markup=await kb.items(callback.data.split('_')[1]))


# @router.message(Command("help"))
# async def cmd_help(message: Message):
#     await message.answer("Вы нажали help")

# @router.message(F.text == 'Каталог')
# async def catalog(message: Message):
#     await message.answer('Выберите категорию товара', reply_markup=kb.catalog)


# @router.callback_query(F.data == "t-shirt")
# async def t_shirt(callback: CallbackQuery):
#     await callback.answer('Вы выбрали категорию')
#     await callback.message.answer('Вы выбрали категорию футболок')
@router.callback_query(F.data == "sign-up")
async def sign_up(callback: CallbackQuery):
    await callback.answer(
        "Вы готовы предоставить нам следущие данные?: \n"
        "Telegram id\nusername\nИмя\nФамилия",
    )
    await callback.message.answer(
        "Вы готовы предоставить нам следущие данные?: \n"
        "Telegram id\nusername\nИмя\nФамилия",
        reply_markup=kb.registrationAccessKeyBoard,
    )


@router.callback_query(F.data == "access")
async def register_access(callback: CallbackQuery):
    user_tg_id = callback.from_user.id
    username = callback.from_user.username
    first_name = callback.from_user.first_name
    last_name = callback.from_user.last_name
    check_register = await rq.get_user(user_tg_id)
    if check_register != None:
        await callback.answer("Вы уже зарегистрированы")
        return
    else:
        async with async_session() as session:
            new_user = User(
                tg_id=user_tg_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                role=1,
            )
            session.add(new_user)
            await session.commit()

    await callback.answer("Регистрация успешна!")


# @router.message(Command('register'))
# async def register(message: Message, state: FSMContext):
#     await state.set_state(Register.name)
#     await message.answer('Введите ваше имя')

# @router.message(Register.name)
# async def regiser_name(message: Message, state: FSMContext):
#     await state.update_data(name=message.text)
#     await state.set_state(Register.age)
#     await message.answer('Введите ваш возраст')

# @router.message(Register.age)
# async def regiser_age(message: Message, state: FSMContext):
#     await state.update_data(age=message.text)
#     await state.set_state(Register.number)
#     await message.answer('Отправьте ваш номер телефона', reply_markup=kb.get_number)

# @router.message(Register.number, F.contact)
# async def register_number(message: Message, state: FSMContext):
#     await state.update_data(number=message.contact.phone_number)
#     data = await state.get_data()
#     await message.answer(f'Ваше имя: {data["name"]}\nВаш возраст: {data['age']}\nВаш номер: {data["number"]}')
#     await state.clear()
