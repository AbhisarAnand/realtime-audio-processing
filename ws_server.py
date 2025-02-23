import asyncio
import websockets
import os

SAVE_DIR = "recordings"
os.makedirs(SAVE_DIR, exist_ok=True)

FINAL_WEBM = os.path.join(SAVE_DIR, "final_audio.webm")

async def handle_audio(websocket):
	print("Client connected")

	with open(FINAL_WEBM, "wb") as final_audio:
		try:
			while True:
				audio_chunk = await websocket.recv()
				final_audio.write(audio_chunk)
				print(f"Chunk received and appended to {FINAL_WEBM}")

				await websocket.send("Chunk received")

		except websockets.exceptions.ConnectionClosed:
			print("Client disconnected")

async def main():
	async with websockets.serve(handle_audio, "0.0.0.0", 3001):
		print("WebSocket Server running on ws://localhost:3001")
		await asyncio.Future()

if __name__ == "__main__":
	asyncio.run(main())