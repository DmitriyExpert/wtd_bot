from sqlalchemy import (
    BigInteger,
    String,
    ForeignKey,
    Integer,
    TIMESTAMP,
    Text,
    SmallInteger,
    DATETIME,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    sessionmaker,
    relationship,
)
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, AsyncSession
import datetime
import config

DB_USER = config.DB_USER
DB_PASSWORD = config.DB_PASSWORD
DB_HOST = config.DB_HOST
DB_PORT = config.DB_PORT
DB_NAME = config.DB_NAME

DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class AppRole(Base):
    __tablename__ = "app_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    app_role_name: Mapped[str] = mapped_column(String(45), unique=True)
    users: Mapped[list["User"]] = relationship(back_populates="app_role")


class InvitationsStatus(Base):
    __tablename__ = "invitations_status"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status_name: Mapped[str] = mapped_column(String(45), unique=True)
    invitations: Mapped[list["Invitation"]] = relationship(back_populates="invitation_status_obj")


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, unique=True)
    tg_id: Mapped[BigInteger] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    registration_date: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.utcnow
    )
    role: Mapped[int] = mapped_column(ForeignKey("app_roles.id"))
    delete_date: Mapped[datetime.datetime] = mapped_column(DATETIME, nullable=True)
    user_logged: Mapped[SmallInteger] = mapped_column(SmallInteger, default=0)
    app_role: Mapped["AppRole"] = relationship(back_populates="users")
    projects: Mapped[list["Project"]] = relationship(back_populates="admin")
    tasks_created: Mapped[list["Task"]] = relationship(
        foreign_keys="[Task.creator_id]", back_populates="creator"
    )
    tasks_assigned: Mapped[list["Task"]] = relationship(
        foreign_keys="[Task.user_id]", back_populates="assignee"
    )
    comments: Mapped[list["TasksComment"]] = relationship(back_populates="user")
    project_users: Mapped[list["ProjectsUser"]] = relationship(back_populates="user")
    invitations_received: Mapped[list["Invitation"]] = relationship(back_populates="invited_user", foreign_keys="[Invitation.user_id]")
    invitations_sent: Mapped[list["Invitation"]] = relationship(back_populates="sender", foreign_keys="[Invitation.sender_id]")
    project_activity: Mapped["ProjectActivity"] = relationship(back_populates="user", uselist=False) #one to one


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    project_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Text] = mapped_column(Text, nullable=True)
    creation_date: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.utcnow
    )
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    delete_date: Mapped[datetime.datetime] = mapped_column(DATETIME, nullable=True)

    admin: Mapped["User"] = relationship(back_populates="projects")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project")
    project_users: Mapped[list["ProjectsUser"]] = relationship(back_populates="project")
    project_activities: Mapped[list["ProjectActivity"]] = relationship(back_populates="project")
    invitations: Mapped[list["Invitation"]] = relationship(back_populates="project")


class Invitation(Base):
    __tablename__ = "invitation"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    invitation_status: Mapped[int] = mapped_column(ForeignKey("invitations_status.id"), default=1)

    project: Mapped["Project"] = relationship(back_populates="invitations")
    invited_user: Mapped["User"] = relationship(back_populates="invitations_received", foreign_keys=[user_id])
    sender: Mapped["User"] = relationship(back_populates="invitations_sent", foreign_keys=[sender_id])
    invitation_status_obj: Mapped["InvitationsStatus"] = relationship(back_populates="invitations")


class ProjectsRole(Base):
    __tablename__ = "projects_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_role_name: Mapped[str] = mapped_column(String(45), unique=True)
    project_users: Mapped[list["ProjectsUser"]] = relationship(
        back_populates="project_role"
    )


class ProjectsUser(Base):
    __tablename__ = "projects_users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    role_project: Mapped[int] = mapped_column(ForeignKey("projects_roles.id"))
    join_date: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.utcnow
    )
    exit_date: Mapped[datetime.datetime] = mapped_column(DATETIME, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="project_users")
    user: Mapped["User"] = relationship(back_populates="project_users")
    project_role: Mapped["ProjectsRole"] = relationship(back_populates="project_users")


class TasksStatut(Base):
    __tablename__ = "tasks_statuts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status_name: Mapped[str] = mapped_column(String(50), unique=True)
    tasks: Mapped[list["Task"]] = relationship(back_populates="status")


class TasksPriority(Base):
    __tablename__ = "tasks_priority"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    priority_name: Mapped[str] = mapped_column(String(45), unique=True)
    tasks: Mapped[list["Task"]] = relationship(back_populates="priority_obj")


class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    task_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Text] = mapped_column(Text, nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("tasks_statuts.id"), default=3)
    priority_id: Mapped[int] = mapped_column(ForeignKey("tasks_priority.id"), default=3)
    deadline: Mapped[datetime.datetime] = mapped_column(DATETIME, nullable=True)
    creation_date: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.utcnow
    )
    last_update: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, nullable=True, onupdate=datetime.datetime.utcnow
    )
    delete_date: Mapped[datetime.datetime] = mapped_column(DATETIME, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="tasks")
    creator: Mapped["User"] = relationship(
        foreign_keys=[creator_id], back_populates="tasks_created"
    )
    assignee: Mapped["User"] = relationship(
        foreign_keys=[user_id], back_populates="tasks_assigned"
    )
    status: Mapped["TasksStatut"] = relationship(back_populates="tasks")
    priority_obj: Mapped["TasksPriority"] = relationship(back_populates="tasks")
    comments: Mapped[list["TasksComment"]] = relationship(back_populates="task")


class TasksComment(Base):
    __tablename__ = "tasks_comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    comment_text: Mapped[str] = mapped_column(String(500))
    comment_date: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.utcnow
    )
    comment_delete_date: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, nullable=True, onupdate=datetime.datetime.utcnow
    )
    task: Mapped["Task"] = relationship(back_populates="comments")
    user: Mapped["User"] = relationship(back_populates="comments")


class ProjectActivity(Base):
    __tablename__ = "projects_activites"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))

    user: Mapped["User"] = relationship(back_populates="project_activity", uselist=False)
    project: Mapped["Project"] = relationship(back_populates="project_activities")