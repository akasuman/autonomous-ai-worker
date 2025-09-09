import os
import httpx
import asyncio
from dotenv import load_dotenv
from textblob import TextBlob
from typing import List, Dict

load_dotenv()

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
TIMEOUT = httpx.Timeout(20.0) # Reduced timeout

SUMMARIZATION_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

async def _call_summarizer(client: httpx.AsyncClient, text: str):
    """Helper function to call the summarization API with detailed logging."""
    try:
        if not HUGGINGFACE_TOKEN:
            print("Summarization failed: HUGGINGFACE_TOKEN not set.")
            return None
            
        response = await client.post(
            SUMMARIZATION_URL, headers=HEADERS, json={"inputs": text}, timeout=TIMEOUT
        )
        response.raise_for_status()
        result = response.json()
        
        if isinstance(result, dict) and result.get("error"):
            print(f"Summarization API returned an error: {result['error']}")
            return None

        return result[0].get("summary_text")

    except httpx.HTTPStatusError as e:
        print(f"Summarization API call failed with status {e.response.status_code}: {e.response.text}")
        return None
    except httpx.TimeoutException:
        print("Summarization API call timed out after 20 seconds.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during summarization: {e}")
        return None

async def _process_single_article(client: httpx.AsyncClient, article: Dict):
    """Processes a single article to add a summary and topics."""
    text_to_process = article.get("content") or article.get("description")
    if not text_to_process:
        return article

    summary = await _call_summarizer(client, text_to_process)
    if summary:
        article["summary"] = summary

    try:
        blob = TextBlob(text_to_process)
        topics = list(set([phrase.strip() for phrase in blob.noun_phrases]))[:3]
        article["topics"] = ", ".join(topics)
    except Exception as e:
        print(f"Topic extraction failed: {e}")
        article["topics"] = None
        
    return article

async def process_articles_concurrently(articles: List[Dict]) -> List[Dict]:
    """Processes a list of articles concurrently to generate summaries and topics."""
    async with httpx.AsyncClient() as client:
        tasks = [_process_single_article(client, article) for article in articles]
        processed_articles = await asyncio.gather(*tasks)
        return processed_articles