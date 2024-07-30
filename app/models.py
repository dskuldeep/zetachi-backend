from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    mongo_collection = Column(String, nullable=False)
    company = Column(String, nullable=True)


class DocumentModel(Base):
    __tablename__ = 'documents'
    id = Column(String, unique=True, primary_key=True, index=True)
    collection = Column(String, nullable=False)