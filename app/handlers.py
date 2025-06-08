from aiogram import F, Router, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    BufferedInputFile,
    ReplyKeyboardRemove,
)
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.database.models import User, async_session
from app.support import is_user_logged_in


import app.keyboards as kb
import app.database.requests as rq

import asyncio

router = Router()

# Стейты
class CreateProject(StatesGroup):
    project_name = State()
    description = State()

class MyProjects(StatesGroup):
    id_project = State()

class SendInvUsername(StatesGroup):
    write_username = State()

class SendInvTgId(StatesGroup):
    write_tgid = State()

# Старт
@router.message(CommandStart())
async def upload_photo(message: Message):
    cheked_user_status = await is_user_logged_in(message.from_user.id)
    if cheked_user_status:
        return await message.answer(
            f"Приветствую, {message.from_user.username}",
            reply_markup=kb.mainMenuKeyBoard,
        )
    else:
        with open("./assets/images/logo.jfif", "rb") as image_from_buffer:
            await message.answer_photo(
                BufferedInputFile(image_from_buffer.read(), filename="logo.jfif"),
                caption="Добро пожаловать в wtdBot!\nС помощью данного бота вы сможете организовывать свои проекты, "
                "а также принимать участие в других проектах и регулировать назначеные на вас задачи. Для начала необходимо войти или зарегистрироваться!",
                reply_markup=kb.registrationKeyBoard,
            )


# Информация о себе

@router.message(F.text == "Посмотреть информацию о себе!")
async def show_me_info(message: Message):
    user_tg_id = message.from_user.id
    user_name = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    cheked_user_status = await is_user_logged_in(user_tg_id)
    if cheked_user_status:
        return await message.answer(
            f"Ваши данные:\nTelegram ID: {user_tg_id}\nUsername: @{user_name}\nИмя: {first_name}\nФамилия: {last_name}"
        )
    else:
        return await message.answer(
            "Вы не вошли в свой аккаунт, чтобы посмотреть информацию о себе:) Зайди в аккаунт и узнаешь нечто большее о себе! /start"
        )

# Выход из аккаунта

@router.message(F.text == "Выйти из аккаунта wtdbot")
async def exit_app(message: Message):
    user_tg_id = message.from_user.id
    cheked_user_status = await is_user_logged_in(user_tg_id)
    if cheked_user_status:
        await rq.change_user_logged(user_tg_id)
        await message.answer(
            f"Досвидания {message.from_user.username}, возвращайтесь за новыми задачами!\nЧтобы заного войти в аккаунт напишите /start",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            "Вы не вошли в свой аккаунт, чтобы из него выходить:) Ну хитрец!"
        )

# Вход в аккаунт

@router.callback_query(F.data == "sign-in")
async def sign_in(callback: CallbackQuery):
    user_tg_id = callback.from_user.id
    checked_user_logged = await rq.get_user_logged(user_tg_id)
    checked_user = await rq.get_user(user_tg_id)
    if checked_user != None:
        if checked_user_logged == 0:
            await rq.change_user_logged(user_tg_id)
            return await callback.message.answer(
                "Вы успешно вошли в аккаунт!", reply_markup=kb.mainMenuKeyBoard
            )
        else:
            return await callback.message.answer(
                "Вы уже войдены в аккаунт! Воспользуйтесь клавиатурой для манипуляций!",
                reply_markup=kb.mainMenuKeyBoard,
            )
    else:
        return callback.message.answer(
            "У вас не существует аккаунта в wtdbot, зарегистрируйтесь!",
            reply_markup=kb.registrationKeyBoard,
        )

# Регистрация

@router.callback_query(F.data == "sign-up")
async def sign_up(callback: CallbackQuery):
    await callback.message.answer(
        "Вы готовы предоставить нам следущие данные?: \n"
        "Telegram id\nИмя пользователя (username)\nИмя\nФамилия",
        reply_markup=kb.registrationAccessKeyBoard,
    )

# В случае подтверждения регистрации

