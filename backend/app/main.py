from fastapi import FastAPI, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from . import crud, models, schemas
from .database import engine, get_db, SessionLocal
from .services import ai_service, news_service, alpha_vantage_service

models.Base.metadata.create_all(bind=engine)


async def run_research_task(topic: str, db: Session):
    """
    This function now correctly processes and saves EACH news article
    to the database individually.
    """
    task = crud.create_task(db=db, topic=topic)
    news_data = await news_service.fetch_news_from_api(topic)
    
    # --- FIX: Extract the 'articles' list from the API response object ---
    articles_list = news_data.get("articles", [])

    if not articles_list:
        return {"articles": []}

    # Now, use the correct 'articles_list' for all subsequent operations
    urls_to_check = [article['url'] for article in articles_list]
    existing_urls = crud.get_existing_document_urls(db, urls=urls_to_check)
    
    new_articles = [article for article in articles_list if article['url'] not in existing_urls]
    
    if not new_articles:
        print(f"--- All fetched articles for '{topic}' are duplicates. Returning existing task data. ---")
        # You might want to return the existing task or documents here
        return task

    # Process new articles with the AI service to get summaries and topics
    # Let's process a smaller number to avoid long waits, e.g., the first 5
    articles_to_process = new_articles[:2]
    processed_articles = await ai_service.process_articles_concurrently(articles_to_process)

    # Loop through each processed article and save it individually
    for article in processed_articles:
        # 1. Create a unique document record for this article
        document = crud.create_document(
            db=db,
            task_id=task.id,
            source=article.get('source', {}).get('name', 'Unknown'),
            content={
                'title': article.get('title'),
                'url': article.get('url'),
                'description': article.get('description'),
                'image': article.get('image')
            }
        )

        # 2. If a summary was generated, save it to the document's 'summary' field
        if article.get("summary"):
            crud.update_document_summary(
                db=db,
                document_id=document.id,
                summary=article["summary"]
            )
        
        # 3. If topics were generated, save them to the document's 'topics' field
        if article.get("topics"):
            crud.update_document_topics(
                db=db,
                document_id=document.id,
                topics=article["topics"]
            )
    
    # Return the newly processed articles to the frontend
    return {"articles": processed_articles}


async def daily_research_job():
    print("--- SCHEDULER: Running daily research job for topic 'artificial intelligence' ---")
    db = SessionLocal()
    try:
        await run_research_task(topic="artificial intelligence", db=db)
        print("--- SCHEDULER: Daily research job completed successfully. ---")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler()
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

@app.get("/api/tasks/{task_id}", response_model=schemas.TaskDetails)
def read_task(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.delete("/api/tasks/{task_id}")
def delete_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.delete_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"ok": True}

@app.get("/api/search/history", response_model=List[schemas.Document])
def search_history(q: str, db: Session = Depends(get_db)):
    """
    Searches the database for documents containing the query text in their summary.
    """
    search_results = crud.search_documents_by_text(db=db, query=q)
    return search_results

@app.get("/api/analytics/stats")
def get_analytics_stats(db: Session = Depends(get_db)):
    stats = crud.get_db_stats(db)
    return stats

@app.get("/api/search/{topic}")
async def search_news(topic: str, db: Session = Depends(get_db)):
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