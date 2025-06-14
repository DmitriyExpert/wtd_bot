from datetime import datetime
from aiogram import F, Router
from aiogram.types import (
    Message,
    CallbackQuery,
    BufferedInputFile,
    ReplyKeyboardRemove,
)
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.database.models import ProjectsUsers, User, Ban, async_session

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.database.models import User, async_session
from app.support import is_user_logged_in
from sqlalchemy import or_, select, update, delete
from sqlalchemy.orm import selectinload

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

class AccessRejectInvite(StatesGroup):
    access_inv = State()
    reject_inv = State()

class ApplyProjectID(StatesGroup):
    write_project_id = State()

class ApplyProjectUsername(StatesGroup):
    write_admin_username = State()
    select_project_id = State()

class ReviewApplication(StatesGroup):
    write_user_id = State()

class TaskManagement(StatesGroup):
    select_action = State()
    create_task_name = State()
    create_task_description = State()
    create_task_assignee = State()
    create_task_deadline = State()
    create_task_priority = State()
    edit_task_id = State()
    edit_task_name = State()
    edit_task_description = State()
    edit_task_assignee = State()
    edit_task_deadline = State()
    edit_task_priority = State()
    edit_task_status = State()
    take_task = State()
    delete_task_id = State()
    select_task = State()  
    select_user_for_assign = State()
    select_status = State()
    manage_comments = State()  # Выбор задачи для управления комментариями
    view_comments = State()  # Просмотр комментариев к задаче
    add_comment = State()  # Добавление комментария
    add_comment_process = State()
    edit_comment = State()  # Редактирование комментария
    delete_comment = State() # Удаление комментария
    select_comment = State() # Выбор комментария
    select_action = State()

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

# Проверка приглашений

@router.message(F.text == "Проверить приглашения в проекты")
async def show_me_inviteme(message: Message):
    user_tg_id = message.from_user.id
    if await rq.get_user_logged(user_tg_id):
        user_table_id = await rq.get_user_id_table(user_tg_id)
        invites = await rq.get_invitations_for_user(user_table_id)
        if invites:
            response_text = "Ваши приглашения:\n"
            for invite in invites:
                if invite.invitation_status not in [2, 3]:
                    project_name = invite.project.project_name
                    admin_username = invite.sender.username
                    response_text += f"ID проекта: {invite.project_id}, Название проекта: {project_name},  Админ: @{admin_username}\n"
            if response_text == "Ваши приглашения:\n":
                await message.answer("У вас нет активных приглашений.")
            else:
                await message.answer(response_text, reply_markup=kb.keyboardAccessInvite)
        else:
            await message.answer("У вас нет приглашений.")
    else:
        await message.answer(
            "Вы не вошли в свой аккаунт, чтобы просмотреть свои приглашения!:)"
        )

@router.callback_query(F.data == "access_invite")
async def access_inv(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AccessRejectInvite.access_inv)
    await callback.message.answer("Введите id проекта из списка!", reply_markup=ReplyKeyboardRemove())

@router.message(AccessRejectInvite.access_inv)
async def process_access_inv(message: Message, state: FSMContext):
    await state.update_data(id_project=message.text)
    data = await state.get_data()
    id_project = data["id_project"]
    user_tg_id = message.from_user.id
    checked_user_logged = await rq.get_user_logged(user_tg_id)
    if checked_user_logged:
        user_table_id = await rq.get_user_id_table(user_tg_id)
        check_change = await rq.change_inviteid_for_access(user_table_id, id_project)
        if check_change == True:
            await rq.post_new_project_user_invite(user_table_id, id_project)
            await state.clear()
            return await message.answer(f"Вы успешно добавлены в проект! Мои проекты -> Проект: {id_project} id", reply_markup=kb.mainMenuKeyBoard)
        if check_change == None:
            await state.clear()
            return await message.answer("Вы уже в проекте или вы отменили заявку на вступление в данный проект!", reply_markup=kb.mainMenuKeyBoard)
        await state.clear()
        return await message.answer("Вы не приглашены в данный проект!", reply_markup=kb.mainMenuKeyBoard)
    await state.clear()

# Обработка отклонения приглашения
@router.callback_query(F.data == "reject_invite")
async def reject_inv(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AccessRejectInvite.reject_inv)
    await callback.message.answer("Введите id проекта из списка!", reply_markup=ReplyKeyboardRemove())

@router.message(AccessRejectInvite.reject_inv)
async def process_reject_inv(message: Message, state: FSMContext):
    await state.update_data(id_project=message.text)
    data = await state.get_data()
    id_project = data["id_project"]
    user_tg_id = message.from_user.id
    checked_user_logged = await rq.get_user_logged(user_tg_id)
    if checked_user_logged:
        user_table_id = await rq.get_user_id_table(user_tg_id)
        check_change = await rq.change_inviteid_for_reject(user_table_id, id_project)
        if check_change == True:
            await state.clear()
            return await message.answer(f"Вы успешно отклонили приглашение в проект c id {id_project}!", reply_markup=kb.mainMenuKeyBoard)
        if check_change == None:
            await state.clear()
            return await message.answer("Вы уже в проекте или вы приняли заявку на вступление в данный проект!", reply_markup=kb.mainMenuKeyBoard)
        await state.clear()
        return await message.answer("Вы не приглашены в данный проект!", reply_markup=kb.mainMenuKeyBoard)
    await state.clear()

@router.message(F.text == "Отправить заявку на вступление в проект")
async def apply_project_menu(message: Message):
    user_tg_id = message.from_user.id
    checked_user_logged = await rq.get_user_logged(user_tg_id)
    if checked_user_logged:
        await message.answer("Выберите, как вы хотите найти проект:", reply_markup=kb.keybordApplyInvite)
    else:
        await message.answer("Вы не вошли в свой аккаунт!")

@router.callback_query(F.data == "apply_by_id")
async def apply_project_id(callback: CallbackQuery, state: FSMContext):
    user_tg_id = callback.from_user.id
    user_id = await rq.get_user_id_table(user_tg_id)
    await state.set_state(ApplyProjectID.write_project_id)
    await state.update_data(user_id=user_id)  #  Сохраняем user_id
    await callback.message.answer("Введите уникальный ID проекта:", reply_markup=ReplyKeyboardRemove())

@router.message(ApplyProjectID.write_project_id)
async def process_apply_project_id(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]
    project_id = message.text

    project = await rq.get_project(project_id)
    if project:
        # Проверяем, что пользователь не является администратором проекта
        if project.admin_id == user_id:
            await state.clear()
            return await message.answer("Вы администратор этого проекта и не можете подавать заявку!", reply_markup=kb.mainMenuKeyBoard)
        
        # Проверяем наличие заявки со статусом "Rejected"
        rejected_application = await rq.check_rejected_application_exists(user_id, project_id)

        if rejected_application:
            await state.clear()
            admin = await rq.get_admin_by_project(project_id)
            admin_username = admin.username if admin and admin.username else "неизвестен"
            return await message.answer(f"Ваша заявка была отклонена! Попробуйте позже или свяжитесь с администрацией проекта: @{admin_username}", reply_markup=kb.mainMenuKeyBoard)

        if not await rq.check_application_exists(user_id, project_id):
            await rq.post_project_application(user_id, project_id)
            await state.clear()
            return await message.answer("Заявка на вступление в проект отправлена!", reply_markup=kb.mainMenuKeyBoard)
        else:
            await state.clear()
            return await message.answer("Вы уже подали заявку на этот проект!", reply_markup=kb.mainMenuKeyBoard)
    else:
        await state.clear()
        return await message.answer("Проекта с таким ID не существует!", reply_markup=kb.mainMenuKeyBoard)

