from datetime import datetime
from app.database.models import async_session
from app.database.models import User, ProjectsUsers, Project, ProjectsRole, ProjectActivity, Invitation, ProjectApplication, Task, TasksStatus, TasksComment
from sqlalchemy import select, delete, or_, and_
from sqlalchemy.orm import selectinload

async def get_user(user_tg_id):
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == user_tg_id))


async def get_user_logged(user_tg_id):
    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.tg_id == user_tg_id))
            if user:
                return user.user_logged
            else:
                return None


async def get_user_id_table(user_tg_id):
    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.tg_id == user_tg_id))
            if user:
                return user.id
            else:
                return None


async def get_myreg_in_projects(user_table_id):
    async with async_session() as session:
        async with session.begin():
            myreglist = await session.scalars(
                select(ProjectsUsers).where(ProjectsUsers.user_id == user_table_id)
            )
            reg_list = set()
            if myreglist:
                for reg in myreglist:
                    reg_list.add(reg.project_id)
                return reg_list
            else:
                return None


async def get_projects_list(reg_list):
    async with async_session() as session:
        async with session.begin():
            project_dict = {}
            for project_id in reg_list:
                project_field = await session.scalar(
                    select(Project).where(Project.id == project_id)
                )
                if project_field:
                    project_dict[project_field.id] = project_field.project_name
            if len(project_dict) > 0:
                return project_dict
            else:
                return None

async def change_task_user_id(user_id, task_id):
    async with async_session() as session:
        async with session.begin():
            task = await session.scalar(select(Task).where(Task.id == task_id))
            if task:
                task.user_id = user_id
                task.status_id = 2
                await session.commit()
                return True
            else:
                return False
            


async def change_user_logged(user_tg_id):
    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(select(User).where(User.tg_id == user_tg_id))
            if user:
                user.user_logged = 0 if user.user_logged == 1 else 1
                await session.commit()
                return user.user_logged
            else:
                return None


async def create_new_project(project_name: str, description: str, admin_id: int):
    async with async_session() as session:
        async with session.begin():
            new_project = Project(
                project_name=project_name,
                description=description,
                admin_id=admin_id,
            )
            session.add(new_project)
            await session.flush()
            project_id = new_project.id
            admin_project_role = await session.scalar(select(ProjectsRole.id).where(ProjectsRole.project_role_name == "Администратор"))
            if not admin_project_role:
                print("Роль не найдена!")
                raise ValueError("Добавьте роль Администратор в таблицу")
            new_project_user = ProjectsUsers(
                project_id=project_id,
                user_id=admin_id,
                role_project=admin_project_role
            )
            session.add(new_project_user)
            return await session.commit()

async def get_writing_active_project(user_table_id):
    async with async_session() as session:
        async with session.begin():
            write = await session.scalar(select(ProjectActivity).where(ProjectActivity.user_id == user_table_id))
            if write:
                return None
            else:
                return True
            
async def get_true_writing_active_project(user_table_id):
    async with async_session() as session:
        async with session.begin():
            write = await session.scalar(select(ProjectActivity).where(ProjectActivity.user_id == user_table_id))
            if write:
                return True
            else:
                return None

async def get_active_id_project_foruser(user_table_id):
    async with async_session() as session:
        async with session.begin():
            project_id = await session.scalar(select(ProjectActivity.project_id).where(ProjectActivity.user_id == user_table_id))
            return project_id
        

async def checking_user_in_project(user_table_id, project_id):
    async with async_session() as session:
        async with session.begin():
            user = await session.scalar(select(ProjectsUsers).where(ProjectsUsers.project_id == project_id and ProjectsUsers.user_id == user_table_id))
            if user:
                return True
            else:
                return None      

async def writing_to_activites_projects(user_table_id, project_id):
    async with async_session() as session:
        async with session.begin():
            new_write_active_project = ProjectActivity(
                user_id = user_table_id,
                project_id = project_id
            )
            session.add(new_write_active_project)
            return await session.commit()
        
