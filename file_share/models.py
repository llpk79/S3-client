from .database import Base
from flask_security import UserMixin, RoleMixin
# from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy import Boolean, Integer, DateTime, Column, String, ForeignKey


class RoleUser(Base):
    __tablename__ = 'RoleUser'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column('user_id', Integer(), ForeignKey('User.id'))
    role_id = Column('role_id', Integer(), ForeignKey('Role.id'))


class Role(Base, RoleMixin):
    __tablename__ = 'Role'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(80), unique=True)
    role = Column(String(255))


class User(Base, UserMixin):
    __tablename__ = 'User'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True)
    password = Column(String(255), nullable=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer())
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship('RoleUser')

    def user_payload(self):
        return {'id': self.id,
                'username': self.username,
                'email': self.email,
                'is_active': self.is_active,
                }


class Files(Base):
    __tablename__ = 'Files'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    upload_time = Column(DateTime())
    last_download = Column(DateTime())
    shared = Column(Boolean())
    owner_id = Column(Integer(), ForeignKey('User.id'), nullable=False)


class UserFiles(Base):
    __tablename__ = 'UserFiles'
    id = Column(Integer(), primary_key=True, autoincrement=True)
    user_id = Column('user_id', Integer(), ForeignKey('User.id'))
    file_id = Column('file_id', Integer(), ForeignKey('Files.id'))
