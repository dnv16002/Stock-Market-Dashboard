import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import pymongo
from news import get_stock_news

# ✅ MongoDB connection
client = pymongo.MongoClient(st.secrets["mongo"]["uri"])  # Use Streamlit secrets
db = client["stock_market_dashboard"]
wishlist_collection = db["wishlist"]  

# ✅ Fetch user wishlist from MongoDB
def get_wishlist(username):
    try:
        user_wishlist = wishlist_collection.find_one({"username": username})
        return user_wishlist["stocks"] if user_wishlist and "stocks" in user_wishlist else []
    except Exception as e:
        print("MongoDB Connection Error in get_wishlist:", e)
        return []

# ✅ Update wishlist in MongoDB
def update_wishlist(username, stocks):
    try:
        wishlist_collection.update_one(
            {"username": username},
            {"$set": {"stocks": stocks}},
            upsert=True
        )
    except Exception as e:
        print("MongoDB Connection Error in update_wishlist:", e)

# ✅ Fetch stock data for wishlist items
def get_wishlist_stock_data(wishlist):
    stock_data = {}
    for stock in wishlist:
        try:
            df = yf.Ticker(stock).history(period="1d", interval="1h")  # Today's hourly data
            if not df.empty:
                df.reset_index(inplace=True)
                df["Datetime"] = pd.to_datetime(df["Datetime"])
                stock_data[stock] = df[["Datetime", "Open", "High", "Low", "Close", "Volume"]]
        except Exception as e:
            print(f"Error fetching data for {stock}:", e)
    return stock_data

# ✅ Fetch news for wishlist stocks
def get_wishlist_news(wishlist):
    news_data = {}
    for stock in wishlist:
        try:
            news_articles = get_stock_news(stock)
            if news_articles:
                news_data[stock] = news_articles[:3]  
        except Exception as e:
            print(f"Error fetching news for {stock}:", e)
    return news_data

# ✅ Function to render wishlist page
def wishlist_page():
    st.title("\ud83c\udf1f Your Wishlist")

    username = st.session_state.get("username", "")
    wishlist = get_wishlist(username)

    if wishlist:
        # ✅ Show Stock Graphs
        stock_data = get_wishlist_stock_data(wishlist)
        for stock, df in stock_data.items():
            st.write(f"### \ud83d\udcc8 {stock} - Today's Trend")
            fig = px.line(df, x="Datetime", y="Close", title=f"{stock} - Stock Trend")
            st.plotly_chart(fig, use_container_width=True)

        # ✅ Display News Data
        news_data = get_wishlist_news(wishlist)
        for stock, articles in news_data.items():
            st.write(f"### \ud83d\udcf0 {stock} Latest News")
            for news in articles:
                st.write(f"\ud83d\udd39 [{news['headline']}]({news['url']})")

        # ✅ Remove stock from Wishlist
        for stock in wishlist:
            if st.button(f"\u274c Remove {stock}", key=f"remove_{stock}"):
                wishlist.remove(stock)
                update_wishlist(username, wishlist)
                st.rerun()

    else:
        st.info("Your wishlist is empty. Add stocks to track their latest updates!")

# ✅ Notification System for Stock Alerts
def stock_notifications():
    username = st.session_state.get("username", "")
    wishlist = get_wishlist(username)

    if wishlist:
        stock_data = get_wishlist_stock_data(wishlist)
        for stock, df in stock_data.items():
            try:
                if not df.empty and df["Close"].iloc[-1] > df["Close"].iloc[-2]:
                    st.toast(f"\ud83d\ude80 {stock} is rising! Last Price: {df['Close'].iloc[-1]}")
            except Exception as e:
                print(f"Error in notification check for {stock}:", e)
