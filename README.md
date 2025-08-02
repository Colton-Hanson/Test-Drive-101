# Test-Drive-101

This is my first repo to test functionality and scripts.

## Stock sentiment tool

`stock_sentiment.py` is a small utility that classifies stocks as **bullish** or **non-bullish** based on recent news. It also pulls basic fundamentals such as book value and latest earnings from Alpha Vantage.

### Setup

1. Install dependencies:
   ```bash
   pip install requests vaderSentiment
   ```
2. Create API keys:
   * [NewsAPI](https://newsapi.org/)
   * [Alpha Vantage](https://www.alphavantage.co/)
3. Export the keys:
   ```bash
   export NEWS_API_KEY="<your-newsapi-key>"
   export ALPHAVANTAGE_KEY="<your-alpha-vantage-key>"
   ```

### Usage

Analyze one or more tickers:

```bash
python stock_sentiment.py AAPL MSFT
```

The script prints a sentiment classification and displays book value and latest annual earnings if available.
