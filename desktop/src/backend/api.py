"""
cd src/backend
uvicorn api:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

app = FastAPI()

# Allow your React dev server to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or "*" for dev
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/search/{query}")
def search_stocks(query: str):
    search = yf.Search(query, max_results=10)
    
    results = []
    for quote in search.quotes:
        results.append({
            "symbol": quote.get("symbol"),
            "name": quote.get("shortname") or quote.get("longname"),
            "exchange": quote.get("exchange"),
            "type": quote.get("quoteType"),
        })
    
    return {"query": query, "results": results}

@app.get("/api/stock/{ticker}")
def get_stock(ticker: str):
    stock = yf.Ticker(ticker)
    info = stock.info
    history = stock.history(period="1mo")
    history = history.reset_index()
    history["Date"] = history["Date"].dt.strftime("%Y-%m-%d")
    return {
        "symbol": ticker,
        "price": info.get("currentPrice"),
        "name": info.get("longName"),
        "history": history.reset_index().to_dict(orient="records"),
        "info": info,
    }

@app.get("/api/news/{ticker}")
def get_news(ticker: str):
    stock = yf.Ticker(ticker)
    news = stock.get_news()
    print(news)
    return {"articles": news}