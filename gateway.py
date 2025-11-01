import asyncio
import httpx
from supabase import create_client, Client
import os
from datetime import datetime

# ---------------- Supabase config ----------------
SUPABASE_URL = "https://bskrigfmzfsbwnjxnvhi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJza3JpZ2ZtemZzYnduanhudmhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5OTEwMDMsImV4cCI6MjA3NzU2NzAwM30.2ULAr8iwpEBV7ucszXDkRxgD1RwtKD514XN_8ql3uEk"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- Platforms ----------------
PLATFORMS = ["1xBet", "22Bet", "Win-Win", "888starz"]

# ---------------- Dummy API URLs ----------------
# Replace these with real endpoints if available
PLATFORM_API = {
    "1xBet": "https://api.1xbet.com/floors",
    "22Bet": "https://api.22bet.com/floors",
    "Win-Win": "https://api.winwin.com/floors",
    "888starz": "https://api.888starz.com/floors",
}

# ---------------- Fetch platform data ----------------
async def fetch_platform(platform: str):
    url = PLATFORM_API.get(platform)
    async with httpx.AsyncClient() as client:
        try:
            # Example: fetch JSON data
            response = await client.get(url, timeout=10)
            data = response.json()
        except Exception as e:
            print(f"[ERROR] Failed to fetch {platform}: {e}")
            # If API not available, simulate dummy floors
            data = [
                {"floor": "X349.68", "pattern": ["X","X","X","X","🍎"]},
                {"floor": "X69.93", "pattern": ["X","🍎","X","🍎","X"]},
                {"floor": "X27.92", "pattern": ["X","🍎","🍎","X","X"]},
            ]
    return data

# ---------------- Push data to Supabase ----------------
async def push_to_supabase(platform: str, floors: list):
    round_id = f"AFR{datetime.now().strftime('%Y%m%d%H%M%S')}"
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "Platform": platform,
        "Round_id": round_id,
        "Floors": floors,
        "Created_at": created_at
    }
    try:
        result = supabase.table("Prediction").insert(payload).execute()
        print(f"[SUCCESS] Updated {platform} at {created_at}")
    except Exception as e:
        print(f"[ERROR] Failed to push {platform}: {e}")

# ---------------- Main loop ----------------
async def main_loop():
    while True:
        for platform in PLATFORMS:
            floors = await fetch_platform(platform)
            await push_to_supabase(platform, floors)
        await asyncio.sleep(15)  # Fetch every 15 seconds

# ---------------- Run ----------------
if __name__ == "__main__":
    print("🚀 API Gateway running...")
    asyncio.run(main_loop())
