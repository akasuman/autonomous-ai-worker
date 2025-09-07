from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    status = Column(String, default="processing")
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="task")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    source = Column(String)
    content = Column(JSON) # Store the raw JSON content of the article/data
    summary = Column(Text, nullable=True)
    topics = Column(Text, nullable=True) # New column to store extracted topics
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="documents")