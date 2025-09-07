from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from . import crud, models, schemas
from .database import engine, get_db, SessionLocal
from .services import ai_service, vector_db_service, news_service

models.Base.metadata.create_all(bind=engine)

async def daily_research_job():
    print("--- SCHEDULER: Running daily research job for topic 'artificial intelligence' ---")
    db = SessionLocal()
    try:
        # Note: The scheduled job logic needs refactoring to work correctly
        # outside of an HTTP request that provides the 'db' dependency.
        print("--- SCHEDULER: Daily research job logic needs refactoring. ---")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    # Disabling the job as it will fail without refactoring the search_news function.
    # scheduler.add_job(daily_research_job, CronTrigger(hour=9, minute=0))
    scheduler.start()
    print("--- SCHEDULER: Scheduler started. Daily job is currently disabled. ---")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/api/tasks", response_model=List[schemas.Task])
def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db, skip=skip, limit=limit)
    return tasks

@app.get("/api/tasks/{task_id}")
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.documents:
        content = db_task.documents[0].content
        if content and db_task.documents[0].topics:
            content["articles"][0]["topics"] = db_task.documents[0].topics
        return content
    return {"articles": []}

@app.delete("/api/tasks/{task_id}")
def delete_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.delete_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}

@app.get("/api/search/history")
def search_history(q: str):
    search_results = vector_db_service.search_similar_documents(query_text=q)
    return search_results

@app.get("/api/analytics/stats")
def get_analytics_stats(db: Session = Depends(get_db)):
    stats = crud.get_db_stats(db)
    return stats

@app.get("/api/search/{topic}")
async def search_news(topic: str, db: Session = Depends(get_db)):
    task = crud.create_task(db=db, topic=topic)
    news_data = await news_service.fetch_news_from_api(topic)

    if news_data and not news_data.get("error") and news_data.get("articles"):
        
        original_articles = news_data.get("articles", [])
        articles_to_process = original_articles[:3]

        if articles_to_process:
            processed_top_articles = await ai_service.process_articles_concurrently(articles_to_process)
            remaining_articles = original_articles[3:]
            news_data["articles"] = processed_top_articles + remaining_articles

        document = crud.create_document(db=db, task_id=task.id, source="GNews", content=news_data)

        processed_articles = news_data.get("articles", [])
        if processed_articles:
            first_article = processed_articles[0]
            if first_article.get("summary"):
                crud.update_document_summary(db=db, document_id=document.id, summary=first_article["summary"])
            if first_article.get("topics"):
                crud.update_document_topics(db=db, document_id=document.id, topics=first_article["topics"])

            # Use 'description' as a fallback for adding to the vector DB
            text_for_vector_db = first_article.get("content") or first_article.get("description")
            if text_for_vector_db:
                metadata = {"task_id": task.id, "document_id": document.id, "source": "GNews", "title": first_article.get("title"), "url": first_article.get("url")}
                vector_db_service.add_document_to_vector_db(document_id=document.id, text=text_for_vector_db, metadata=metadata)
            
    return news_data

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str):
    # This endpoint seems to be missing dependencies and imports from previous context
    return {"error": "Stock data service not fully implemented in provided code."}

@app.post("/api/upload")
async def upload_document(file: UploadFile):
    return {"filename": file.filename, "content_type": file.content_type}