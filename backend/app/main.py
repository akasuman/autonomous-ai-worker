from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from . import crud, models, schemas
from .database import engine, get_db, SessionLocal
from .services import ai_service, vector_db_service, news_service, alpha_vantage_service

models.Base.metadata.create_all(bind=engine)

# --- CHANGE 1 of 3: The core logic is moved to its own function ---
async def run_research_task(topic: str, db: Session):
    """
    This function contains the core logic for fetching, processing,
    and saving news articles. It can be called from anywhere.
    """
    task = crud.create_task(db=db, topic=topic)
    news_data = await news_service.fetch_news_from_api(topic)

    if news_data and not news_data.get("error") and news_data.get("articles"):
        original_articles = news_data.get("articles", [])
        if not original_articles:
            return news_data

        urls_to_check = [article['url'] for article in original_articles]
        existing_urls = crud.get_existing_document_urls(db, urls=urls_to_check)
        
        new_articles = [article for article in original_articles if article['url'] not in existing_urls]
        
        if not new_articles:
            print(f"--- All fetched articles for '{topic}' are duplicates. ---")
            return news_data
            
        news_data["articles"] = new_articles
        articles_to_process = new_articles[:6]

        if articles_to_process:
            processed_top_articles = await ai_service.process_articles_concurrently(articles_to_process)
            remaining_articles = new_articles[6:]
            news_data["articles"] = processed_top_articles + remaining_articles

        document = crud.create_document(db=db, task_id=task.id, source="GNews", content=news_data)

        processed_articles = news_data.get("articles", [])
        if processed_articles:
            first_article = processed_articles[0]
            if first_article.get("summary"):
                crud.update_document_summary(db=db, document_id=document.id, summary=first_article["summary"])
            if first_article.get("topics"):
                crud.update_document_topics(db=db, document_id=document.id, topics=first_article["topics"])

            text_for_vector_db = first_article.get("content") or first_article.get("description")
            if text_for_vector_db:
                metadata = {"task_id": task.id, "document_id": document.id, "source": "GNews", "title": first_article.get("title"), "url": first_article.get("url")}
                vector_db_service.add_document_to_vector_db(document_id=document.id, text=text_for_vector_db, metadata=metadata)
            
    return news_data

async def daily_research_job():
    print("--- SCHEDULER: Running daily research job for topic 'artificial intelligence' ---")
    db = SessionLocal()
    try:
        # --- CHANGE 2 of 3: The job now calls the new logic function ---
        await run_research_task(topic="artificial intelligence", db=db)
        print("--- SCHEDULER: Daily research job completed successfully. ---")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
    # --- CHANGE 3 of 3: Re-enable the scheduled job ---
    # This now runs the `daily_research_job` every day at 9:00 AM server time.
    scheduler.add_job(daily_research_job, CronTrigger(hour=9, minute=0))
    scheduler.start()
    print("--- SCHEDULER: Scheduler started. Daily job is scheduled for 9:00 AM. ---")
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:3000",
    "https://autonomous-ai-worker-lr4u-m7v6p5x6-sumans-projects.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
    # The endpoint now simply calls the shared core logic function
    return await run_research_task(topic=topic, db=db)

@app.get("/api/stock/{symbol}")
async def get_stock_data(symbol: str):
    stock_data = await alpha_vantage_service.fetch_stock_overview(symbol)
    if stock_data and stock_data.get("error"):
        raise HTTPException(status_code=404, detail=stock_data["error"])
    return stock_data

@app.get("/api/stock/{symbol}/history")
async def get_stock_history(symbol: str):
    history_data = await alpha_vantage_service.fetch_stock_history(symbol)
    if isinstance(history_data, dict) and history_data.get("error"):
        raise HTTPException(status_code=404, detail=history_data["error"])
    return history_data

@app.post("/api/upload")
async def upload_document(file: UploadFile):
    return {"filename": file.filename, "content_type": file.content_type}