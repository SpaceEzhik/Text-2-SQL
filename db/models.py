from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(45), unique=True, nullable=False)
    password = Column(String(60), nullable=False)
    user_group = Column(String(45), nullable=False)
    refresh_token = Column(Text, nullable=True)
    is_active = Column(Boolean, default=False)
