from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from . import models

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Task).order_by(models.Task.id.desc()).offset(skip).limit(limit).all()

def create_task(db: Session, topic: str):
    db_task = models.Task(topic=topic, status="processing")
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.query(models.Document).filter(models.Document.task_id == task_id).delete(synchronize_session=False)
        db.delete(db_task)
        db.commit()
        return db_task
    return None

def create_document(db: Session, task_id: int, source: str, content: dict):
    db_document = models.Document(task_id=task_id, source=source, content=content)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def update_document_summary(db: Session, document_id: int, summary: str):
    db_document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if db_document:
        db_document.summary = summary
        db.commit()
        db.refresh(db_document)
        return db_document

def update_document_topics(db: Session, document_id: int, topics: str):
    db_document = db.query(models.Document).filter(models.Document.id == document_id).first()
    if db_document:
        db_document.topics = topics
        db.commit()
        db.refresh(db_document)
        return db_document
        
def get_db_stats(db: Session):
    total_tasks = db.query(models.Task).count()
    total_documents = db.query(models.Document).count()
    
    top_topics = db.query(models.Task.topic, func.count(models.Task.topic).label('count')) \
                     .group_by(models.Task.topic) \
                     .order_by(func.count(models.Task.topic).desc()) \
                     .limit(5).all()
                     
    return {
        "total_tasks": total_tasks,
        "total_documents": total_documents,
        "top_topics": [{"topic": topic, "count": count} for topic, count in top_topics]
    }

# --- ADDED: New function to find documents by their URLs ---
def get_existing_document_urls(db: Session, urls: List[str]) -> List[str]:
    """
    Checks the database for a list of article URLs and returns the ones that already exist.
    The 'url' is inside the 'content' JSON field.
    """
    if not urls:
        return []
    
    # Corrected syntax using .as_string() instead of .astext
    existing_docs = db.query(models.Document.content['url'].as_string()).filter(
        models.Document.content['url'].as_string().in_(urls)
    ).all()
    
    # The result is a list of tuples, e.g., [('http://url1',), ('http://url2',)], so we flatten it.
    return [url for url, in existing_docs]