@router.callback_query(F.data == "access")
async def register_access(callback: CallbackQuery):
    user_tg_id = callback.from_user.id
    username = callback.from_user.username
    first_name = callback.from_user.first_name
    last_name = callback.from_user.last_name
    check_register = await rq.get_user(user_tg_id)
    if check_register != None:
        await rq.change_user_logged(user_tg_id)
        return await callback.message.answer(
            "Вы уже зарегистрированы", reply_markup=kb.mainMenuKeyBoard
        )
    else:
        async with async_session() as session:
            new_user = User(
                tg_id=user_tg_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                role=1,
                user_logged=1,
            )
            session.add(new_user)
            await session.commit()
    return await callback.message.answer(
        "Регистрация успешна! Теперь можете пользоваться ботом. Вам доступна новая раскладка клавиатуры в правом нижнем углу поля ввода сообщения!", reply_markup=kb.mainMenuKeyBoard
    )

# В случае отказа от регистрации

@router.callback_query(F.data == "not-access")
async def register_notaccess(callback: CallbackQuery):
    return await callback.message.answer(
        "Очень жаль, ждем вашего возвращения!", reply_markup=kb.registrationKeyBoard
    )

# FAQ по использованию

@router.message(F.text == "FAQ по использованию")
async def show_me_faq(message: Message):
    user_tg_id = message.from_user.id
    if await rq.get_user_logged(user_tg_id):
        return await message.answer(
            "Здесь описан функционал бота. Какая кнопка за что отвечает:\n"
            '\nКнопка "Создать проект" - запускает функцию регистрации нового проекта.\n'
            '\nКнопка "Проверить приглашения в проекты" - просмотр приглашений в проекты.\n'
            '\nКнопка "Мои проекты" - возможность просмотреть список проектов, в которых вы принимаете участие.\n'
            '\nКнопка "Посмотреть информацию о себе!" - посмотреть основные регистрационные данные.\n'
            '\nКнопка "Выйти из аккаунта wtdbot" - выход из аккаунта, функции бота будут не доступны.\n'
            '\nКнопка "FAQ по использованию" - то что вы сейчас читаете:)'
        )
    else:
        return await message.answer(
            "Как вы догадались, что такая команда есть:) В прочем не важно, на данный момент вам доступна лишь команда /start"
        )

# Мои проекты

