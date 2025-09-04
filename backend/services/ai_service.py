import os
import httpx
import asyncio
from dotenv import load_dotenv
from textblob import TextBlob
from typing import List, Dict

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
TIMEOUT = httpx.Timeout(90.0)

SUMMARIZATION_URL = "https://api-inference.huggingface.co/models/sshleifer/distilbart-cnn-12-6"

async def _call_summarizer(client: httpx.AsyncClient, text: str):
    """Helper function to call the summarization API."""
    try:
        response = await client.post(
            SUMMARIZATION_URL, headers=HEADERS, json={"inputs": text}, timeout=TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        return result[0].get("summary_text")
    except Exception as e:
        print(f"Summarization API call failed: {e}")
        return None

async def _process_single_article(client: httpx.AsyncClient, article: Dict):
    """Processes a single article to add a summary and topics."""
    content = article.get("content")
    if not content:
        return article # Return original article if no content

    # Step 1: Generate summary
    summary = await _call_summarizer(client, content)
    if summary:
        article["summary"] = summary

    # Step 2: Extract topics locally (this is fast)
    try:
        blob = TextBlob(content)
        topics = list(set([phrase.strip() for phrase in blob.noun_phrases]))[:5]
        article["topics"] = ", ".join(topics)
    except Exception as e:
        print(f"Topic extraction failed: {e}")
        article["topics"] = None
        
    return article

async def process_articles_concurrently(articles: List[Dict]) -> List[Dict]:
    """
    Processes a list of articles concurrently to generate summaries and topics.
    """
    async with httpx.AsyncClient() as client:
        tasks = [_process_single_article(client, article) for article in articles]
        processed_articles = await asyncio.gather(*tasks)
        return processed_articles