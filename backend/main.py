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
        await search_news(topic="artificial intelligence", db=db)
        print("--- SCHEDULER: Daily research job completed successfully. ---")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(daily_research_job, CronTrigger(hour=9, minute=0))
    scheduler.start()
    print("--- SCHEDULER: Scheduler started. Daily job scheduled for 9:00 AM. ---")
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
        
        # --- PERFORMANCE UPGRADE ---
        processed_articles = await ai_service.process_articles_concurrently(news_data["articles"])
        news_data["articles"] = processed_articles
        # --- END UPGRADE ---

        document = crud.create_document(db=db, task_id=task.id, source="NewsAPI", content=news_data)

        if processed_articles:
            first_article = processed_articles[0]
            if first_article.get("summary"):
                crud.update_document_summary(db=db, document_id=document.id, summary=first_article["summary"])
            if first_article.get("topics"):
                crud.update_document_topics(db=db, document_id=document.id, topics=first_article["topics"])

            if first_article.get("content"):
                 metadata = {"task_id": task.id, "document_id": document.id, "source": "NewsAPI", "title": first_article.get("title"), "url": first_article.get("url")}
                 vector_db_service.add_document_to_vector_db(document_id=document.id, text=first_article["content"], metadata=metadata)
            
    return news_data

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str, db: Session = Depends(get_db)):
    stock_data = await fetch_stock_overview(symbol)
    return stock_data

@app.post("/api/upload")
async def upload_document(file: UploadFile):
    return {"filename": file.filename, "content_type": file.content_type}