async def check_roleuser_in_project(user_table_id, project_id):
    async with async_session() as session:
        async with session.begin():
            role = await session.scalar(select(ProjectsUsers.role_project).where(ProjectsUsers.project_id == project_id and ProjectsUsers.user_id == user_table_id))
            return role


async def del_activites_project(user_table_id):
    async with async_session() as session:
        try:
            async with session.begin():
                result = await session.execute(
                    delete(ProjectActivity).where(ProjectActivity.user_id == user_table_id)
                )
                await session.commit()
                return result.rowcount
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при удалении активностей проекта: {e}")
            return 0
            
async def post_invitation(sender_id, project_id, user_id):
    async with async_session() as session:
        async with session.begin():
            new_inv = Invitation(
                sender_id = sender_id,
                project_id = project_id,
                user_id = user_id
            )
            session.add(new_inv)
            return await session.commit()

async def get_userid_for_username(username):
    async with async_session() as session:
        async with session.begin():
            user_id = await session.scalar(select(User.id).where(User.username == username))
            if user_id:
                return user_id
            return False
        
async def get_userid_for_tgid(tg_id):
    async with async_session() as session:
        async with session.begin():
            user_id = await session.scalar(select(User.id).where(User.tg_id == tg_id))
            if user_id:
                return user_id
            return False
        
async def check_invite_in_project(user_id, project_id):
    async with async_session() as session:
        async with session.begin():
            invite = await session.scalar(select(Invitation.id).where(Invitation.project_id == project_id and Invitation.user_id == user_id))
            if invite:
                return True
            return False
        
async def get_invitations_for_user(user_id: int) -> list:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Invitation)
                .options(selectinload(Invitation.project), selectinload(Invitation.sender))
                .where(Invitation.user_id == user_id)
            )
            invitations = result.scalars().all()
            return invitations

async def change_inviteid_for_access(user_table_id, project_id):
    async with async_session() as session:
        async with session.begin():
            invite = await session.scalar(select(Invitation).where(Invitation.user_id == user_table_id and Invitation.project_id == project_id))
            if invite:
                if invite.invitation_status == 1:
                    invite.invitation_status = 2
                    await session.commit()
                    return True
                return None
            return False

async def change_inviteid_for_reject(user_table_id, project_id):
    async with async_session() as session:
        async with session.begin():
            invite = await session.scalar(select(Invitation).where(Invitation.user_id == user_table_id and Invitation.project_id == project_id))
            if invite:
                if invite.invitation_status == 1:
                    invite.invitation_status = 3
                    await session.commit()
                    return True
                return None
            return False
                
async def post_new_project_user_invite(user_id, project_id):
    async with async_session() as session:
        async with session.begin():
            new_user_project = ProjectsUsers(
                project_id = project_id,
                user_id = user_id
            )
            session.add(new_user_project)
            return await session.commit()
    
# Project Application
async def post_project_application(user_id, project_id):
    async with async_session() as session:
        async with session.begin():
            new_application = ProjectApplication(
                user_id=user_id,
                project_id=project_id
            )
            session.add(new_application)
            return await session.commit()

async def get_project(project_id):
    async with async_session() as session:
        async with session.begin():
            return await session.scalar(select(Project).where(Project.id == project_id))

async def get_project_id_activity(user_table_id):
    async with async_session() as session:
        async with session.begin():
            try:
                result = await session.scalar(select(ProjectActivity.project_id).where(ProjectActivity.user_id == user_table_id))
                return result
            except Exception as e:
                await session.rollback()
                raise
            
        
async def check_application_exists(user_id, project_id):
     async with async_session() as session:
        async with session.begin():
            application = await session.scalar(select(ProjectApplication).where(ProjectApplication.user_id == user_id, ProjectApplication.project_id == project_id))
            if application:
                return True
            return False

