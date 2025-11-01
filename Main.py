import json
import requests
import asyncio
import websockets
from supabase import create_client, Client
from datetime import datetime

# ---------------- SUPABASE CONFIG ----------------
SUPABASE_URL = "https://bskrigfmzfsbwnjxnvhi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJza3JpZ2ZtemZzYnduanhudmhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjE5OTEwMDMsImV4cCI6MjA3NzU2NzAwM30.2ULAr8iwpEBV7ucszXDkRxgD1RwtKD514XN_8ql3uEk"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- PLATFORM API CONFIG ----------------
PLATFORM_API_URLS = {
    "1xBet": "https://1xbet.com/api/rounds/latest",
    "22Bet": "https://22bet.com/api/rounds/latest",
    "Win-Win": "https://winwin.com/api/rounds/latest",
    "888starz": "https://888starz.com/api/rounds/latest"
}

PLATFORM_API_HEADERS = {
    "1xBet": {"Authorization": "Bearer YOUR_1XBET_TOKEN"},
    "22Bet": {"Authorization": "Bearer YOUR_22BET_TOKEN"},
    "Win-Win": {"Authorization": "Bearer YOUR_WINWIN_TOKEN"},
    "888starz": {"Authorization": "Bearer YOUR_888STARZ_TOKEN"}
}

# ---------------- FETCH FLOORS ----------------
def fetch_platform_floors(platform: str):
    url = PLATFORM_API_URLS.get(platform)
    headers = PLATFORM_API_HEADERS.get(platform, {})
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()

        floors = []
        for round_data in data.get("rounds", []):
            floor_pattern = round_data.get("pattern", [])
            floors.append({
                "floor": round_data.get("floor"),
                "pattern": floor_pattern
            })
        return floors

    except Exception as e:
        print(f"[{platform}] Error fetching API: {e}")
        # fallback patterns
        return [
            {"floor": "X349.68", "pattern": ["X","X","X","X","🍎"]},
            {"floor": "X69.93", "pattern": ["X","🍎","X","🍎","X"]},
            {"floor": "X27.92", "pattern": ["X","🍎","🍎","X","X"]},
            {"floor": "X11.18", "pattern": ["🍎","X","🍎","🍎","X"]},
            {"floor": "X6.71", "pattern": ["🍎","X","X","🍎","🍎"]}
        ]

# ---------------- UPDATE SUPABASE ----------------
def update_supabase_prediction(platform: str):
    floors = fetch_platform_floors(platform)
    payload = {
        "Platform": platform,
        "Round_id": f"AFR{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        "Floors": json.dumps(floors),
        "Created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        supabase.table("Prediction").insert(payload).execute()
        print(f"[{platform}] Prediction updated successfully.")
    except Exception as e:
        print(f"[{platform}] Supabase insert error: {e}")
    return payload  # for WebSocket broadcast

# ---------------- WEBSOCKET SERVER ----------------
connected_clients = set()

async def websocket_handler(websocket, path):
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            # Optional: receive commands from client
            pass
    finally:
        connected_clients.remove(websocket)

async def broadcast_updates(update_data):
    if connected_clients:
        message = json.dumps(update_data)
        await asyncio.wait([client.send(message) for client in connected_clients])

# ---------------- MAIN LOOP ----------------
async def main_loop():
    while True:
        for platform in PLATFORM_API_URLS.keys():
            data = update_supabase_prediction(platform)
            await broadcast_updates(data)  # push to clients in real-time
        await asyncio.sleep(5)  # adjust for how often you want updates

# ---------------- START SERVER ----------------
async def main():
    # Start WebSocket server
    ws_server = websockets.serve(websocket_handler, "0.0.0.0", 8765)
    print("WebSocket server running on ws://0.0.0.0:8765")
    await asyncio.gather(ws_server, main_loop())

if __name__ == "__main__":
    asyncio.run(main())
