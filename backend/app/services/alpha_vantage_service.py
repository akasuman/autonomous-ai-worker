import yfinance as yf
from pprint import pprint

# This dictionary maps the keys from the yfinance 'info' object
# to the keys your frontend expects (which were based on Alpha Vantage).
YFINANCE_TO_AV_MAP = {
    'symbol': 'Symbol',
    'longName': 'Name',
    'longBusinessSummary': 'Description',
    'assetType': 'AssetType',
    'exchange': 'Exchange',
    'currency': 'Currency',
    'country': 'Country',
    'sector': 'Sector',
    'industry': 'Industry',
    'website': 'OfficialSite',
    'marketCap': 'MarketCapitalization',
    'trailingPE': 'PERatio',
    'pegRatio': 'PEGRatio',
    'bookValue': 'BookValue',
    'dividendRate': 'DividendPerShare',
    'dividendYield': 'DividendYield',
    'trailingEps': 'EPS',
    'profitMargins': 'ProfitMargin',
    'returnOnAssets': 'ReturnOnAssetsTTM',
    'returnOnEquity': 'ReturnOnEquityTTM',
    'revenuePerShare': 'RevenuePerShareTTM',
    'ebitda': 'EBITDA',
    'beta': 'Beta',
    'fiftyTwoWeekHigh': '52WeekHigh',
    'fiftyTwoWeekLow': '52WeekLow',
    'fiftyDayAverage': '50DayMovingAverage',
    'twoHundredDayAverage': '200DayMovingAverage',
    'sharesOutstanding': 'SharesOutstanding',
    'floatShares': 'SharesFloat',
    'heldPercentInsiders': 'PercentInsiders',
    'heldPercentInstitutions': 'PercentInstitutions',
    'dividendDate': 'DividendDate',
    'exDividendDate': 'ExDividendDate'
}

async def fetch_stock_overview(symbol: str):
    """
    Fetches a company overview from Yahoo Finance using the yfinance library
    and maps it to the format expected by the frontend.
    """
    try:
        ticker = yf.Ticker(symbol)
        stock_info = ticker.info

        # Make the validation check more reliable
        if not stock_info or stock_info.get('symbol', '').upper() != symbol.upper():
            # For indices, the symbol might not match exactly (e.g., ^NSEI vs NSEI)
            if symbol.startswith('^') and stock_info.get('quoteType') == 'INDEX':
                pass # It's a valid index, so we can proceed
            else:
                return {"error": f"Invalid or unsupported stock symbol: {symbol}"}

        # Create a new dictionary with the keys our frontend expects
        formatted_data = {}
        for yf_key, av_key in YFINANCE_TO_AV_MAP.items():
            value = stock_info.get(yf_key)
            if value is not None:
                if yf_key in ['dividendDate', 'exDividendDate'] and isinstance(value, int):
                    from datetime import datetime
                    formatted_data[av_key] = datetime.fromtimestamp(value).strftime('%Y-%m-%d')
                else:
                    formatted_data[av_key] = value
        
        if 'Symbol' not in formatted_data:
            formatted_data['Symbol'] = symbol.upper()

        return formatted_data

    except Exception as e:
        print(f"An error occurred while fetching data from yfinance: {e}")
        return {"error": f"An unexpected error occurred for symbol: {symbol}"}

# --- ADDED: New function to fetch historical data for the chart ---
async def fetch_stock_history(symbol: str):
    """
    Fetches the last year of stock history for a given symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        # Get historical data for the past year
        history = ticker.history(period="1y")

        if history.empty:
            return {"error": f"No historical data found for symbol: {symbol}"}
        
        # Reset index to make 'Date' a column and format it
        history.reset_index(inplace=True)
        history['Date'] = history['Date'].dt.strftime('%Y-%m-%d')
        
        # Convert the data to a list of dictionaries for easy use in the frontend
        return history[['Date', 'Close']].to_dict('records')

    except Exception as e:
        print(f"An error occurred while fetching history from yfinance: {e}")
        return {"error": "An unexpected error occurred while fetching history."}