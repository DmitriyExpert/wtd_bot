from sqlalchemy import BigInteger, String, ForeignKey, Integer, TIMESTAMP, Text
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
    __tablename__ = "App_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    app_role_name: Mapped[str] = mapped_column(String(45), unique=True)
    users: Mapped[list["User"]] = relationship(back_populates="app_role")


class User(Base):
    __tablename__ = "Users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tg_id: Mapped[BigInteger] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    registration_date: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.utcnow
    )
    role: Mapped[int] = mapped_column(ForeignKey("App_roles.id"))
    delete_date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=True)

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


class Project(Base):
    __tablename__ = "Projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Text] = mapped_column(Text, nullable=True)
    creation_date: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.utcnow
    )
    admin_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    delete_date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=True)

    admin: Mapped["User"] = relationship(back_populates="projects")
    tasks: Mapped[list["Task"]] = relationship(back_populates="project")
    project_users: Mapped[list["ProjectsUser"]] = relationship(back_populates="project")


class ProjectsRole(Base):
    __tablename__ = "Projects_roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_role_name: Mapped[str] = mapped_column(String(45), unique=True)
    project_users: Mapped[list["ProjectsUser"]] = relationship(
        back_populates="project_role"
    )


class ProjectsUser(Base):
    __tablename__ = "Projects_users"
    project_id: Mapped[int] = mapped_column(ForeignKey("Projects.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"), primary_key=True)
    role_project: Mapped[int] = mapped_column(ForeignKey("Projects_roles.id"))
    join_date: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.utcnow
    )
    exit_date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="project_users")
    user: Mapped["User"] = relationship(back_populates="project_users")
    project_role: Mapped["ProjectsRole"] = relationship(back_populates="project_users")


class TasksStatut(Base):
    __tablename__ = "Tasks_statuts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status_name: Mapped[str] = mapped_column(String(50), unique=True)
    tasks: Mapped[list["Task"]] = relationship(back_populates="status")


class TasksPriority(Base):
    __tablename__ = "Tasks_priority"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    priority_name: Mapped[str] = mapped_column(String(45), unique=True)
    tasks: Mapped[list["Task"]] = relationship(back_populates="priority")


class Task(Base):
    __tablename__ = "Tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("Projects.id"))
    task_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Text] = mapped_column(Text, nullable=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"), nullable=True)
    status_id: Mapped[int] = mapped_column(ForeignKey("Tasks_statuts.id"), default=3)
    priority_id: Mapped[int] = mapped_column(ForeignKey("Tasks_priority.id"), default=3)
    deadline: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=True)
    creation_date: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.utcnow
    )
    last_update: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, nullable=True, onupdate=datetime.datetime.utcnow
    )
    delete_date: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, nullable=True)

    project: Mapped["Project"] = relationship(back_populates="tasks")
    creator: Mapped["User"] = relationship(
        foreign_keys=[creator_id], back_populates="tasks_created"
    )
    assignee: Mapped["User"] = relationship(
        foreign_keys=[user_id], back_populates="tasks_assigned"
    )
    status: Mapped["TasksStatut"] = relationship(back_populates="tasks")
    priority: Mapped["TasksPriority"] = relationship(
        back_populates="tasks"
    )  
    comments: Mapped[list["TasksComment"]] = relationship(back_populates="task")


class TasksComment(Base):
    __tablename__ = "Tasks_comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("Tasks.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.id"))
    comment_text: Mapped[str] = mapped_column(String(500))
    comment_date: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, default=datetime.datetime.utcnow
    )
    comment_delete_date: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP, nullable=True, onupdate=datetime.datetime.utcnow
    )
    task: Mapped["Task"] = relationship(back_populates="comments")
    user: Mapped["User"] = relationship(back_populates="comments")