async def get_projects_by_admin(admin_id):
    async with async_session() as session:
        async with session.begin():
            projects = await session.scalars(select(Project).where(Project.admin_id == admin_id))
            return projects.all()
        
        
async def get_pending_applications(project_id):
    async with async_session() as session:
        async with session.begin():
            applications = await session.scalars(select(ProjectApplication).options(selectinload(ProjectApplication.user)).where(ProjectApplication.project_id == project_id, ProjectApplication.status == "Pending"))
            return applications.all()
        
async def accept_application(user_id, project_id):
    async with async_session() as session:
        async with session.begin():
            application = await session.scalar(select(ProjectApplication).where(ProjectApplication.user_id == user_id, ProjectApplication.project_id == project_id))
            if application:
                application.status = "Accepted"
                await session.commit()
                return True
            return False
        
async def reject_application(user_id, project_id):
    async with async_session() as session:
        async with session.begin():
            application = await session.scalar(select(ProjectApplication).where(ProjectApplication.user_id == user_id, ProjectApplication.project_id == project_id))
            if application:
                application.status = "Rejected"
                await session.commit()
                return True
            return False
        
async def delete__application(target_user_id, project_id):
    async with async_session() as session:
        async with session.begin():
            try:
                application = await session.execute(delete(ProjectApplication).where(ProjectApplication.user_id == target_user_id, ProjectApplication.project_id == project_id))
                await session.commit()
                return application.rowcount
            except Exception as e:
                await session.rollback()
                print(f"Ошибка при удалении заявки на вступление в проект: {e}")
                return 0
            

async def check_rejected_application_exists(user_id, project_id):
    async with async_session() as session:
        async with session.begin():
            application = await session.scalar(
                select(ProjectApplication)
                .where(ProjectApplication.user_id == user_id, ProjectApplication.project_id == project_id, ProjectApplication.status == "Rejected")
            )
            if application:
                return True
            return False

async def get_admin_by_project(project_id):
    async with async_session() as session:
        async with session.begin():
            project = await session.scalar(
                select(Project)
                .options(selectinload(Project.admin))
                .where(Project.id == project_id)
            )
            if project:
                return project.admin
            return None
        
# Управление проектами

async def get_tasks_by_status(project_id: int, status_id: int):
    async with async_session() as session:
        async with session.begin():
            tasks = await session.scalars(
                select(Task)
                .where(Task.project_id == project_id, Task.status_id == status_id)
                .options(selectinload(Task.assignee))
            )
            return tasks.all()

async def create_new_task(project_id: int, task_name: str, description: str | None, creator_id: int, deadline: datetime | None, priority_id: int):
    async with async_session() as session:
        async with session.begin():
            new_task = Task(
                project_id=project_id,
                task_name=task_name,
                description=description,
                creator_id=creator_id,
                deadline=deadline,
                priority_id=priority_id,
                status_id=1
            )
            session.add(new_task)
            return await session.commit()
    

# Редактирование задачи 

async def update_task(task_id: int, task_name: str | None, description: str | None, deadline: datetime | None, priority_id: int):
    async with async_session() as session:
        async with session.begin():
            task = await session.scalar(select(Task).where(Task.id == task_id))
            if task:
                if task_name:
                    task.task_name = task_name
                if description is not None:
                    task.description = description
                if deadline is not None:
                    task.deadline = deadline
                task.priority_id = priority_id

                await session.commit()
                return True
            return False
        
async def get_tasks_by_project(project_id):
    async with async_session() as session:
        async with session.begin():
            tasks = await session.scalars(
                select(Task)
                .where(Task.project_id == project_id)
            )
            return tasks.all()

async def get_tasks_by_project_assignee(project_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Task)
            .options(selectinload(Task.assignee))  # Жадная загрузка исполнителя
            .where(Task.project_id == project_id)
        )
        return result.scalars().all()
        
