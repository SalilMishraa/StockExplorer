import streamlit as st
import requests
import pandas as pd

# Alpha Vantage API key
API_KEY = "HA68S2F46ZB94J6E"

# NewsAPI key
NEWS_API_KEY = "59fc0b6559b541a7a40e87c7efbed402"

# Stock symbol mapping
stock_symbols = {
    "Microsoft Corporation": "MSFT",
    "Apple Inc.": "AAPL",
    "NVIDIA Corporation": "NVDA",
    "Amazon.com Inc.": "AMZN",
    "Alphabet Inc.": "GOOGL",
    "Meta Platforms Inc.": "META",
    "Tesla Inc.": "TSLA",
    "UnitedHealth Group Inc.": "UNH",
    "Johnson & Johnson": "JNJ"
}

# Title
st.title("📈 Real-Time US Stock Explorer & News Summarizer")
st.write("This app displays near real-time stock prices and top market news.")

# Filters
search_symbol = st.text_input(" Search by Stock Symbol (e.g., AAPL, TSLA)", "").upper()
price_min = st.number_input(" Minimum Price", value=0.0)
price_max = st.number_input(" Maximum Price", value=1000.0)

# Get stock data
@st.cache_data(ttl=300)
def get_stock_data(symbol):
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    try:
        time_series = data["Time Series (5min)"]
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index(ascending=False)
        return df
    except KeyError:
        return None

# Display stock data
st.header("Stock Data")
for name, symbol in stock_symbols.items():
    if search_symbol and search_symbol != symbol:
        continue
    stock_data = get_stock_data(symbol)
    if stock_data is not None:
        latest_price = stock_data.iloc[0]["4. close"]
        if price_min <= latest_price <= price_max:
            st.subheader(f"{name} ({symbol})")
            st.write(f"Latest Price: **${latest_price:.2f}**")
            st.dataframe(stock_data.head())
    else:
        st.warning(f" Could not fetch data for {name} ({symbol})")

# Get news data
def get_market_news():
    url = (
        f"https://newsapi.org/v2/top-headlines?"
        f"category=business&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()
    if data.get("status") == "ok":
        return data.get("articles", [])
    else:
        return []

# Show news
st.header("Daily Stock Market News")
articles = get_market_news()
if articles:
    for article in articles:
        st.markdown(f"### [{article['title']}]({article['url']})")
        st.write(f"*{article['source']['name']} - {article['publishedAt'][:10]}*")
        if article["description"]:
            st.write(article["description"])
        st.write("---")
else:
    st.write("No news available at the moment.")
