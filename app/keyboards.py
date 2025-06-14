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

mainMenuKeyBoard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать проект")],
        [KeyboardButton(text="Проверить приглашения в проекты")],
        [KeyboardButton(text="Отправить заявку на вступление в проект")],
        [KeyboardButton(text="Мои проекты")],
        [KeyboardButton(text="Посмотреть информацию о себе!")],
        [KeyboardButton(text="Управление аккаунтом в боте!")],
        [KeyboardButton(text="Выйти из аккаунта wtdbot")],
        [KeyboardButton(text="FAQ по использованию")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите пункт меню для дальнейших действий!",
)


adminProjectsPanel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Посмотреть свои задачи")],
        [KeyboardButton(text="Управление задачами")],
        [KeyboardButton(text="Управление участниками проекта")],
        [KeyboardButton(text="Управление комментариями")],
        [KeyboardButton(text="Отправить приглашение на вступление")],
        [KeyboardButton(text="Проверить заявки на вступление")],
        [KeyboardButton(text="Управление аккаунтом проекта")],
        [KeyboardButton(text="В главное меню")],
    ],
    resize_keyboard=True,
)

moderatorProjectsPanel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Посмотреть свои задачи")],
        [KeyboardButton(text="Управление задачами")],
        [KeyboardButton(text="Управление участниками проекта")],
        [KeyboardButton(text="Управление комментариями")],
        [KeyboardButton(text="Проверить заявки на вступление")],
        [KeyboardButton(text="Управление аккаунтом проекта")],
        [KeyboardButton(text="В главное меню")],
    ],
    resize_keyboard=True,
)

userProjectsPanel = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Посмотреть свои задачи")],
        [KeyboardButton(text="Управление задачами")],
        [KeyboardButton(text="Управление комментариями")],
        [KeyboardButton(text="Управление аккаунтом проекта")],
        [KeyboardButton(text="В главное меню")],
    ],
    resize_keyboard=True,
)

keybordSendInvite = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Отправить приглашение по @username",
                callback_data="send_to_username",
            )
        ],
        [
            InlineKeyboardButton(
                text="Отправить приглашение по телеграмм id",
                callback_data="send_to_tgid",
            )
        ],
    ]
)

keybordAccountManagment = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Удалить аккаунт", callback_data="delete_account")],
        [
            InlineKeyboardButton(
                text="Выйти из всех проектов", callback_data="leave_project"
            )
        ],
    ]
)

keyboardAccessInvite = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Принять приглашение по id", callback_data="access_invite"
            )
        ],
        [InlineKeyboardButton(text="Отказаться по id", callback_data="reject_invite")],
    ]
)

keyboardAddComments = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Добавить комментарий к задаче!", callback_data="adding_comment"
            )
        ]
    ]
)

keybordApplyInvite = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="По ID проекта", callback_data="apply_by_id")],
        [
            InlineKeyboardButton(
                text="По username админа", callback_data="apply_by_admin"
            )
        ],
    ]
)


def applicationActionsKeyBoard(target_user_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Принять", callback_data=f"application_accept_{target_user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Отклонить",
                    callback_data=f"application_reject_{target_user_id}",
                )
            ],
        ]
    )
    return keyboard


def get_task_management_keyboard(role):
    keyboard = []
    if role == 2:
        keyboard.append(
            [InlineKeyboardButton(text="Создать задачу", callback_data="create_task")]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Редактировать задачу", callback_data="edit_task"
                )
            ]
        )
        keyboard.append(
            [InlineKeyboardButton(text="Удалить задачу", callback_data="delete_task")]
        )
        keyboard.append(
            [InlineKeyboardButton(text="Назначить задачу", callback_data="assign_task")]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Изменить статус задачи", callback_data="change_status"
                )
            ]
        )
    elif role == 3:
        keyboard.append(
            [InlineKeyboardButton(text="Создать задачу", callback_data="create_task")]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Редактировать задачу", callback_data="edit_task"
                )
            ]
        )
        keyboard.append(
            [InlineKeyboardButton(text="Назначить задачу", callback_data="assign_task")]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Изменить статус задачи", callback_data="change_status"
                )
            ]
        )
    else:
        keyboard.append(
            [InlineKeyboardButton(text="Взять задачу", callback_data="take_task")]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Изменить статус задачи", callback_data="change_status"
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_keyboard_managment_users_project(role):
    keyboard = []
    if role == 2:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Заблокировать пользователя!",
                    callback_data="permanent_ban_users",
                )
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Разблокировать пользователя", callback_data="unblock_user"
                )
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Изменить роль пользователя",
                    callback_data="change_role_project",
                )
            ]
        )
    elif role == 3:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Заблокировать пользователя!",
                    callback_data="permanent_ban_users",
                )
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Разблокировать пользователя", callback_data="unblock_user"
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_keyboard_managment_account_project(role):
    keyboard = []
    if role in [3, 1]:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Выйти из проекта", callback_data="mc_leave_project"
                )
            ]
        )
    else:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Выйти из проекта", callback_data="mc_leave_project"
                )
            ]
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    text="Удалить проект", callback_data="mc_delete_project"
                )
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_task_keyboard(tasks, action=None):
    keyboard = []
    for task in tasks:
        user_info = ""
        if task.assignee:
            user_info = f" (@{task.assignee.username})"
        if action == "assign":
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"{task.id} - {task.task_name}{user_info}",
                        callback_data=f"select_task_assign_{task.id}",
                    )
                ]
            )
        elif action == "edit":
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"{task.id} - {task.task_name}{user_info}",
                        callback_data=f"select_task_edit_{task.id}",
                    )
                ]
            )
        elif action == "status":
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"{task.id} - {task.task_name}{user_info}",
                        callback_data=f"select_task_status_{task.id}",
                    )
                ]
            )
        else:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"{task.id} - {task.task_name}{user_info}",
                        callback_data=f"select_task_view_{task.id}",
                    )
                ]
            )

    keyboard.append(
        [InlineKeyboardButton(text="Отмена", callback_data="cancel_assign")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_users_keyboard(users):
    keyboard = []
    for user in users:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"@{user.username} ({user.first_name} {user.last_name})",
                    callback_data=f"select_user_assign_{user.id}",
                )
            ]
        )
    keyboard.append(
        [InlineKeyboardButton(text="Отмена", callback_data="cancel_assign")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_tasks_keyboard(tasks, action=None):
    keyboard = []
    for task in tasks:
        if action == "assign":
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"{task.id} - {task.task_name}",
                        callback_data=f"select_task_assign_{task.id}",
                    )
                ]
            )
        else:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        text=f"{task.id} - {task.task_name}",
                        callback_data=f"select_task_edit_{task.id}",
                    )
                ]
            )
    keyboard.append(
        [InlineKeyboardButton(text="Отмена", callback_data="cancel_assign")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_status_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="В работе", callback_data="set_status_2")],
        [InlineKeyboardButton(text="Выполнена", callback_data="set_status_3")],
        [InlineKeyboardButton(text="Просрочена", callback_data="set_status_4")],
        [
            InlineKeyboardButton(
                text="Ожидает назначения", callback_data="set_status_1"
            )
        ],  # Добавил возможность вернуть в ожидание назначения
        [InlineKeyboardButton(text="Отмена", callback_data="cancel_status")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
