import sys
import json
import time
import requests
import asyncio
import websockets
import threading
import os
from flask import Flask

app = Flask(__name__)

# Variables d'environnement
GUILD_ID = os.getenv("GUILD_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")
USERTOKEN = os.getenv("USERTOKEN")

STATUS = "online"
SELF_MUTE = True
SELF_DEAF = True

HEADERS = {
    "Authorization": USERTOKEN,
    "Content-Type": "application/json"
}

# Vérification du token utilisateur
response = requests.get('https://discord.com/api/v9/users/@me', headers=HEADERS)
if response.status_code != 200:
    print("[ERREUR] Token invalide.")
    sys.exit()

userinfo = response.json()
USERNAME = userinfo["username"]
DISCRIMINATOR = userinfo["discriminator"]
USERID = userinfo["id"]

async def heartbeat(ws, interval):
    while True:
        await asyncio.sleep(interval / 1000)
        try:
            await ws.send(json.dumps({"op": 1, "d": None}))
        except Exception as e:
            print(f"[ERREUR] Heartbeat échoué : {e}")
            break

async def connect_voice():
    while True:
        try:
            async with websockets.connect("wss://gateway.discord.gg/?v=9&encoding=json") as ws:
                hello = json.loads(await ws.recv())
                heartbeat_interval = hello["d"]["heartbeat_interval"]
                asyncio.create_task(heartbeat(ws, heartbeat_interval))

                # Authentification
                await ws.send(json.dumps({
                    "op": 2,
                    "d": {
                        "token": USERTOKEN,
                        "properties": {
                            "$os": "windows",
                            "$browser": "chrome",
                            "$device": "pc"
                        },
                        "presence": {
                            "status": STATUS,
                            "afk": False
                        }
                    }
                }))

                await asyncio.sleep(2)

                # Envoi du voice state update
                await ws.send(json.dumps({
                    "op": 4,
                    "d": {
                        "guild_id": GUILD_ID,
                        "channel_id": CHANNEL_ID,
                        "self_mute": SELF_MUTE,
                        "self_deaf": SELF_DEAF
                    }
                }))

                print(f"Connecté en vocal en tant que {USERNAME}#{DISCRIMINATOR} ({USERID})")

                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)

                    if "t" in data and data["t"] == "VOICE_STATE_UPDATE":
                        state = data["d"]
                        if state.get("user_id") == USERID and state.get("channel_id") is None:
                            print("[INFO] Expulsé du vocal. Reconnexion...")
                            await asyncio.sleep(2)
                            await ws.send(json.dumps({
                                "op": 4,
                                "d": {
                                    "guild_id": GUILD_ID,
                                    "channel_id": CHANNEL_ID,
                                    "self_mute": SELF_MUTE,
                                    "self_deaf": SELF_DEAF
                                }
                            }))
                            print("[INFO] Reconnexion envoyée.")

        except Exception as e:
            print(f"[ERREUR] WebSocket déconnecté : {e}. Nouvelle tentative dans 5 sec...")
            await asyncio.sleep(5)

# Flask app pour ping uptime
def start_flask():
    app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    threading.Thread(target=start_flask, daemon=True).start()
    asyncio.run(connect_voice())
