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

GUILD_ID = os.getenv("GUILD_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")
USERTOKEN = os.getenv("USERTOKEN")

STATUS = "online"
SELF_MUTE = True
SELF_DEAF = True

HEADERS = {"Authorization": USERTOKEN, "Content-Type": "application/json"}

response = requests.get('https://discordapp.com/api/v9/users/@me', headers=HEADERS)

if response.status_code != 200:
    print("[ERROR] Token invalide. Vérifiez vos identifiants.")
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
        except:
            print("[ERROR] Déconnecté pendant le heartbeat.")
            break 

async def connect_voice():
    while True:
        try:
            async with websockets.connect("wss://gateway.discord.gg/?v=9&encoding=json") as ws:
                start_payload = json.loads(await ws.recv())  
                heartbeat_interval = start_payload['d']['heartbeat_interval']

                auth = {
                    "op": 2,
                    "d": {
                        "token": USERTOKEN,
                        "properties": {
                            "$os": "Windows",
                            "$browser": "Chrome",
                            "$device": "Windows"
                        },
                        "presence": {
                            "status": STATUS,
                            "afk": False
                        }
                    }
                }

                vc_payload = {
                    "op": 4,
                    "d": {
                        "guild_id": GUILD_ID,
                        "channel_id": CHANNEL_ID,
                        "self_mute": SELF_MUTE,
                        "self_deaf": SELF_DEAF
                    }
                }

                await ws.send(json.dumps(auth))
                await ws.send(json.dumps(vc_payload))

                print(f"Connecté en vocal en tant que {USERNAME}#{DISCRIMINATOR} ({USERID})")

                asyncio.create_task(heartbeat(ws, heartbeat_interval))

                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)

                    if data.get("op") == 10:
                        heartbeat_interval = data['d']['heartbeat_interval']

                    elif data.get("t") == "VOICE_STATE_UPDATE":
                        state = data.get("d", {})
                        if state.get("user_id") == USERID and state.get("channel_id") is None:
                            print("Expulsé du vocal ! Tentative de reconnexion...")
                            await asyncio.sleep(2) 
                            await ws.send(json.dumps(vc_payload))  
                            print("Reconnexion réussie !")

        except Exception as e:
            print(f"[ERROR] Déconnexion WebSocket : {e}. Reconnexion dans 5 secondes...")
            await asyncio.sleep(5) 

def start_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    threading.Thread(target=start_flask, daemon=True).start()  
    asyncio.run(connect_voice())
