import asyncio
from app.services import alpha_vantage_service
from pprint import pprint

async def main():
    """
    A simple async function to test the stock fetching service.
    """
    print("--- Testing Alpha Vantage API call for symbol: IBM ---")
    stock_data = await alpha_vantage_service.fetch_stock_overview("IBM")

    if stock_data and not stock_data.get("error"):
        print("--- SUCCESS: Data received from Alpha Vantage ---")
        pprint(stock_data)
    else:
        print("--- FAILURE: Could not retrieve data. ---")
        pprint(stock_data)

if __name__ == "__main__":
    asyncio.run(main())