async def get_tasks_by_user(project_id, user_id):
    async with async_session() as session:
        async with session.begin():
            tasks = await session.scalars(
                select(Task)
                .where(Task.user_id == user_id and Task.project_id == project_id)
            )
            return tasks.all()
# Удаление задачи


async def get_task_by_id(task_id: int):
    async with async_session() as session:
        async with session.begin():
            task = await session.scalar(
                select(Task)
                .where(Task.id == task_id)
                .options(selectinload(Task.assignee))  # Load assignee
            )
            return task

async def get_admin_id_for_project(project_id: int):
    async with async_session() as session:
        async with session.begin():
            project = await session.scalar(select(Project).where(Project.id == project_id))
            if project:
                return project.admin_id
            return None 

async def delete_task(task_id: int):
    async with async_session() as session:
        async with session.begin():
            task = await session.scalar(select(Task).where(Task.id == task_id))
            if task:
                await session.delete(task)
                await session.commit()
            else:
                return False

async def check_status_task(task_id: int):
    async with async_session() as session:
        async with session.begin():
            status = await session.scalar(select(Task.status_id).where(Task.id == task_id))
            if status:
                return status
            else:
                return False
            
# Назначение задачи 

# async def get_tasks_by_project(project_id: int):
#     async with async_session() as session:
#         async with session.begin():
#             tasks = await session.scalars(
#                 select(Task)
#                 .where(Task.project_id == project_id, Task.status_id == 1)  # Ожидают назначения
#             )
#             return tasks.all()

async def get_users_in_project(project_id: int):
    async with async_session() as session:
        async with session.begin():
            # Здесь мы получаем все записи ProjectUser для данного project_id
            project_users = await session.scalars(
                select(ProjectsUsers)
                .where(ProjectsUsers.project_id == project_id)
            )
            project_users = project_users.all()

            # Затем из каждой записи ProjectUser получаем соответствующего пользователя
            users = [project_user.user for project_user in project_users]
            return users

async def assign_task_to_user(task_id: int, assignee_id: int):
    async with async_session() as session:
        async with session.begin():
            task = await session.scalar(select(Task).where(Task.id == task_id))
            if not task:
                raise Exception("Задача с таким ID не найдена!")
            
            task.assignee_id = assignee_id
            task_status_in_progress = await session.scalar(select(TasksStatus).where(TasksStatus.status_name == "В работе"))
            task.status_in_progress_id = task_status_in_progress
            await session.commit()

async def get_admin_id_for_project(project_id: int):
    async with async_session() as session:
        async with session.begin():
            project = await session.scalar(select(Project).where(Project.id == project_id))
            if project:
                return project.admin_id
            return None 

async def assign_task_to_user(task_id: int, assignee_id: int):
    async with async_session() as session:
        async with session.begin():
            try:
                task = await session.scalar(select(Task).where(Task.id == task_id))
                if not task:
                    raise Exception("Задача с таким ID не найдена!")
                task.user_id = assignee_id  #  Присваиваем задаче пользователя
                # Получаем статус "В работе"
                task_status_in_progress = await session.scalar(select(TasksStatus).where(TasksStatus.id == 2))
                if not task_status_in_progress:
                    raise Exception("Статус 'В работе' не найден!")
                task.status_id = task_status_in_progress.id #  Устанавливаем ID статуса
                await session.commit()
            except Exception as e:
                await session.rollback()  # Откатываем транзакцию при ошибке
                raise

async def get_tasks_by_user(user_table_id: int, project_id: int):
    async with async_session() as session:
        async with session.begin():
            tasks = await session.scalars(
                select(Task)
                .where(Task.project_id == project_id, Task.user_id == user_table_id)
                .options(selectinload(Task.assignee))
            )
            return tasks.all()

async def get_all_tasks_by_project(project_id: int):
    async with async_session() as session:
        async with session.begin():
            tasks = await session.scalars(
                select(Task)
                .where(Task.project_id == project_id)  # Все задачи, независимо от статуса
                .options(selectinload(Task.assignee))
            )
            return tasks.all()

