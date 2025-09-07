import os
import httpx
import asyncio
import logging
from dotenv import load_dotenv
from functools import wraps

# --- 1. SETUP ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

MIN_ARTICLES_REQUIRED = 5

# --- 2. RETRY LOGIC DECORATOR ---
def retry_with_backoff(retries=3, backoff_in_seconds=1):
    """
    A decorator that retries a function call with exponential backoff if it fails.
    """
    def rwb(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            mtries, mdelay = retries, backoff_in_seconds
            while mtries > 1:
                try:
                    return await f(*args, **kwargs)
                except httpx.HTTPStatusError as e:
                    # Don't retry on client errors (4xx), only server errors (5xx)
                    if 400 <= e.response.status_code < 500:
                        logging.error(f"Client error {e.response.status_code} calling {f.__name__}. Not retrying.")
                        raise
                    msg = f"Server error {e.response.status_code}, Retrying in {mdelay} seconds..."
                    logging.warning(msg)
                    await asyncio.sleep(mdelay)
                    mtries -= 1
                    mdelay *= 2
            return await f(*args, **kwargs)
        return wrapper
    return rwb

# --- 3. MAPPING FUNCTIONS (to keep data consistent) ---
def _map_gnews_to_standard_format(articles):
    # (Same mapping function as before)
    return [{"title": a.get("title"), "description": a.get("description"), "url": a.get("url"), "urlToImage": a.get("image")} for a in articles]

def _map_newsdata_to_standard_format(articles):
    # New mapping function for NewsData.io's response format
    return [{"title": a.get("title"), "description": a.get("description"), "url": a.get("link"), "urlToImage": a.get("image_url")} for a in articles]

# --- 4. INDIVIDUAL API CALLS ---
@retry_with_backoff()
async def _fetch_from_gnews(topic: str, client: httpx.AsyncClient):
    if not GNEWS_API_KEY: return None
    url = "https://gnews.io/api/v4/search"
    params = {"q": topic, "apikey": GNEWS_API_KEY, "max": 10, "lang": "en"}
    response = await client.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return _map_gnews_to_standard_format(data.get("articles", []))

@retry_with_backoff()
async def _fetch_from_newsdata(topic: str, client: httpx.AsyncClient):
    if not NEWSDATA_API_KEY: return None
    url = "https://newsdata.io/api/1/news"
    params = {"q": topic, "apikey": NEWSDATA_API_KEY, "size": 10, "language": "en"}
    response = await client.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return _map_newsdata_to_standard_format(data.get("results", []))

# --- 5. MAIN ORCHESTRATOR FUNCTION ---
async def fetch_news_from_api(topic: str):
    """
    Fetches articles resiliently, trying a primary API and falling back to a secondary one.
    This is the only function that should be called from your main.py file.
    """
    async with httpx.AsyncClient() as client:
        # --- Try Primary API: GNews ---
        logging.info(f"Attempting to fetch articles for '{topic}' from primary source (GNews)...")
        try:
            articles = await _fetch_from_gnews(topic, client)
            if articles and len(articles) >= MIN_ARTICLES_REQUIRED:
                logging.info(f"Successfully fetched {len(articles)} articles from GNews.")
                return {"articles": articles}
            logging.warning(f"Primary source (GNews) returned only {len(articles) if articles else 0} articles. Falling back to secondary source.")
        except Exception as e:
            logging.error(f"Primary source (GNews) failed: {e}. Falling back to secondary source.")

        # --- Fallback to Secondary API: NewsData.io ---
        logging.info(f"Attempting to fetch articles for '{topic}' from secondary source (NewsData.io)...")
        try:
            articles = await _fetch_from_newsdata(topic, client)
            if articles and len(articles) >= MIN_ARTICLES_REQUIRED:
                logging.info(f"Successfully fetched {len(articles)} articles from NewsData.io.")
                return {"articles": articles}
            logging.warning(f"Secondary source (NewsData.io) also returned only {len(articles) if articles else 0} articles.")
        except Exception as e:
            logging.error(f"Secondary source (NewsData.io) failed: {e}.")

    # --- If both fail ---
    logging.error(f"All sources failed to provide at least {MIN_ARTICLES_REQUIRED} articles for '{topic}'.")
    return {"error": f"Could not retrieve sufficient news for '{topic}'. Please try another search."}