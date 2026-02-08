import streamlit as st
import yfinance as yf
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import os

# --- 1. SETUP & CLOUD FIX ---
# This ensures NLTK works on your computer AND on Streamlit Cloud
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

sia = SentimentIntensityAnalyzer()

st.set_page_config(page_title="SA Strategic Trader", page_icon="🇿🇦")
st.title("🇿🇦 SA Strategic Trader Dashboard")
st.markdown("Analyzing JSE & Crypto trends using News Sentiment + Price Action.")

# --- 2. SIDEBAR INPUTS ---
ticker = st.sidebar.text_input("Enter Ticker (e.g., NPN.JO, CPI.JO, or BTC-USD)", value="NPN.JO")
period = st.sidebar.selectbox("Select Analysis Period", ["1mo", "3mo", "6mo", "1y"])

# --- 3. FETCH MARKET DATA ---
@st.cache_data # This makes the app faster by "remembering" data
def get_data(symbol, time_p):
    d = yf.Ticker(symbol)
    h = d.history(period=time_p)
    return d, h

ticker_obj, hist = get_data(ticker, period)

if hist.empty:
    st.error("Could not find data for that ticker. Please check the symbol.")
else:
    # Calculate 20-day Moving Average (Trend Indicator)
    hist['MA20'] = hist['Close'].rolling(window=20).mean()
    last_price = hist['Close'].iloc[-1]
    last_ma20 = hist['MA20'].iloc[-1]
    
    # --- 4. NEWS & SENTIMENT ---
    st.subheader(f"Strategic Analysis: {ticker}")
    news = ticker_obj.news
    avg_sentiment = 0

    if not news:
        st.info("No recent news found for this specific ticker.")
    else:
        sentiment_scores = []
        for article in news[:5]:
            score = sia.polarity_scores(article['title'])['compound']
            sentiment_scores.append(score)
            st.write(f"📰 {article['title']} (Score: {score})")
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

    # --- 5. STRATEGIC LOGIC ---
    st.divider()
    
    # Logic: Price > MA20 (Positive Trend) AND Sentiment > 0.1 (Positive News)
    is_bullish_trend = last_price > last_ma20
    is_positive_news = avg_sentiment > 0.1
    
    if is_bullish_trend and is_positive_news:
        st.success("🎯 STRATEGIC RECOMMENDATION: STRONG BUY (Positive Trend + Positive News)")
    elif is_bullish_trend:
        st.info("📈 STRATEGIC RECOMMENDATION: HOLD (Positive Trend, but Neutral News)")
    elif is_positive_news:
        st.warning("⚖️ STRATEGIC RECOMMENDATION: WATCH (Good News, but Price is in a Downtrend)")
    else:
        st.error("⚠️ STRATEGIC RECOMMENDATION: CAUTION (Negative Trend/News)")

    # --- 6. VISUALS ---
    col1, col2 = st.columns(2)
    col1.metric("Current Price", f"R{last_price:.2f}")
    col2.metric("20-Day Average", f"R{last_ma20:.2f}")

    st.line_chart(hist[['Close', 'MA20']])
