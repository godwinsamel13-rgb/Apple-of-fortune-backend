# main.py
import os
import json
import time
import requests
from supabase import create_client, Client
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Supabase credentials
SUPABASE_URL = "https://bskrigfmzfsbwnjxnvhi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJza3JpZ2ZtemZzYnduanhudmhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5OTEwMDMsImV4cCI6MjA3NzU2NzAwM30.2ULAr8iwpEBV7ucszXDkRxgD1RwtKD514XN_8ql3uEk"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# FastAPI setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Platforms we monitor ---
PLATFORMS = ["1xBet", "Win-Win", "22Bet", "888starz"]

# Simulated API fetch function (replace with real API call later)
def fetch_platform_floors(platform: str):
    # Example simulated floors
    return [
        {"floor": "X349.68", "pattern": ["X","X","X","X","🍎"]},
        {"floor": "X69.93",  "pattern": ["X","🍎","X","🍎","X"]},
        {"floor": "X27.92",  "pattern": ["X","🍎","🍎","X","X"]},
        {"floor": "X11.18",  "pattern": ["🍎","X","🍎","🍎","X"]},
        {"floor": "X6.71",   "pattern": ["🍎","X","X","🍎","🍎"]},
    ]

# Update Supabase Platform table
def update_platform(platform: str):
    floors = fetch_platform_floors(platform)
    # Set is_active True and uncovered_image (example URL)
    supabase.table("Platform").update({
        "is_active": True,
        "covered_image": "https://example.com/cross.png",
        "uncovered_image": "https://example.com/apple.png"
    }).eq("Platform", platform).execute()
    # Optional: update prediction table here
    supabase.table("Prediction").upsert({
        "Platform": platform,
        "Round_id": f"AFR{int(time.time())}",
        "Floors": json.dumps(floors),
        "Created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }).execute()

# Endpoint to get live floors
@app.get("/api/floors")
def get_floors():
    result = {}
    for p in PLATFORMS:
        res = supabase.table("Prediction").select("*").eq("Platform", p).order("Created_at", desc=True).limit(1).execute()
        if res.data:
            result[p] = res.data[0]["Floors"]
        else:
            result[p] = fetch_platform_floors(p)
    return result

# WebSocket for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        floors = {p: fetch_platform_floors(p) for p in PLATFORMS}
        await ws.send_json(floors)
        time.sleep(5)  # send every 5 seconds

# Main loop to update platforms continuously
def run_platform_loop():
    while True:
        for p in PLATFORMS:
            update_platform(p)
        time.sleep(10)  # update every 10 seconds

# Run backend
if __name__ == "__main__":
    import threading
    threading.Thread(target=run_platform_loop, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
