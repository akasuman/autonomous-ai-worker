from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

# --- Document Schemas ---
# Used as a base to avoid repetition
class DocumentBase(BaseModel):
    source: str
    summary: Optional[str] = None
    topics: Optional[str] = None
    content: dict[str, Any]

# Schema for reading a document from the database
class Document(DocumentBase):
    id: int
    task_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Task Schemas ---
# Used as a base to avoid repetition
class TaskBase(BaseModel):
    topic: str

# Schema for reading a basic task (e.g., in a list)
class Task(TaskBase):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- SOLVED: This is the missing TaskDetails schema ---
# For reading a single task WITH its list of documents.
class TaskDetails(Task):
    documents: List[Document] = []