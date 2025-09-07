import os
import httpx
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

async def fetch_stock_overview(symbol: str):
    """
    Fetches company overview data for a given stock symbol from Alpha Vantage.
    """
    if not ALPHA_VANTAGE_API_KEY:
        return {"error": "API key for Alpha Vantage is not configured."}

    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": ALPHA_VANTAGE_API_KEY
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            # The free API often returns a 'Note' on usage limits. Check for an empty response.
            if not data or "Note" in data:
                 return {"error": "Failed to fetch data, possibly due to API rate limits."}
            return data
        except httpx.HTTPStatusError as e:
            return {"error": f"API request failed with status {e.response.status_code}"}
        except httpx.RequestError as e:
            return {"error": f"An error occurred while requesting {e.request.url!r}."}