async def get_tasks_by_status(project_id: int, status_id: int):
    async with async_session() as session:
        async with session.begin():
            tasks = await session.scalars(
                select(Task)
                .where(Task.project_id == project_id, Task.status_id == status_id)
                .options(selectinload(Task.assignee))
            )
            return tasks.all()

async def update_task_status(task_id: int, status_id: int, user_id: int, role: int):
    async with async_session() as session:
        async with session.begin():
            try:
                task = await session.scalar(select(Task).where(Task.id == task_id))
                if not task:
                    raise Exception("Задача с таким ID не найдена!")

                # Получаем project_id из task
                project_id = task.project_id

                # Получаем проект и admin_id
                project = await session.scalar(select(Project).where(Project.id == project_id))
                if not project:
                    raise Exception("Проект с таким ID не найден!")
                admin_id = project.admin_id

                # Сравниваем user_id с admin_id
                if role == 3 and user_id != admin_id:  # Модератор и не админ
                    if task.creator_id == admin_id:
                        raise Exception("Модератор не может менять статус задачи, созданной администратором!")

                task.status_id = status_id

                if status_id == 1:  # Если статус "Ожидает назначения" (ID = 1)
                    task.user_id = None  # Очищаем user_id

                await session.commit()
            except Exception as e:
                await session.rollback()
                raise

async def get_priority_task(task_id):
    async with async_session() as session:
        async with session.begin():
            try:
                priority = await session.scalar(select(Task.priority_id).where(Task.id == task_id))
                return priority
            except Exception as e:
                await session.rollback()
                raise

async def delete_account(tg_id):
    async with async_session() as session:
        async with session.begin():
            try:
                result = await session.execute(
                    delete(User).where(User.tg_id == tg_id)
                )   
                await session.commit()
                return result.rowcount
            except Exception as e:
                await session.rollback()
                raise

async def delete_userproject_all(user_table_id):
    async with async_session() as session:
        async with session.begin():
            try:
                result = await session.execute(delete(ProjectsUsers).where(ProjectsUsers.user_id == user_table_id))
                await session.commit()
                return result.rowcount
            except Exception as e:
                await session.rollback()
                raise

async def delete_userproject_all_projectid(project_id):
    async with async_session() as session:
        async with session.begin():
            try:
                result = await session.execute(delete(ProjectsUsers).where(ProjectsUsers.project_id == project_id))
                await session.commit()
                return result.rowcount
            except Exception as e:
                await session.rollback()
                raise

async def delete_userproject(user_table_id, project_id):
    async with async_session() as session:
        async with session.begin():
            try:
                result = await session.execute(delete(ProjectsUsers).where(ProjectsUsers.user_id == user_table_id, ProjectsUsers.project_id == project_id))
                await session.commit()
                return result.rowcount
            except Exception as e:
                await session.rollback()
                raise

async def delete_project_user_table_id(user_table_id):
    async with async_session() as session:
        async with session.begin():
            try:
                result = await session.execute(delete(Project).where(Project.admin_id == user_table_id))
                await session.commit()
                return result.rowcount
            except Exception as e:
                await session.rollback()
                raise

async def get_comments(task_id):
    async with async_session() as session:
        async with session.begin():
            try:
                comments = await session.scalars(select(TasksComment).where(TasksComment.task_id == task_id).options(selectinload(TasksComment.user)))
                return comments.all()
            except Exception as e:
                await session.rollback()
                raise
        
async def add_new_comment(id_task, user_table_id, comment_text):
    async with async_session() as session:
        async with session.begin():
            try:
                new_comment = TasksComment(
                    task_id = id_task,
                    user_id = user_table_id,
                    comment_text = comment_text,
                )

                session.add(new_comment)
                await session.commit()
                return True
            
            except Exception as e:
                await session.rollback()
                raise
