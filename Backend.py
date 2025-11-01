# backend.py
import os
from supabase import create_client, Client
from datetime import datetime

# 🔥 Your Supabase credentials
SUPABASE_URL = "https://bskrigfmzfsbwnjxnvhi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJza3JpZ2ZtemZzYnduanhudmhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5OTEwMDMsImV4cCI6MjA3NzU2NzAwM30.2ULAr8iwpEBV7ucszXDkRxgD1RwtKD514XN_8ql3uEk"

# Connect to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# Example functions
# -----------------------------

def get_users():
    """Fetch all users"""
    response = supabase.table("Users").select("*").execute()
    return response.data

def get_platforms():
    """Fetch all platforms"""
    response = supabase.table("Platform").select("*").execute()
    return response.data

def get_predictions(platform_name: str):
    """Fetch predictions for a platform"""
    response = supabase.table("Prediction").select("*").eq("Platform", platform_name).execute()
    return response.data

def update_user_vip(user_id: str, vip_status: bool = True):
    """Update a user's VIP status"""
    response = supabase.table("Users").update({"vip": vip_status}).eq("id", user_id).execute()
    return response.data

def add_balance(user_id: str, platform: str, balance: float):
    """Add balance entry for a user"""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    response = supabase.table("Balance").insert({
        "Users_id": user_id,
        "Platform": platform,
        "Balance": balance,
        "Updated_at": now,
        "Is_active": True,
        "Created_at": now
    }).execute()
    return response.data

# -----------------------------
# Test connection
# -----------------------------
if __name__ == "__main__":
    print("✅ Supabase backend connected successfully!")
    print("Users:", get_users())
    print("Platforms:", get_platforms())
    print("1xBet Predictions:", get_predictions("1xBet"))
