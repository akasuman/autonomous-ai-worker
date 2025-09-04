import os
import httpx
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

async def fetch_news_from_api(topic: str):
    """
    Fetches news articles related to a specific topic from the NewsAPI,
    prioritizing English language results.
    """
    if not NEWS_API_KEY:
        return {"error": "API key for NewsAPI is not configured."}

    params = {
        "q": topic,
        "apiKey": NEWS_API_KEY,
        "sortBy": "relevancy",
        "language": "en",  # This is the new parameter to specify English
        "pageSize": 20
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"API request failed with status {e.response.status_code}"}
        except httpx.RequestError as e:
            return {"error": f"An error occurred while requesting {e.request.url!r}."}