@router.callback_query(F.data == "apply_by_admin")
async def apply_project_admin(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ApplyProjectUsername.write_admin_username)
    await callback.message.answer("Введите username админа:", reply_markup=ReplyKeyboardRemove())

@router.message(ApplyProjectUsername.write_admin_username)
async def process_apply_project_username(message: Message, state: FSMContext):
    await state.update_data(admin_username=message.text)
    data = await state.get_data()
    admin_username = data["admin_username"]
    admin_id = await rq.get_userid_for_username(admin_username)

    if admin_id:
        projects = await rq.get_projects_by_admin(admin_id)
        if projects:
            project_list = ""
            for project in projects:
                project_list += f"{project.id} - {project.project_name}\n"
            await state.set_state(ApplyProjectUsername.select_project_id)
            await state.update_data(projects=projects)
            await message.answer(f"Проекты админа {admin_username}:\n{project_list}\nВведите ID проекта:", reply_markup=ReplyKeyboardRemove())
        else:
            await state.clear()
            return await message.answer("У этого админа нет проектов!", reply_markup=kb.mainMenuKeyBoard)
    else:
        await state.clear()
        return await message.answer("Админа с таким username не существует!", reply_markup=kb.mainMenuKeyBoard)

@router.message(ApplyProjectUsername.select_project_id)
async def process_apply_select_project(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user_id = await rq.get_user_id_table(user_tg_id)
    project_id = message.text
    data = await state.get_data()
    projects = data["projects"]

    if any(project.id == int(project_id) for project in projects):
         if not await rq.check_application_exists(user_id, project_id):
            await rq.post_project_application(user_id, project_id)
            await state.clear()
            return await message.answer("Заявка на вступление в проект отправлена!", reply_markup=kb.mainMenuKeyBoard)
         else:
            await state.clear()
            return await message.answer("Вы уже подали заявку на этот проект!", reply_markup=kb.mainMenuKeyBoard)
    else:
        await state.clear()
        return await message.answer("Неверный ID проекта!", reply_markup=kb.mainMenuKeyBoard)

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
                    output_string += f"id проекта {project_id} - {project_name}\n"
                await state.set_state(MyProjects.id_project)
                await message.answer(
                    f"{output_string}\n"
                    "Напишите ID проекта, чтобы взаимодействовать с ним!",
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
                    return await message.answer(f"Вы успешно вошли в проект как \"Администратор проекта\"", reply_markup=kb.adminProjectsPanel)
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


@router.message(F.text == "Проверить заявки на вступление")
async def review_project_applications(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user_table_id = await rq.get_user_id_table(user_tg_id)
    project_id = await rq.get_active_id_project_foruser(user_table_id)

    # Проверяем, что пользователь является админом или модератором проекта
    role = await rq.check_roleuser_in_project(user_table_id, project_id)
    if role == 2 or role == 3:
        applications = await rq.get_pending_applications(project_id)
        if applications:
            application_list = ""
            for app in applications:
                application_list += f"ID Пользователя: {app.user_id}, Username: @{app.user.username}\n"
            await state.set_state(ReviewApplication.write_user_id)
            await message.answer(f"Заявки на вступление:\n{application_list}\nВведите ID пользователя для принятия/отклонения:", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer("Нет ожидающих заявок на вступление.")
    else:
        await message.answer("У вас нет прав для просмотра заявок на вступление!")

@router.message(ReviewApplication.write_user_id)
async def process_review_application(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user_table_id = await rq.get_user_id_table(user_tg_id)
    project_id = await rq.get_active_id_project_foruser(user_table_id)
    target_user_id = message.text
    if not target_user_id.isdigit():
        await state.clear()
        return await message.answer("Неверный формат ID пользователя, должно быть число!", reply_markup=kb.adminProjectsPanel)
    
    try:
        if int(target_user_id) == user_table_id:
            role = await rq.check_roleuser_in_project(user_table_id, project_id)
            if role == 2:
                try:
                    await rq.delete__application(target_user_id, project_id)
                    await state.clear()    
                    return await message.answer("Вы не можете принять себя самого!", reply_markup=kb.adminProjectsPanel)
                except:
                    await state.clear()
                    return await message.answer("Неожиданная ошибка", reply_markup=kb.adminProjectsPanel)
            elif role == 3:
                try:
                    await rq.delete__application(target_user_id, project_id)
                    await state.clear()    
                    return await message.answer("Вы не можете принять себя самого!", reply_markup=kb.adminProjectsPanel)
                except:
                    await state.clear()
                    return await message.answer("Неожиданная ошибка", reply_markup=kb.adminProjectsPanel)
        int(target_user_id)
    except ValueError:
        await state.clear()
        return await message.answer("Неверный формат ID пользователя, должно быть число!", reply_markup=kb.adminProjectsPanel)

    await state.clear()
    await message.answer("Выберите действие:", reply_markup=kb.applicationActionsKeyBoard(target_user_id))

@router.callback_query(F.data.startswith("application_"))
async def process_application_action(callback: CallbackQuery):
    action, target_user_id = callback.data.split("_")[1], callback.data.split("_")[2]
    user_tg_id = callback.from_user.id
    user_table_id = await rq.get_user_id_table(user_tg_id)
    project_id = await rq.get_active_id_project_foruser(user_table_id)
    if action == "accept":
        check_change = await rq.accept_application(target_user_id, project_id)
        if check_change == True:
            await rq.post_new_project_user_invite(target_user_id, project_id)
            return await callback.message.answer(f"Вы приняли заявку от пользователя с ID {target_user_id}!", reply_markup=kb.adminProjectsPanel)
        else:
            return await callback.message.answer("Не получилось принять", reply_markup=kb.adminProjectsPanel)
    elif action == "reject":
        await rq.reject_application(target_user_id, project_id)
        return await callback.message.answer(f"Вы отклонили заявку от пользователя с ID {target_user_id}!", reply_markup=kb.adminProjectsPanel)
    else:
        return await callback.message.answer("Неверное действие!", reply_markup=kb.adminProjectsPanel)


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

async def format_task_list(tasks):
    task_list = ""
    task_priority = ""
    for task in tasks:
        user_info = ""
        if task.assignee:
            user_info = f" (Назначен: @{task.assignee.username})"
        if task.priority_id == 3:
            task_priority = "Высокий"
        elif task.priority_id == 2:
            task_priority = "Средний"
        else: 
            task_priority = "Низкий"
        task_list += f"ID: {task.id} - {task.task_name}{user_info}; Приоритет: {task_priority};\n"
    return task_list


@router.message(F.text == "Управление задачами")
async def task_management_menu(message: Message, state: FSMContext):
    user_tg_id = message.from_user.id
    user_table_id = await rq.get_user_id_table(user_tg_id)
    project_id = await rq.get_active_id_project_foruser(user_table_id)

    role = await rq.check_roleuser_in_project(user_table_id, project_id)
    if not role:
        return await message.answer("Вы не состоите в проекте!", reply_markup=kb.mainMenuKeyBoard)

    tasks_in_progress = await rq.get_tasks_by_status(project_id, 2)
    tasks_pending = await rq.get_tasks_by_status(project_id, 1)
    tasks_completed = await rq.get_tasks_by_status(project_id, 3)
    tasks_overdue = await rq.get_tasks_by_status(project_id, 4)

    response_text = "**Задачи в работе:**\n"
    response_text += await format_task_list(tasks_in_progress)
    response_text += "\n**Ожидают назначения:**\n"
    response_text += await format_task_list(tasks_pending)
    response_text += "\n**Выполнены:**\n"
    response_text += await format_task_list(tasks_completed)
    response_text += "\n**Просрочены:**\n"
    response_text += await format_task_list(tasks_overdue)

    await state.set_state(TaskManagement.select_action)
    await message.answer(response_text, reply_markup=kb.get_task_management_keyboard(role), parse_mode="Markdown")

# Создание задачи

@router.callback_query(F.data == "create_task", TaskManagement.select_action)
async def create_task(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TaskManagement.create_task_name)
    await callback.message.answer("Введите название задачи; Чтобы отменить создание задачи напишите \" Отмена создания задачи \"", reply_markup=ReplyKeyboardRemove())

@router.message(TaskManagement.create_task_name)
async def process_create_task_name(message: Message, state: FSMContext):
    await state.update_data(my_be_cancel=message.text)
    tg_id = message.from_user.id
    data = await state.get_data()
    message_text = data["my_be_cancel"]
    if message_text.lower() == "отмена создания задачи":
        await state.clear()
        user_table_id = await rq.get_user_id_table(tg_id)
        project_id = await rq.get_active_id_project_foruser(user_table_id)
        role_in_project = await rq.check_roleuser_in_project(user_table_id, project_id)
        if role_in_project == 2:
            return message.answer("Успешная отмена создания задачи!", reply_markup=kb.adminProjectsPanel)
        if role_in_project == 3:
            return message.answer("Успешная отмена создания задачи!", reply_markup=kb.moderatorProjectsPanel)
        return message.answer("Успешная отмена создания задачи!", reply_markup=kb.userProjectsPanel)
    await state.update_data(task_name=message.text)
    await state.set_state(TaskManagement.create_task_description)
    await message.answer("Введите описание задачи (или пропустите, нажав /skip):")

@router.message(TaskManagement.create_task_description, Command(commands="skip"))
async def skip_create_task_description(message: Message, state: FSMContext):
    await state.update_data(task_description=None)  # Пропускаем описание
    await state.set_state(TaskManagement.create_task_deadline)
    await message.answer("Укажите срок выполнения задачи в формате ГГГГ-ММ-ДД (или пропустите, нажав /skip):")

@router.message(TaskManagement.create_task_description)
async def process_create_task_description(message: Message, state: FSMContext):
    await state.update_data(task_description=message.text)
    await state.set_state(TaskManagement.create_task_deadline)
    await message.answer("Укажите срок выполнения задачи в формате ГГГГ-ММ-ДД (или пропустите, нажав /skip):")

@router.message(TaskManagement.create_task_deadline, Command(commands="skip"))
async def skip_create_task_deadline(message: Message, state: FSMContext):
    await state.update_data(task_deadline=None) # Пропускаем дедлайн
    await state.set_state(TaskManagement.create_task_priority)
    await message.answer("Укажите приоритет задачи (Низкий, Средний, Высокий):")

@router.message(TaskManagement.create_task_deadline)
async def process_create_task_deadline(message: Message, state: FSMContext):
    try:
        deadline = datetime.strptime(message.text, "%Y-%m-%d")
        await state.update_data(task_deadline=deadline)
        await state.set_state(TaskManagement.create_task_priority)
        await message.answer("Укажите приоритет задачи (Низкий, Средний, Высокий):")
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД (или пропустите, нажав /skip):")
        return  # Важно прервать обработку, чтобы не перейти к следующему шагу

@router.message(TaskManagement.create_task_priority)
async def process_create_task_priority(message: Message, state: FSMContext):
    priority = message.text.lower()
    if priority == "низкий":
        priority_id = 1
    elif priority == "средний":
        priority_id = 2
    elif priority == "высокий":
        priority_id = 3
    else:
        await message.answer("Неверный приоритет. Пожалуйста, укажите Низкий, Средний или Высокий:")
        return  # Важно прервать обработку

    await state.update_data(task_priority=priority_id)

    data = await state.get_data()
    user_tg_id = message.from_user.id
    user_table_id = await rq.get_user_id_table(user_tg_id)
    project_id = await rq.get_active_id_project_foruser(user_table_id)

    task_name = data["task_name"]
    task_description = data.get("task_description")
    task_deadline = data.get("task_deadline")
    task_priority = data["task_priority"]

    try:
        await rq.create_new_task(project_id, task_name, task_description, user_table_id, task_deadline, task_priority)
        await state.clear()
        await message.answer("Задача успешно создана!", reply_markup=kb.adminProjectsPanel)
    except Exception as e:
        await state.clear()
        await message.answer(f"Произошла ошибка при создании задачи: {e}", reply_markup=kb.adminProjectsPanel)

# Редактирование задачи

@router.callback_query(F.data == "edit_task", TaskManagement.select_action)
async def edit_task(callback: CallbackQuery, state: FSMContext):
    user_tg_id = callback.from_user.id
    user_table_id = await rq.get_user_id_table(user_tg_id)
    project_id = await rq.get_active_id_project_foruser(user_table_id)
    
    # Получаем список задач для проекта
    tasks = await rq.get_tasks_by_project(project_id)
    if not tasks:
        await callback.message.answer("В проекте нет задач для редактирования!", reply_markup=kb.adminProjectsPanel)
        return

    await state.set_state(TaskManagement.select_task)
    await callback.message.answer("Выберите задачу для редактирования:", reply_markup=kb.get_task_keyboard(tasks, "edit"))

@router.callback_query(F.data.startswith("select_task_edit_"), TaskManagement.select_task)
async def process_select_task_edit(callback: CallbackQuery, state: FSMContext):
    task_id = callback.data.split("_")[3]
    try:
        task_id_int = int(task_id)
    except ValueError:
        await callback.message.answer("Неверный ID задачи!", reply_markup=kb.adminProjectsPanel)
        await state.clear()
        return

    # Get the task with the assignee loaded
    task = await rq.get_task_by_id(task_id_int)
    if task is None:
        await callback.message.answer("Задача не найдена!", reply_markup=kb.adminProjectsPanel)
        await state.clear()
        return

    await state.update_data(edit_task_id=task_id_int)
    await state.set_state(TaskManagement.edit_task_name)
    await callback.message.answer(f"Редактирование задачи: {task.task_name}\nВведите новое название задачи (или пропустите, нажав /skip):", reply_markup=ReplyKeyboardRemove())

@router.message(TaskManagement.edit_task_name, Command(commands="skip"))
async def skip_edit_task_name(message: Message, state: FSMContext):
    await state.update_data(edit_task_name=None)
    await state.set_state(TaskManagement.edit_task_description)
    await message.answer("Введите новое описание задачи (или пропустите, нажав /skip):", reply_markup=ReplyKeyboardRemove())

@router.message(TaskManagement.edit_task_name)
async def process_edit_task_name(message: Message, state: FSMContext):
    await state.update_data(edit_task_name=message.text)
    await state.set_state(TaskManagement.edit_task_description)
    await message.answer("Введите новое описание задачи (или пропустите, нажав /skip):", reply_markup=ReplyKeyboardRemove())

@router.message(TaskManagement.edit_task_description, Command(commands="skip"))
async def skip_edit_task_description(message: Message, state: FSMContext):
    await state.update_data(edit_task_description=None)
    await state.set_state(TaskManagement.edit_task_deadline)
    await message.answer("Укажите новый срок выполнения задачи в формате ГГГГ-ММ-ДД (или пропустите, нажав /skip):", reply_markup=ReplyKeyboardRemove())

@router.message(TaskManagement.edit_task_description)
async def process_edit_task_description(message: Message, state: FSMContext):
    await state.update_data(edit_task_description=message.text)
    await state.set_state(TaskManagement.edit_task_deadline)
    await message.answer("Укажите новый срок выполнения задачи в формате ГГГГ-ММ-ДД (или пропустите, нажав /skip):", reply_markup=ReplyKeyboardRemove())

@router.message(TaskManagement.edit_task_deadline, Command(commands="skip"))
async def skip_edit_task_deadline(message: Message, state: FSMContext):
    await state.update_data(edit_task_deadline=None)
    await state.set_state(TaskManagement.edit_task_priority)
    await message.answer("Укажите новый приоритет задачи (Низкий, Средний, Высокий или пропустите, нажав /skip):", reply_markup=ReplyKeyboardRemove())

@router.message(TaskManagement.edit_task_deadline)
async def process_edit_task_deadline(message: Message, state: FSMContext):
    try:
        deadline = datetime.strptime(message.text, "%Y-%m-%d")
        await state.update_data(edit_task_deadline=deadline)
        await state.set_state(TaskManagement.edit_task_priority)
        await message.answer("Укажите новый приоритет задачи (Низкий, Средний, Высокий):", reply_markup=ReplyKeyboardRemove())
    except ValueError:
        await message.answer("Неверный формат даты. Пожалуйста, используйте формат ГГГГ-ММ-ДД (или пропустите, нажав /skip):", reply_markup=ReplyKeyboardRemove())
        return  # Важно прервать обработку, чтобы не перейти к следующему шагу

@router.message(TaskManagement.edit_task_priority, Command(commands="skip"))
async def skip_edit_task_priority(message: Message, state: FSMContext):
    await state.update_data(edit_task_priority=None)
    data = await state.get_data()
    task_id = data["edit_task_id"]
    task_name = data.get("edit_task_name")
    task_description = data.get("edit_task_description")
    task_deadline = data.get("edit_task_deadline")
    task_priority = data.get("edit_task_priority")
    await state.clear()
    try:
        await rq.update_task(task_id, task_name, task_description, task_deadline, task_priority)
        await message.answer("Задача успешно обновлена!", reply_markup=kb.adminProjectsPanel)
    except Exception as e:
        await message.answer(f"Произошла ошибка при обновлении задачи: {e}", reply_markup=kb.adminProjectsPanel)

@router.message(TaskManagement.edit_task_priority)
async def process_edit_task_priority(message: Message, state: FSMContext):
    priority = message.text.lower()
    if priority == "низкий":
        priority_id = 1
    elif priority == "средний":
        priority_id = 2
    elif priority == "высокий":
        priority_id = 3
    else:
        await message.answer("Неверный приоритет. Пожалуйста, укажите Низкий, Средний или Высокий:")
        return  # Важно прервать обработку
    await state.update_data(edit_task_priority=priority_id)

    data = await state.get_data()
    task_id = data["edit_task_id"]
    task_name = data.get("edit_task_name")
    task_description = data.get("edit_task_description")
    task_deadline = data.get("edit_task_deadline")
    task_priority = data["edit_task_priority"]

    try:
        await rq.update_task(task_id, task_name, task_description, task_deadline, task_priority)
        await state.clear()
        await message.answer("Задача успешно обновлена!", reply_markup=kb.adminProjectsPanel)
    except Exception as e:
        await state.clear()
        await message.answer(f"Произошла ошибка при обновлении задачи: {e}", reply_markup=kb.adminProjectsPanel)

# Удаление задачи

@router.callback_query(F.data == "delete_task", TaskManagement.select_action)
async def delete_task(callback: CallbackQuery, state: FSMContext):
    user_tg_id = callback.from_user.id
    user_table_id = await rq.get_user_id_table(user_tg_id)
    project_id = await rq.get_active_id_project_foruser(user_table_id)
    role = await rq.check_roleuser_in_project(user_table_id, project_id)
    
    await state.update_data(user_role=role) # Добавил сохранение роли

    # Проверяем права доступа
    if role in [2, 3]:  # Администратор или Модератор
        await state.set_state(TaskManagement.delete_task_id)
        await callback.message.answer("Введите ID задачи для удаления:", reply_markup=ReplyKeyboardRemove())
    else:
        await callback.message.answer("У вас нет прав для удаления задачи!", reply_markup=kb.adminProjectsPanel)


@router.message(TaskManagement.delete_task_id)
async def process_delete_task(message: Message, state: FSMContext):
    try:
        task_id = int(message.text)
    except ValueError:
        await message.answer("Неверный формат ID задачи! Введите целое число.")
        return

    data = await state.get_data()
    user_role = data["user_role"]
    user_tg_id = message.from_user.id
    user_table_id = await rq.get_user_id_table(user_tg_id)
    project_id = await rq.get_active_id_project_foruser(user_table_id)

    try:
        task = await rq.get_task_by_id(task_id)
        if not task:
            if user_role == 2:
                return await message.answer("Задача с таким ID не найдена.", reply_markup=kb.adminProjectsPanel)
            elif user_role == 3:
                return await message.answer("Задача с таким ID не найдена.", reply_markup=kb.moderatorProjectsPanel)
                

        if user_role == 2:  # Администратор: может удалять все задачи
            await rq.delete_task(task_id)
            await message.answer(f"Задача с ID {task_id} успешно удалена!", reply_markup=kb.adminProjectsPanel)
        elif user_role == 3:  # Модератор: может удалять только не созданные администратором задачи
            if task.creator_id == await rq.get_admin_id_for_project(project_id):
                await message.answer("Вы не можете удалять задачи, созданные администратором!")
            else:
                await rq.delete_task(task_id)
                await message.answer(f"Задача с ID {task_id} успешно удалена!", reply_markup=kb.adminProjectsPanel)
        else:
            await message.answer("У вас нет прав для удаления задачи!", reply_markup=kb.adminProjectsPanel)
    except Exception as e:
        await message.answer(f"Произошла ошибка при удалении задачи: {e}", reply_markup=kb.adminProjectsPanel)
    finally:
        await state.clear()

# Назначение задачи

@router.callback_query(F.data == "assign_task", TaskManagement.select_action)
async def assign_task(callback: CallbackQuery, state: FSMContext):
    user_tg_id = callback.from_user.id
    user_table_id = await rq.get_user_id_table(user_tg_id)
    project_id = await rq.get_active_id_project_foruser(user_table_id)
    role = await rq.check_roleuser_in_project(user_table_id, project_id)

    if role in [2, 3]:  # Admin или Moderator
        tasks = await rq.get_tasks_by_project(project_id)
        if not tasks:
            await callback.message.answer("В проекте нет задач для назначения!", reply_markup=kb.adminProjectsPanel)
            return

        await state.update_data(assign_role=role)
        await state.update_data(tasks_for_assign=tasks) # Save Tasks

        await state.set_state(TaskManagement.select_task)
        await callback.message.answer("Выберите задачу для назначения:", reply_markup=kb.get_tasks_keyboard(tasks, "assign"))  # "assign" tells which callback to use
    else:
        await callback.message.answer("У вас нет прав для назначения задач!", reply_markup=kb.adminProjectsPanel)

@router.callback_query(F.data.startswith("select_task_assign_"), TaskManagement.select_task)
async def process_select_task_assign(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split("_")[3])
    await state.update_data(assign_task_id=task_id)

    # Получаем список участников проекта
    data = await state.get_data()
    user_tg_id = callback.from_user.id
    user_table_id = await rq.get_user_id_table(user_tg_id)
    project_id = await rq.get_active_id_project_foruser(user_table_id)

    try: # Добавил try-except для отлова возможных ошибок
        users = await rq.get_users_in_project(project_id)
        if not users:
            await callback.message.answer("В проекте нет участников, которым можно назначить задачу!", reply_markup=kb.adminProjectsPanel)
            await state.clear()
            return

        await state.set_state(TaskManagement.select_user_for_assign)
        await callback.message.answer("Выберите пользователя, которому хотите назначить задачу:", reply_markup=kb.get_users_keyboard(users))
    except Exception as e:
        print(f"Ошибка в process_select_task_assign: {e}")
        await callback.message.answer(f"Произошла ошибка при получении пользователей: {e}", reply_markup=kb.adminProjectsPanel)
        await state.clear()

@router.callback_query(F.data.startswith("select_user_assign_"), TaskManagement.select_user_for_assign)
async def process_select_user_assign(callback: CallbackQuery, state: FSMContext):
    assignee_id = int(callback.data.split("_")[3])

    data = await state.get_data()
    task_id = data["assign_task_id"]
    assign_role = data["assign_role"]
    user_tg_id = callback.from_user.id
    user_table_id = await rq.get_user_id_table(user_tg_id)
    project_id = await rq.get_active_id_project_foruser(user_table_id)

    # Проверяем, что модератор не пытается назначить задачу на администратора
    if assign_role == 3:  # Moderator
        admin_id = await rq.get_admin_id_for_project(project_id)
        if assignee_id == admin_id:
            await callback.message.answer("Модератор не может назначать задачи администратору!", reply_markup=kb.adminProjectsPanel)
            await state.set_state(TaskManagement.select_user_for_assign)
            return await process_select_user_assign()

    try:
        await rq.assign_task_to_user(task_id, assignee_id)
        await callback.message.answer(f"Задача с ID {task_id} успешно назначена пользователю с ID {assignee_id}!", reply_markup=kb.adminProjectsPanel)
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при назначении задачи: {e}", reply_markup=kb.adminProjectsPanel)
    finally:
        await state.clear()


# Обновление статуса

@router.callback_query(F.data == "change_status", TaskManagement.select_action)
async def change_status(callback: CallbackQuery, state: FSMContext):
    user_tg_id = callback.from_user.id
    user_table_id = await rq.get_user_id_table(user_tg_id)
    project_id = await rq.get_active_id_project_foruser(user_table_id)
    role = await rq.check_roleuser_in_project(user_table_id, project_id)
    if role in [3, 2]:
        tasks = await rq.get_all_tasks_by_project(project_id)
    else:
        tasks = await rq.get_tasks_by_user(user_table_id, project_id)
        if not tasks:
            await callback.message.answer("Нет задач назначенных на вас!", reply_markup=kb.userProjectsPanel)
            return
    if not tasks:
        await callback.message.answer("В проекте нет задач для изменения статуса!", reply_markup=kb.adminProjectsPanel)
        return

    await state.set_state(TaskManagement.select_task)

    # Теперь передаем user_id и role в keyboard, чтобы они были доступны при выборе задачи
    await state.update_data(user_id=user_table_id, role=role)

    await callback.message.answer("Выберите задачу, статус которой вы хотите изменить:", reply_markup=kb.get_task_keyboard(tasks, "status"))

@router.callback_query(F.data.startswith("select_task_status_"), TaskManagement.select_task)
async def process_select_task_status(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split("_")[3])
    await state.update_data(selected_task_id=task_id)

    data = await state.get_data()
    user_id = data.get("user_id")
    role = data.get("role")

    await state.set_state(TaskManagement.select_status)

    # Передаем user_id и role в get_status_keyboard, чтобы они были доступны при выборе статуса
    await state.update_data(user_id=user_id, role=role)

    await callback.message.answer("Выберите новый статус для задачи:", reply_markup=kb.get_status_keyboard())

@router.callback_query(F.data.startswith("set_status_"), TaskManagement.select_status)
async def process_set_status(callback: CallbackQuery, state: FSMContext):
    status_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    task_id = data["selected_task_id"]
    user_id = data["user_id"]
    role = data["role"]

    try:
        await rq.update_task_status(task_id, status_id, user_id, role)
        if role in [2, 3]:
            await callback.message.answer(f"Статус задачи с ID {task_id} успешно изменен!", reply_markup=kb.adminProjectsPanel)
        else:
            await callback.message.answer(f"Статус задачи с ID {task_id} успешно изменен!", reply_markup=kb.userProjectsPanel)
    except Exception as e:
        await callback.message.answer(f"Произошла ошибка при изменении статуса задачи: {e}", reply_markup=kb.adminProjectsPanel)
    finally:
        await state.clear()

@router.callback_query(F.data == "cancel_assign")
async def cancel_assign(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    return await callback.message.answer("Изменение статуса отменено.")

@router.callback_query(F.data == "cancel_status", TaskManagement.select_status)
async def cancel_status(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    return await callback.message.answer("Изменение статуса отменено.")


@router.callback_query(F.data == "take_task")
async def take_task(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TaskManagement.take_task)
    await callback.message.answer("Напишите ID нужной задачи в статусе \"Ожидает назначения\"")

@router.message(TaskManagement.take_task)
async def process_take_task(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    user_table_id = await rq.get_user_id_table(tg_id)
    task_id = message.text
    await state.update_data(task_id = task_id)
    data = await state.get_data()
    task_id = data["task_id"]
    status_check = await rq.check_status_task(task_id)
    if status_check != 1:
        await state.clear()
        return await message.answer("Вы выбрали задачу, которой нет или которая уже назначена на другого человека", reply_markup=kb.userProjectsPanel)
    if status_check == False:
        await state.clear()
        return await message.answer("Внутренняя ошибка, задач на назначение нет!")
    if status_check == 1:
        try:
            change_task = await rq.change_task_user_id(user_table_id, task_id)
            if change_status:
                await state.clear()
                return await message.answer("Вы успешно взяли задачу на себя!")
            else:
                await state.clear()
                return await message.answer("Внутренняя ошибка, данной задачи резко не оказалось в списке, возможно ее удалили!")
        except:
            await state.clear()
            return await message.answer("Не известная ошибка!")

        

# Управление аккаунтом проекта

class AccountManagment(StatesGroup):
    delete_account = State()
    leave_projects = State()


@router.message(F.text == "Управление аккаунтом в боте!")
async def account_managment(message: Message):
    tg_id = message.from_user.id
    if await rq.get_user_logged(tg_id):
        return await message.answer("Меню управления аккаунтом проекта:\n" \
        "У вас есть возможность:\n" \
        "1. Удалить аккаунт\n" \
        "2. Выйти из всех проектов", reply_markup=kb.keybordAccountManagment)
    return await message.answer("Вы не зашли в свой аккаунт! /start")

@router.callback_query(F.data == "delete_account")
async def delete_account(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AccountManagment.delete_account)
    tg_id = callback.from_user.id
    await callback.message.answer(f"Если вы точно хотите удалить аккаунт введите: \"Удалить {tg_id}\"")

@router.callback_query(F.data == "leave_project")
async def leave_projects(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AccountManagment.leave_projects)
    tg_id = callback.from_user.id
    await callback.message.answer(f"Если вы точно хотите выйти из всех проектов: \"Выйти из всех проектов {tg_id}\"! \
                                \n*При выходе из проекта, который создали вы, права администратора будут назначены ближайшему модератору!* \
                                \n*А если модераторов нет, проект удалится!*")

@router.message(AccountManagment.leave_projects)
async def process_leave_projects(message: Message, state: FSMContext):
    await state.update_data(leave_message = message.text)
    data = await state.get_data()
    message_leave = data["leave_message"]
    tg_id = message.from_user.id
    if message_leave.lower().strip() == f"выйти из всех проектов {tg_id}".lower().strip():
        try:
            user_table_id = await rq.get_user_id_table(tg_id)
            check_leave_projects = await rq.delete_userproject_all(user_table_id)
            check_delete_project = await rq.delete_project_user_table_id(user_table_id)
            if check_leave_projects > 0:
                if check_delete_project > 0:
                    await message.answer("Вы успешно вышли из проектов, ваши проекты где вы администратор - удалены!")
                else:
                    await message.answer("Вы успешно вышли из проектов")
            else:
                await message.answer("У вас нет проектов!")
        except Exception as e:
            await message.answer(
                f"Произошла ошибка при выходе из проектов: {str(e)}",
                reply_markup=ReplyKeyboardRemove()
            )
    else:
        # Добавим отладочную информацию
        print(f"Ожидалось: 'Выйти из всех проектов {tg_id}', получено: '{message_leave}'")
        await message.answer(
            f"Неверное подтверждение удаления. Ожидается: 'Выйти из всех проектов {tg_id}'. Попробуйте еще раз.",
            reply_markup=ReplyKeyboardRemove()
        )
    
    await state.clear()
            


@router.message(AccountManagment.delete_account)
async def process_delete_account(message: Message, state: FSMContext):
    await state.update_data(delete_message = message.text)
    data = await state.get_data()
    message_delete = data["delete_message"]
    tg_id = message.from_user.id
    if message_delete.lower().strip() == f"удалить {tg_id}".lower().strip():
        try:
            check_delete_row = await rq.delete_account(tg_id)
            if check_delete_row > 0:
                await message.answer(
                    "Вы успешно удалили аккаунт, возвращайтесь еще, /start", 
                    reply_markup=ReplyKeyboardRemove()
                )
            else:
                await message.answer(
                    "У вас нет аккаунта!", 
                    reply_markup=ReplyKeyboardRemove()
                )
        except Exception as e:
            await message.answer(
                f"Произошла ошибка при удалении аккаунта: {str(e)}",
                reply_markup=ReplyKeyboardRemove()
            )
    else:
        # Добавим отладочную информацию
        print(f"Ожидалось: 'Удалить {tg_id}', получено: '{message_delete}'")
        await message.answer(
            f"Неверное подтверждение удаления. Ожидается: 'Удалить {tg_id}'. Попробуйте еще раз.",
            reply_markup=ReplyKeyboardRemove()
        )
    
    await state.clear()


@router.message(F.text == "Посмотреть свои задачи")
async def process_delete_account(message: Message):
    tg_id = message.from_user.id
    if await rq.get_user_logged(tg_id):
        user_table_id = await rq.get_user_id_table(tg_id)
        user_in_activite = await rq.get_true_writing_active_project(user_table_id)
        if user_in_activite:
            id_project_active = await rq.get_project_id_activity(user_table_id)
            tasks = await rq.get_tasks_by_user(id_project_active, user_table_id)
            if tasks:
                output_string = ""
                
                for task in tasks:
                    task_status = task.status_id
                    task_priority = task.priority_id
                    deadline = task.deadline
                    if task_status == 2:
                        task_status = "В работе"
                    elif task_status == 3:
                        task_status = "Выполнена"
                    elif task_status == 4:
                        task_status = "Просрочена"
                    if task_priority == 1:
                        task_priority = "Низкий"
                    elif task_priority == 2:
                        task_priority = "Средний"
                    elif task_priority == 3:
                        task_priority = "Высокий"
                    if deadline == None:
                        deadline = "Не определено"
                    output_string += f"#ID: {task.id}\nНазвание проекта: {task.task_name}\nОписание задачи: {task.description}\nСтатус: {task_status}\nПриоритет: {task_priority}\nDeadline: {deadline}\n\n\n"
                if len(output_string) > 0:
                    return await message.answer(f"{output_string}")
            else:
                return await message.answer("Вы не назначены не на одну задачу!")
        return await message.answer("Вы не вошли в проект!")
    return await message.answer("Вы не вошли в аккаунт бота!")

# Управление комментариями



@router.message(F.text == "Управление комментариями")
async def manage_comments_reply(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    if await rq.get_user_logged(tg_id):
        await state.set_state(TaskManagement.manage_comments)
        await show_task_comment_menu(message, state)
    else:
        return message.answer("Вы не авторизованы! /start", reply_markup=ReplyKeyboardRemove)

@router.message(TaskManagement.manage_comments)
async def show_task_comment_menu(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    if await rq.get_user_logged(tg_id):
        user_table_id = await rq.get_user_id_table(tg_id)
        user_in_activite = await rq.get_true_writing_active_project(user_table_id)
        if user_in_activite:
            id_project_active = await rq.get_project_id_activity(user_table_id)
            check_role_user = await rq.check_roleuser_in_project(user_table_id, id_project_active)
            if check_role_user in [3, 2]:
                tasks = await rq.get_tasks_by_project_assignee(id_project_active)
                output_string = ""
                for task in tasks:
                    if task.assignee:
                        output_string += f"ID: {task.id};  Название задачи: {task.task_name}; Username: @{task.assignee.username}; \n\n"
                if len(output_string) > 0:
                    await state.set_state(TaskManagement.view_comments)
                    await message.answer(f"Задачи:\n{output_string}Введите ID нужной задачи!")
                else:
                    await message.answer("Нет назначенных задач в проекте")
                    await state.clear()
            else:
                tasks = await rq.get_tasks_by_user(id_project_active, user_table_id)
                output_string = ""
                if tasks:
                    for task in tasks:
                        output_string += f"ID: {task.id}; Название задачи: {task.task_name}\n\n"
                    await message.answer(f"Ваши задачи:\n{output_string}Введите ID нужной задачи!")
                    await state.set_state(TaskManagement.view_comments)
                else:
                    await message.answer("Нет задач назначенных на вас!")
                    await state.clear()
        else:
            await message.answer("Вы не зашли в проект!")
            await state.clear()
    else:
        await message.answer("Вы не авторизованы!")
        await state.clear()

# id_task = ""
@router.message(TaskManagement.view_comments)
async def show_comments(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    if await rq.get_user_logged(tg_id):
        user_table_id = await rq.get_user_id_table(tg_id)
        user_in_activite = await rq.get_true_writing_active_project(user_table_id)
        if user_in_activite:
            id_project_active = await rq.get_project_id_activity(user_table_id)
            check_role_user = await rq.check_roleuser_in_project(user_table_id, id_project_active)
            await state.update_data(id_task = message.text,
                                    cur_user_table_id = user_table_id)
            data = await state.get_data()
            id_task = data["id_task"]
            task_list = []
            if check_role_user in [3, 2]:
                tasks = await rq.get_tasks_by_project_assignee(id_project_active)
                for task in tasks:
                    task_list.append(task.id)
                if int(id_task) in task_list:
                    comments_list = await rq.get_comments(id_task)
                    if len(comments_list) > 0:
                        output_string = ""
                        for comment in comments_list:
                            output_string += f"ID комментария: {comment.id}\nАвтор комментария: @{comment.user.username}\nТекст комментария: {comment.comment_text}\n\n"
                        await message.answer(f"Коментарии к задаче ID {id_task}:\n{output_string}", reply_markup=kb.keyboardAddComments)
                        await state.set_state(TaskManagement.add_comment)
                    else:
                        await message.answer("У данной задачи нет комментариев!\n\n", reply_markup=kb.keyboardAddComments)
                        await state.set_state(TaskManagement.add_comment)
                else:
                    await message.answer("Такой задачи нет в списке доступных вам задач!")
                    await state.clear()
            else:
                tasks = await rq.get_tasks_by_user(id_project_active, user_table_id)
                for task in tasks:
                    task_list.append(task.id)
                if int(id_task) in task_list:
                    comments_list = await rq.get_comments(id_task)
                    if len(comments_list) > 0:
                        output_string = ""
                        for comment in comments_list:
                            output_string += f"ID комментария: {comment.id}\nАвтор комментария: @{comment.user.username}\nТекст комментария: {comment.comment_text}\n\n"
                        await message.answer(f"Коментарии к задаче ID {id_task}:\n{output_string}", reply_markup=kb.keyboardAddComments)
                        await state.set_state(TaskManagement.add_comment)
                    else:
                        await message.answer("У данной задачи нет комментариев!\n\n", reply_markup=kb.keyboardAddComments)
                        await state.set_state(TaskManagement.add_comment)
                else:
                    await message.answer("Такой задачи нет в списке доступных вам задач!")
                    await state.clear()
        else:
            await message.answer("Вы не вошли в проект!")
            await state.clear()        
    else:
        await message.answer("Вы не авторизованы!")     
        await state.clear()

@router.callback_query(F.data == "adding_comment", TaskManagement.add_comment)
async def adding_new_comment(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите текст комментария!")
    await state.set_state(TaskManagement.add_comment_process)

@router.message(TaskManagement.add_comment_process)
async def process_adding_new_comment(message:Message, state: FSMContext):
    await state.update_data(comment_text = message.text)
    data = await state.get_data()
    comment_text = data.get("comment_text")
    id_task = data.get("id_task")
    cur_user_table_id = data.get("cur_user_table_id")
    if await rq.add_new_comment(id_task, cur_user_table_id, comment_text):
        return await message.answer("Комментарий успешно добавлен!")
    return await message.answer("Неожиданная ошибка, попробуйте позже!")
    

# Управление аккаунтом проекта

@router.message(F.text == "Управление аккаунтом проекта")
async def account_project_managment(message: Message):
    tg_id = message.from_user.id
    if await rq.get_user_logged(tg_id):
        user_table_id = await rq.get_user_id_table(tg_id)
        user_in_activite = await rq.get_true_writing_active_project(user_table_id)
        if user_in_activite:
            id_project_active = await rq.get_project_id_activity(user_table_id)
            check_role_user = await rq.check_roleuser_in_project(user_table_id, id_project_active)
            if check_role_user in [3, 1]:
                return await message.answer("Вы в меню управления аккаунтом проекта!\nВаши возможности:\n1. Выйти из проекта", reply_markup=kb.get_keyboard_managment_account_project(check_role_user))   
            return await message.answer("Вы в меню управления аккаунтом проекта!\nВаши возможности:\n1. Выйти из проекта\n2. Удалить проект!", reply_markup=kb.get_keyboard_managment_account_project(check_role_user))     
        
    return await message.answer("Вы не авторизованы в боте! /start") 
    
class managmentAccountProjects(StatesGroup):
    mc_leave_project = State()
    mc_delete_project = State()

@router.callback_query(F.data == "mc_delete_project")
async def mc_leave_project_f(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    user_table_id = await rq.get_user_id_table(tg_id)
    id_project_active = await rq.get_project_id_activity(user_table_id)
    await state.set_state(managmentAccountProjects.mc_delete_project)
    await callback.message.answer(f"Для подтверждения, введите: \"Удалить проект: {id_project_active}\"")

@router.message(managmentAccountProjects.mc_delete_project)
async def process_mc_delete_project(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    await state.update_data(success=message.text)
    data = await state.get_data()
    success = data["success"]
    if await rq.get_user_logged(tg_id):
        user_table_id = await rq.get_user_id_table(tg_id)
        user_in_activite = await rq.get_true_writing_active_project(user_table_id)
        if user_in_activite:
            id_project_active = await rq.get_project_id_activity(user_table_id)
            desired_str = f"удалить проект: {id_project_active}"
            if success.lower().strip() == desired_str.strip():
                try:
                    await rq.delete_project_user_table_id(user_table_id)
                    await message.answer("Успешное удаление проекта!", reply_markup=kb.mainMenuKeyBoard)
                except Exception as e:
                        await message.answer(
                        f"Произошла ошибка при выходе из проекта: {str(e)}"
                    )
            else:
                await message.answer("Вы ввели совсем не то, что требовалось, попробуйте еще раз! Заного перейдите в раздел управления аккаунтом проекта!")
        else:
           await message.answer("Вы не зашли в проект!") 
    else:
        await message.answer("Вы не авторизованы в аккаунте!")
    await state.clear()


@router.callback_query(F.data == "mc_leave_project")
async def mc_leave_project_f(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    user_table_id = await rq.get_user_id_table(tg_id)
    id_project_active = await rq.get_project_id_activity(user_table_id)
    await state.set_state(managmentAccountProjects.mc_leave_project)
    await callback.message.answer(f"Для подтверждения, введите: \"Выйти проект: {id_project_active}\"")

@router.message(managmentAccountProjects.mc_leave_project)
async def process_mc_leave_project(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    await state.update_data(success=message.text)
    data = await state.get_data()
    success = data["success"]
    if await rq.get_user_logged(tg_id):
        user_table_id = await rq.get_user_id_table(tg_id)
        user_in_activite = await rq.get_true_writing_active_project(user_table_id)
        if user_in_activite:
            id_project_active = await rq.get_project_id_activity(user_table_id)
            desired_str = f"выйти проект: {id_project_active}"
            if success.lower().strip() == desired_str.strip():
                try:
                    await rq.delete_userproject(user_table_id, id_project_active)
                    await message.answer("Вы успешно вышли из проекта!", reply_markup=kb.mainMenuKeyBoard)
                except Exception as e:
                    await message.answer(
                    f"Произошла ошибка при выходе из проекта: {str(e)}"
                )
            else:
                await message.answer("Вы ввели совсем не то, что требовалось, попробуйте еще раз! Заного перейдите в раздел управления аккаунтом проекта!") 
        else:
           await message.answer("Вы не зашли в проект!") 
    else:
        await message.answer("Вы не авторизованы в аккаунте!")
    await state.clear()




# Управление участниками проекта

class MemberManagement(StatesGroup):
    select_action = State()
    select_user = State()
    ban_reason = State()
    unblock_user = State()
    change_role = State()

# Проверка прав доступа
async def check_access(user_id: int, project_id: int) -> tuple[bool, bool]:
    """Возвращает (is_admin, is_moderator)"""
    async with async_session() as session:
        result = await session.execute(
            select(ProjectsUsers.role_project)
            .where(ProjectsUsers.user_id == user_id)
            .where(ProjectsUsers.project_id == project_id)
        )
        role = result.scalar_one_or_none()
        return role == 2, role in [2, 3]  # 2 - admin, 3 - moderator

# Хэндлер для кнопки управления участниками
@router.message(F.text == "Управление участниками проекта")
async def manage_members(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    async with async_session() as session:
        # Получаем user_id и project_id
        user = await session.execute(
            select(User.id)
            .where(User.tg_id == tg_id)
        )
        user_id = user.scalar_one_or_none()
        
        if not user_id:
            return await message.answer("Пользователь не найден!")
        
        project_id = await rq.get_active_id_project_foruser(user_id)
        
        # Проверка прав
        is_admin, has_access = await check_access(user_id, project_id)
        if not has_access:
            return await message.answer("У вас нет прав для управления участниками!")
        
        # Сохраняем данные в state
        await state.update_data(
            current_user_id=user_id,
            project_id=project_id,
            is_admin=is_admin
        )
        
        # Создаем клавиатуру
        builder = InlineKeyboardBuilder()
        builder.button(text="Заблокировать участника", callback_data="ban_user")
        builder.button(text="Разблокировать участника", callback_data="unban_user")
        
        if is_admin:
            builder.button(text="Изменить роль", callback_data="change_role")
        
        builder.button(text="Отмена", callback_data="cancel")
        builder.adjust(1)
        
        await message.answer(
            "Выберите действие:",
            reply_markup=builder.as_markup()
        )
        await state.set_state(MemberManagement.select_action)

# Блокировка пользователя
@router.callback_query(F.data == "ban_user", MemberManagement.select_action)
async def select_user_to_ban(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    project_id = data["project_id"]
    
    async with async_session() as session:
        # Получаем активных участников (не забаненных)
        users = await session.execute(
            select(User)
            .join(ProjectsUsers)
            .where(ProjectsUsers.project_id == project_id)
            .where(ProjectsUsers.ban.is_(None))  # Только не забаненные
            .where(ProjectsUsers.exit_date.is_(None))  # Только активные
        )
        users = users.scalars().all()
    
    if not users:
        await callback.message.edit_text("Нет активных участников для блокировки")
        await state.clear()
        return
    
    builder = InlineKeyboardBuilder()
    for user in users:
        builder.button(
            text=f"@{user.username}" if user.username else f"ID {user.id}",
            callback_data=f"ban_{user.id}"
        )
    builder.button(text="Отмена", callback_data="cancel")
    builder.adjust(2)
    
    await callback.message.edit_text(
        "Выберите пользователя для блокировки:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(MemberManagement.select_user)

@router.callback_query(F.data.startswith("ban_"), MemberManagement.select_user)
async def ask_ban_reason(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split("_")[1])
    await state.update_data(target_user_id=user_id)
    
    await callback.message.edit_text(
        "Введите причину блокировки:",
        reply_markup=None  # Убираем клавиатуру
    )
    await state.set_state(MemberManagement.ban_reason)

@router.message(MemberManagement.ban_reason)
async def execute_ban(message: Message, state: FSMContext):
    data = await state.get_data()
    target_user_id = data["target_user_id"]
    project_id = data["project_id"]
    current_user_id = data["current_user_id"]
    reason = message.text
    
    # Проверка, что не блокируем себя
    if target_user_id == current_user_id:
        await message.answer("Вы не можете заблокировать себя!")
        await state.clear()
        return
    
    async with async_session() as session:
        # Проверяем роль целевого пользователя
        target_role = await session.execute(
            select(ProjectsUsers.role_project)
            .where(ProjectsUsers.user_id == target_user_id)
            .where(ProjectsUsers.project_id == project_id)
        )
        target_role = target_role.scalar_one_or_none()
        
        # Админа нельзя заблокировать
        if target_role == 2:
            await message.answer("Нельзя заблокировать администратора проекта!")
            await state.clear()
            return
        
        # Создаем запись о бане
        new_ban = Ban(ban_type="project_ban")
        session.add(new_ban)
        await session.flush()  # Получаем ID нового бана
        
        # Обновляем запись в ProjectsUsers
        await session.execute(
            update(ProjectsUsers)
            .where(ProjectsUsers.user_id == target_user_id)
            .where(ProjectsUsers.project_id == project_id)
            .values(
                ban=new_ban.id,
                ban_description=reason,
                exit_date=datetime.now()
            )
        )
        await session.commit()
    
    await message.answer(
        f"Пользователь успешно заблокирован. Причина: {reason}",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()

# Разблокировка пользователя
@router.callback_query(F.data == "unban_user", MemberManagement.select_action)
async def select_user_to_unban(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    project_id = data["project_id"]
    
    async with async_session() as session:
        # Получаем забаненных пользователей
        users = await session.execute(
            select(User)
            .join(ProjectsUsers)
            .where(ProjectsUsers.project_id == project_id)
            .where(ProjectsUsers.ban.is_not(None))  # Только забаненные
        )
        users = users.scalars().all()
    
    if not users:
        await callback.message.edit_text("Нет заблокированных участников")
        await state.clear()
        return
    
    builder = InlineKeyboardBuilder()
    for user in users:
        builder.button(
            text=f"@{user.username}" if user.username else f"ID {user.id}",
            callback_data=f"unban_{user.id}"
        )
    builder.button(text="Отмена", callback_data="cancel")
    builder.adjust(2)
    
    await callback.message.edit_text(
        "Выберите пользователя для разблокировки:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(MemberManagement.unblock_user)

@router.callback_query(F.data.startswith("unban_"), MemberManagement.unblock_user)
async def execute_unban(callback: CallbackQuery, state: FSMContext):
    target_user_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    project_id = data["project_id"]
    
    async with async_session() as session:
        # Получаем ID бана для удаления
        ban_id = await session.execute(
            select(ProjectsUsers.ban)
            .where(ProjectsUsers.user_id == target_user_id)
            .where(ProjectsUsers.project_id == project_id)
        )
        ban_id = ban_id.scalar_one_or_none()
        
        if ban_id:
            # Удаляем бан
            await session.execute(
                update(ProjectsUsers)
                .where(ProjectsUsers.user_id == target_user_id)
                .where(ProjectsUsers.project_id == project_id)
                .values(
                    ban=None,
                    ban_description=None,
                    exit_date=None
                )
            )
            
            # Удаляем запись из таблицы Ban
            await session.execute(
                delete(Ban)
                .where(Ban.id == ban_id)
            )
            
            await session.commit()
    
    await callback.message.edit_text(
        "Пользователь успешно разблокирован",
        reply_markup=None
    )
    await state.clear()

# Изменение роли (только для админа)
@router.callback_query(F.data == "change_role", MemberManagement.select_action)
async def select_user_to_change_role(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("is_admin"):
        await callback.message.edit_text("Только администратор может изменять роли!")
        await state.clear()
        return
    
    project_id = data["project_id"]
    
    async with async_session() as session:
        users = await session.execute(
            select(User)
            .join(ProjectsUsers)
            .where(ProjectsUsers.project_id == project_id)
            .where(ProjectsUsers.ban.is_(None))  # Не забаненные
            .where(ProjectsUsers.exit_date.is_(None))  # Активные
        )
        users = users.scalars().all()
    
    if not users:
        await callback.message.edit_text("Нет участников для изменения роли")
        await state.clear()
        return
    
    builder = InlineKeyboardBuilder()
    for user in users:
        builder.button(
            text=f"@{user.username}" if user.username else f"ID {user.id}",
            callback_data=f"chrole_{user.id}"
        )
    builder.button(text="Отмена", callback_data="cancel")
    builder.adjust(2)
    
    await callback.message.edit_text(
        "Выберите пользователя для изменения роли:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(MemberManagement.change_role)

@router.callback_query(F.data.startswith("chrole_"), MemberManagement.change_role)
async def select_new_role(callback: CallbackQuery, state: FSMContext):
    target_user_id = int(callback.data.split("_")[1])
    await state.update_data(target_user_id=target_user_id)
    
    builder = InlineKeyboardBuilder()
    builder.button(text="Участник", callback_data="role_1")
    builder.button(text="Модератор", callback_data="role_3")
    builder.button(text="Отмена", callback_data="cancel")
    builder.adjust(2)
    
    await callback.message.edit_text(
        "Выберите новую роль:",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("role_"), MemberManagement.change_role)
async def execute_role_change(callback: CallbackQuery, state: FSMContext):
    new_role = int(callback.data.split("_")[1])
    data = await state.get_data()
    target_user_id = data["target_user_id"]
    project_id = data["project_id"]
    current_user_id = data["current_user_id"]
    
    # Проверка, что не изменяем свою роль
    if target_user_id == current_user_id:
        await callback.message.edit_text("Вы не можете изменить свою собственную роль!")
        await state.clear()
        return
    
    async with async_session() as session:
        # Проверяем, что не изменяем роль другого админа
        target_role = await session.execute(
            select(ProjectsUsers.role_project)
            .where(ProjectsUsers.user_id == target_user_id)
            .where(ProjectsUsers.project_id == project_id)
        )
        target_role = target_role.scalar_one_or_none()
        
        if target_role == 2:  # Админ
            await callback.message.edit_text("Нельзя изменить роль администратора!")
            await state.clear()
            return
        
        # Обновляем роль
        await session.execute(
            update(ProjectsUsers)
            .where(ProjectsUsers.user_id == target_user_id)
            .where(ProjectsUsers.project_id == project_id)
            .values(role_project=new_role)
        )
        await session.commit()
    
    await callback.message.edit_text(
        "Роль пользователя успешно изменена",
        reply_markup=None
    )
    await state.clear()

# Отмена действий
@router.callback_query(F.data == "cancel", StateFilter(MemberManagement))
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Действие отменено",
        reply_markup=None
    )