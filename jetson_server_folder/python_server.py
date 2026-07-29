import asyncio
import websockets
import json

connected_clients = set()


last_real_message = None

#//Why are the spaces so big how do i fix this
async def handler(websocket):
	global last_real_message

	connected_clients.add(websocket)
	print("Client connected:", websocket.remote_address)

	# Acknowledge connection
	await websocket.send(json.dumps({
		"status": "connected_to_python_server"
	}))

	try:
		async for message in websocket:

			# Ignore empty frames
			if not message or message.strip() == "":
				continue

			# Ignore duplicate messages
			if message == last_real_message:
				continue

			# Update last real message
			last_real_message = message

			print("Received from client:", message)

			# Validate JSON
			try:
				data = json.loads(message)
			except json.JSONDecodeError:
				await websocket.send(json.dumps({
					"error": "invalid_json"
				}))
				continue

			# Broadcast ONLY real messages
			for client in connected_clients:
				if client != websocket:
					await client.send(json.dumps({
						"status": "forwarded_from_python",
						"payload": data
					}))

	except websockets.exceptions.ConnectionClosed:
		print("Client disconnected:", websocket.remote_address)

	finally:
		connected_clients.remove(websocket)


async def main():
	print("Python WebSocket server running on ws://localhost:8765")
	async with websockets.serve(handler, "localhost", 8765):
		# Change above to 0.0.0.0, 8080 for the samsung
		await asyncio.Future()  # Run forever


if __name__ == "__main__":
	asyncio.run(main())