@router.message(F.text == "Мои проекты")
async def show_me_myprojects(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    checked_user_logged = await rq.get_user_logged(user_tg_id)
    if checked_user_logged:
        id_user_table = await rq.get_user_id_table(user_tg_id)
        list_reg_in_projects = await rq.get_myreg_in_projects(id_user_table)
        if len(list_reg_in_projects) > 0:
            project_list = await rq.get_projects_list(list_reg_in_projects)
            if project_list:
                output_string = ""
                for project_id, project_name in project_list.items():
                    output_string += f"{project_id} - {project_name}\n"
                await state.set_state(MyProjects.id_project)
                await message.answer(
                    f"{output_string}\n"
                    "Напишите ID проекта(цифра перед названием проекта), чтобы взаимодействовать с ним!",
                    reply_markup=ReplyKeyboardRemove()
                )
            else:
                await state.clear()
                return await message.answer("Упс!:( Что-то пошло не так!")
        else:
            await state.clear()
            return await message.answer("У вас нет проектов:(")
    else:
        await state.clear()
        return await message.answer(
            "Вы не вошли в аккаунт, чтобы просмотреть свои проекты!:)"
        )

@router.message(MyProjects.id_project)
async def check_loading_projectmenu(message: Message, state: FSMContext):
    await state.update_data(id_project=message.text)
    user_tg_id = message.from_user.id
    data = await state.get_data()
    id_project = data["id_project"]
    user_table_id = await rq.get_user_id_table(user_tg_id)
    if await rq.checking_user_in_project(user_table_id, id_project):
        role = await rq.check_roleuser_in_project(user_table_id, id_project)
        if await rq.get_writing_active_project(user_table_id):
            await rq.writing_to_activites_projects(user_table_id, id_project)

            if role == 2 or role == 3:
                if role == 2:
                    await state.clear()
                    return await message.answer("Вы успешно вошли в проект как \"Администратор проекта\"", reply_markup=kb.adminProjectsPanel)
                else:
                    await state.clear()
                    return await message.answer("Вы успешно вошли в проект как \"Модератор проекта\"", reply_markup=kb.moderatorProjectsPanel)
            else:
                await state.clear()
                return await message.answer("Вы успешно вошли в проект как \"Участник проекта\"", reply_markup=kb.userProjectsPanel)
        else:
            if role == 2 or role == 3:
                if role == 2:
                    await state.clear()
                    return await message.answer("Вы уже вошли в проект, откройте клавиатуру", reply_markup=kb.adminProjectsPanel)
                else:
                    await state.clear()
                    return await message.answer("Вы уже вошли в проект, откройте клавиатуру", reply_markup=kb.moderatorProjectsPanel)
            else:
                await state.clear()
                return await message.answer("Вы уже вошли в проект, откройте клавиатуру", reply_markup=kb.userProjectsPanel)
    else:
        await state.clear()
        return await message.answer("Вы не состоите в данном проекте!", reply_markup=kb.mainMenuKeyBoard)


@router.message(F.text == "В главное меню")
async def back_to_mainmenu(message: Message):
    user_tg_id = message.from_user.id
    checked_user_logged = await rq.get_user_logged(user_tg_id)
    user_table_id = await rq.get_user_id_table(user_tg_id)
    write = await rq.get_true_writing_active_project(user_table_id)
    if checked_user_logged:
        if write:
            del_row = await rq.del_activites_project(user_table_id)
            if del_row == 1:
                return await message.answer("Вы успешно вышли из меню проекта", reply_markup=kb.mainMenuKeyBoard)
            write = await rq.get_true_writing_active_project(user_table_id)
            if write:
                return await message.answer("Не известная ошибка выхода из меню проекта")
            else:
                return await message.answer("Хорошо, вы успешно вышли из меню проекта!", reply_markup=kb.mainMenuKeyBoard)
        else:
            return await message.answer("Вы и так не в меню проекта!", reply_markup=kb.mainMenuKeyBoard)
       
@router.message(F.text == "Отправить приглашение на вступление")
async def admin_send_invite_menu(message: Message):
    user_tg_id = message.from_user.id
    checked_user_logged = await rq.get_user_logged(user_tg_id)
    user_table_id = await rq.get_user_id_table(user_tg_id)
    project_id = await rq.get_active_id_project_foruser(user_table_id)
    check_role_in_project = await rq.check_roleuser_in_project(user_table_id, project_id)
    write = await rq.get_true_writing_active_project(user_table_id)
    if checked_user_logged:
        if write:
            if check_role_in_project == 2:
                return await message.answer("Выберите вариант того, как вы хотите отправить приглашение пользователю!", reply_markup=kb.keybordSendInvite)
            if check_role_in_project == 1:
                return await message.answer("Вы не администратор проекта!", reply_markup=kb.userProjectsPanel)
            if check_role_in_project == 3:
                return await message.answer("Вы не администратор проекта!", reply_markup=kb.moderatorProjectsPanel)
            return await message.answer("Вы кто?", reply_markup=kb.mainMenuKeyBoard)
        else:
            return await message.answer("Вы не зашли в меню проекта!", reply_markup=kb.mainMenuKeyBoard)


@router.callback_query(F.data == "send_to_tgid")
async def send_tgid(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SendInvTgId.write_tgid)
    await callback.message.answer("Введите телеграмм id", reply_markup=ReplyKeyboardRemove())

@router.message(SendInvTgId.write_tgid)
async def process_sendinvite_tgid(message: Message, state: FSMContext):
    await state.update_data(user_tg_id=message.text)
    admin_tg_id = message.from_user.id
    data = await state.get_data()
    user_tg_id = data["user_tg_id"]
    user_id = await rq.get_userid_for_tgid(user_tg_id)
    if user_id != False:
        sender_id = await rq.get_user_id_table(admin_tg_id)
        project_id = await rq.get_active_id_project_foruser(sender_id)
        if sender_id != user_id:
            invite = await rq.check_invite_in_project(user_id, project_id)
            if invite == False:
                try:
                    await rq.post_invitation(sender_id, project_id, user_id)
                    await state.clear()
                    return message.answer("Пользователю успешно отправлено приглашение!", reply_markup=kb.adminProjectsPanel)
                except Exception as e:
                    await state.clear()
                    return await message.answer(f"Произошла ошибка при отправке приглашения: {e}", reply_markup=kb.adminProjectsPanel)
            await state.clear()
            return await message.answer(f"Данному пользователю уже отправленно приглашение на данный проект!", reply_markup=kb.adminProjectsPanel)
        await state.clear()
        return await message.answer(f"Вы не можете отправить приглашение самому себе!", reply_markup=kb.adminProjectsPanel)
    await state.clear()
    return message.answer("Такого пользователя нет!", reply_markup=kb.adminProjectsPanel)


@router.callback_query(F.data == "send_to_username")
async def send_username(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SendInvUsername.write_username)
    await callback.message.answer("Введите username пользователя без @", reply_markup=ReplyKeyboardRemove())

@router.message(SendInvUsername.write_username)
async def process_sendinvite_username(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    await state.update_data(username=message.text)
    data = await state.get_data()
    username = data["username"]
    user_id = await rq.get_userid_for_username(username)
    if user_id != False:
        sender_id = await rq.get_user_id_table(user_tg_id)
        project_id = await rq.get_active_id_project_foruser(sender_id)
        if sender_id != user_id:
            invite = await rq.check_invite_in_project(user_id, project_id)
            if invite == False:
                try:
                    await rq.post_invitation(sender_id, project_id, user_id)
                    await state.clear()
                    return message.answer("Пользователю успешно отправлено приглашение!", reply_markup=kb.adminProjectsPanel)
                except Exception as e:
                    await state.clear()
                    return await message.answer(f"Произошла ошибка при отправке приглашения: {e}", reply_markup=kb.adminProjectsPanel)
            await state.clear()
            return await message.answer(f"Данному пользователю уже отправленно приглашение на данный проект!", reply_markup=kb.adminProjectsPanel)
        await state.clear()
        return await message.answer(f"Вы не можете отправить приглашение самому себе!", reply_markup=kb.adminProjectsPanel)
    await state.clear()
    return message.answer("Такого пользователя нет!", reply_markup=kb.adminProjectsPanel)


# Создание проекта

@router.message(F.text == "Создать проект")
async def create_project(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    checked_user_logged = await rq.get_user_logged(user_tg_id)
    if checked_user_logged:
        await state.set_state(CreateProject.project_name)
        await message.answer("Пожалуйста, введите название проекта: ", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer("Вы не вошли в свой аккаунт!")
        return await state.clear()


@router.message(CreateProject.project_name)
async def process_project_name(message: Message, state: FSMContext):
    await state.update_data(project_name=message.text)
    await state.set_state(CreateProject.description)
    await message.answer("Отлично! Теперь введите описание проекта:")

@router.message(CreateProject.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    user_tg_id = message.from_user.id
    user_id = await rq.get_user_id_table(user_tg_id)
    project_name = data["project_name"]
    description = data["description"]

    if len(project_name) < 5:
        await message.answer("Название не должно быть меньше 5 символов! Напишите еще раз \"Создать проект\"")
        return await state.clear()
    if len(description) == 0:
        description = "Описания пока что нет!"
    if len(description) > 1000:
        await message.answer(f"Описание не должно превышать 1000 символов, сейчас символов: {len(description)}. Напишите еще раз \"Создать проект\"")
        return await state.clear()
    try:
        await rq.create_new_project(project_name, description, user_id)
        await message.answer("Проект успешно создан!", reply_markup=kb.mainMenuKeyBoard)
    except Exception as e:
        return await message.answer(f"Произошла ошибка при создании проекта: {e}", reply_markup=kb.mainMenuKeyBoard)
    finally:
        return await state.clear()
