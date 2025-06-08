from app.database.models import async_session
from app.database.models import User, ProjectsUser, Project, ProjectsRole, ProjectActivity, Invitation
from sqlalchemy import select, delete

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
                select(ProjectsUser).where(ProjectsUser.user_id == user_table_id)
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
                    project_dict[project_field.id] = project_field.project_name  # Store id and name
            if len(project_dict) > 0:
                return project_dict
            else:
                return None



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
            new_project_user = ProjectsUser(
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
            user = await session.scalar(select(ProjectsUser).where(ProjectsUser.project_id == project_id and ProjectsUser.user_id == user_table_id))
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
            role = await session.scalar(select(ProjectsUser.role_project).where(ProjectsUser.project_id == project_id and ProjectsUser.user_id == user_table_id))
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