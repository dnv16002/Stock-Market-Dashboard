import streamlit as st
import pymongo
from pymongo import MongoClient
import bcrypt

# ✅ MongoDB Connection
MONGO_URI = st.secrets["mongo"]["uri"]
client = MongoClient(MONGO_URI)
db = client["stock_market_dashboard"]
users_collection = db["users"]

# ✅ Function to fetch user details
def get_user(username):
    """Retrieve user details from MongoDB."""
    user = users_collection.find_one({"username": username})
    if user:
        return {"username": user["username"], "password": user["password"].encode("utf-8")}
    return None

# ✅ Function to add a new user (with hashed password)
def add_user(username, password):
    """Register a new user with hashed password."""
    if users_collection.find_one({"username": username}):
        return False  # Username already exists
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    users_collection.insert_one({"username": username, "password": hashed_password})
    return True

# ✅ Function to verify user login
def verify_user(username, password):
    """Check if the entered password matches the stored hashed password."""
    user = get_user(username)
    if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
        return True
    return False
