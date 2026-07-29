#VENV
import asyncio
import websockets
import json

async def send_json_to_server(json_data):
  uri = "ws://localhost:8765"
  print(uri)
  async with websockets.connect(uri) as websocket:
    await websocket.send(json.dumps(json_data))
    print("Sent JSON to server")

def notify_server(json_data):
  asyncio.get_event_loop().run_until_complete(send_json_to_server(json_data))
