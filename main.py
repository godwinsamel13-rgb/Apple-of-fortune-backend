# main.py
import os
import asyncio
from fastapi import FastAPI, HTTPException
from supabase import create_client, Client
from pydantic import BaseModel
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

# 🔥 Supabase credentials
SUPABASE_URL = "https://bskrigfmzfsbwnjxnvhi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJza3JpZ2ZtemZzYnduanhudmhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5OTEwMDMsImV4cCI6MjA3NzU2NzAwM30.2ULAr8iwpEBV7ucszXDkRxgD1RwtKD514XN_8ql3uEk"

# Connect to Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Apple of Fortune & Aviator Backend")

# Enable CORS for frontend apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Pydantic Models
# -----------------------------
class UserVIPUpdate(BaseModel):
    user_id: str
    vip_status: bool

class AddBalance(BaseModel):
    user_id: str
    platform: str
    balance: float

# -----------------------------
# API Endpoints
# -----------------------------

@app.get("/users")
async def fetch_users():
    return supabase.table("Users").select("*").execute().data

@app.get("/platforms")
async def fetch_platforms():
    return supabase.table("Platform").select("*").execute().data

@app.get("/predictions/{platform_name}")
async def fetch_predictions(platform_name: str):
    return supabase.table("Prediction").select("*").eq("Platform", platform_name).execute().data

@app.post("/update-vip")
async def update_vip(data: UserVIPUpdate):
    result = supabase.table("Users").update({"vip": data.vip_status}).eq("id", data.user_id).execute()
    if result.error:
        raise HTTPException(status_code=400, detail=result.error.message)
    return result.data

@app.post("/add-balance")
async def add_balance(data: AddBalance):
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    result = supabase.table("Balance").insert({
        "Users_id": data.user_id,
        "Platform": data.platform,
        "Balance": data.balance,
        "Updated_at": now,
        "Is_active": True,
        "Created_at": now
    }).execute()
    if result.error:
        raise HTTPException(status_code=400, detail=result.error.message)
    return result.data

# -----------------------------
# Real-time subscription for predictions
# -----------------------------
async def realtime_listener():
    def handle_update(payload):
        print("🔔 Prediction Updated:", payload)

    print("⏳ Connecting to Supabase Realtime for Prediction table...")
    subscription = supabase.table("Prediction").on("*", handle_update).subscribe()
    while True:
        await asyncio.sleep(1)

# -----------------------------
# Run FastAPI with real-time listener
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    loop = asyncio.get_event_loop()
    loop.create_task(realtime_listener())
    uvicorn.run(app, host="0.0.0.0", port=8000)
