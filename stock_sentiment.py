import os
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import argparse


def fetch_news(api_key: str, symbol: str, limit: int = 20):
    """Fetch recent news articles mentioning the symbol."""
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": symbol,
        "sortBy": "publishedAt",
        "pageSize": limit,
        "apiKey": api_key,
    }
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    articles = [
        (a.get("title", "") + ". " + (a.get("description") or "")).strip()
        for a in data.get("articles", [])
    ]
    return [a for a in articles if a]


def fetch_earnings(api_key: str, symbol: str):
    """Fetch recent annual earnings for the symbol."""
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "EARNINGS",
        "symbol": symbol,
        "apikey": api_key,
    }
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    return data.get("annualEarnings", [])


def fetch_overview(api_key: str, symbol: str):
    """Fetch company overview including book value."""
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "OVERVIEW",
        "symbol": symbol,
        "apikey": api_key,
    }
    resp = requests.get(url, params=params, timeout=10)
    return resp.json()


def sentiment_score(texts):
    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(t)["compound"] for t in texts]
    return sum(scores) / len(scores) if scores else 0.0


def classify(score: float) -> str:
    return "Bullish" if score > 0 else "Non-bullish"


def scan_symbol(symbol: str, news_key: str, alpha_key: str):
    news_items = fetch_news(news_key, symbol)
    score = sentiment_score(news_items)
    earnings = fetch_earnings(alpha_key, symbol)
    overview = fetch_overview(alpha_key, symbol)
    latest_earnings = earnings[0] if earnings else {}
    return {
        "symbol": symbol,
        "sentiment_score": score,
        "sentiment_class": classify(score),
        "book_value": overview.get("BookValue"),
        "latest_earnings": latest_earnings,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Simple stock market sentiment analyzer"
    )
    parser.add_argument("tickers", nargs="+", help="Ticker symbols to analyze")
    parser.add_argument(
        "--news-key",
        default=os.getenv("NEWS_API_KEY"),
        help="NewsAPI key (or set NEWS_API_KEY)",
    )
    parser.add_argument(
        "--alpha-key",
        default=os.getenv("ALPHAVANTAGE_KEY"),
        help="Alpha Vantage key (or set ALPHAVANTAGE_KEY)",
    )
    args = parser.parse_args()

    if not args.news_key or not args.alpha_key:
        parser.error("Both NewsAPI and Alpha Vantage API keys are required.")

    for symbol in args.tickers:
        info = scan_symbol(symbol, args.news_key, args.alpha_key)
        print(f"{info['symbol']}: {info['sentiment_class']} ({info['sentiment_score']:.3f})")
        if info["book_value"]:
            print(f"  Book value: {info['book_value']}")
        le = info["latest_earnings"]
        if le:
            print(
                f"  Latest annual earnings: {le.get('reportedEPS', 'N/A')} on {le.get('fiscalDateEnding', 'N/A')}"
            )


if __name__ == "__main__":
    main()
