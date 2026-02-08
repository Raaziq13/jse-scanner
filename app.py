import streamlit as st
import yfinance as yf
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Ensure the sentiment engine is ready
nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

st.title("🇿🇦 SA Strategic Trader Dashboard")

# Sidebar for User Input
ticker = st.sidebar.text_input("Enter Ticker (e.g., NPN.JO or BTC-USD)", value="NPN.JO")

# 1. Fetch Market Data
data = yf.Ticker(ticker)
hist = data.history(period="1mo")

# 2. Fetch & Analyze News
st.subheader(f"Strategic Analysis for {ticker}")
news = data.news
sentiment_scores = []

for article in news[:5]: # Analyze top 5 recent stories
    score = sia.polarity_scores(article['title'])['compound']
    sentiment_scores.append(score)
    st.write(f"📰 {article['title']} | **Score: {score}**")

# 3. Final Recommendation Logic
avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
last_price = hist['Close'].iloc[-1]

st.divider()
if avg_sentiment > 0.2:
    st.success(f"STRATEGIC RECOMMENDATION: BULLISH (Sentiment: {avg_sentiment:.2f})")
elif avg_sentiment < -0.2:
    st.error(f"STRATEGIC RECOMMENDATION: BEARISH (Sentiment: {avg_sentiment:.2f})")
else:
    st.warning("STRATEGIC RECOMMENDATION: NEUTRAL")

st.metric("Latest Price", f"R{last_price:.2f}")
