import os
import httpx
import asyncio
import logging
from dotenv import load_dotenv
from functools import wraps
import feedparser

# --- 1. SETUP ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")

MIN_ARTICLES_REQUIRED = 3

RSS_FEEDS = {
    "Reuters World News": "http://feeds.reuters.com/reuters/worldNews",
    "New York Times": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "The Times of India": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms", # India News
    "The Hindu - Karnataka": "https://www.thehindu.com/news/national/karnataka/feeder/default.xml" # Karnataka News
}

# --- 2. RETRY LOGIC DECORATOR (Unchanged) ---
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

# --- 3. MAPPING FUNCTIONS (Unchanged) ---
def _map_gnews_to_standard_format(articles):
    return [{"title": a.get("title"), "description": a.get("description"), "url": a.get("url"), "urlToImage": a.get("image")} for a in articles]

def _map_newsdata_to_standard_format(articles):
    return [{"title": a.get("title"), "description": a.get("description"), "url": a.get("link"), "urlToImage": a.get("image_url")} for a in articles]

def _map_rss_to_standard_format(entries):
    formatted_articles = []
    for entry in entries:
        image_url = None
        if 'media_content' in entry and entry.media_content:
            image_url = entry.media_content[0]['url']
        
        formatted_articles.append({
            "title": entry.get("title"),
            "description": entry.get("summary"),
            "url": entry.get("link"),
            "urlToImage": image_url
        })
    return formatted_articles

# --- 4. INDIVIDUAL API CALLS (with updated RSS function) ---
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

# --- MODIFIED: The RSS fetcher now accepts a topic and filters the results ---
async def _fetch_from_rss(topic: str):
    all_entries = []
    for name, url in RSS_FEEDS.items():
        try:
            logging.info(f"Parsing RSS feed: {name}")
            feed = feedparser.parse(url)
            all_entries.extend(feed.entries)
        except Exception as e:
            logging.error(f"Failed to parse RSS feed {name}: {e}")
            
    # Filter the collected entries to find ones that match the topic
    topic_lower = topic.lower()
    filtered_entries = [
        entry for entry in all_entries 
        if topic_lower in entry.get('title', '').lower() 
        or topic_lower in entry.get('summary', '').lower()
    ]
    
    return _map_rss_to_standard_format(filtered_entries)

# --- 5. UPDATED: Main orchestrator function with filtered RSS fallback ---
async def fetch_news_from_api(topic: str):
    """
    Fetches articles resiliently, trying a primary, secondary, and finally RSS feeds.
    """
    async with httpx.AsyncClient() as client:
        # --- Try Primary API: GNews ---
        logging.info(f"Attempting to fetch articles for '{topic}' from primary source (GNews)...")
        try:
            articles = await _fetch_from_gnews(topic, client)
            if articles and len(articles) >= MIN_ARTICLES_REQUIRED:
                logging.info(f"Successfully fetched {len(articles)} articles from GNews.")
                return {"articles": articles}
            logging.warning(f"Primary source returned only {len(articles) if articles else 0} articles. Falling back.")
        except Exception as e:
            logging.error(f"Primary source failed: {e}. Falling back.")

        # --- Fallback to Secondary API: NewsData.io ---
        logging.info(f"Attempting to fetch articles for '{topic}' from secondary source (NewsData.io)...")
        try:
            articles = await _fetch_from_newsdata(topic, client)
            if articles and len(articles) >= MIN_ARTICLES_REQUIRED:
                logging.info(f"Successfully fetched {len(articles)} articles from NewsData.io.")
                return {"articles": articles}
            logging.warning(f"Secondary source returned only {len(articles) if articles else 0} articles. Falling back to RSS.")
        except Exception as e:
            logging.error(f"Secondary source failed: {e}. Falling back to RSS.")
            
        # --- MODIFIED: The call to the RSS function now passes the topic ---
        logging.info("Attempting to fetch articles from tertiary source (RSS Feeds)...")
        try:
            articles = await _fetch_from_rss(topic)
            if articles:
                logging.info(f"Successfully fetched {len(articles)} articles from RSS feeds.")
                return {"articles": articles}
        except Exception as e:
            logging.error(f"Tertiary source (RSS) failed: {e}.")

    # --- If all sources fail ---
    logging.error(f"All sources failed to provide sufficient articles for '{topic}'.")
    return {"error": f"Could not retrieve sufficient news for '{topic}'. Please try another search."}