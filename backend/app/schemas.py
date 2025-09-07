from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# This is the Pydantic model for a Document
class Document(BaseModel):
    id: int
    source: str
    summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# This is the Pydantic model for a Task
class Task(BaseModel):
    id: int
    topic: str
    status: str
    created_at: datetime
    documents: List[Document] = []

    class Config:
        from_attributes = True