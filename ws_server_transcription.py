import asyncio
import websockets
import numpy as np
import os
import subprocess
from faster_whisper import WhisperModel

model = WhisperModel("small.en")

SAVE_DIR = "recordings"
os.makedirs(SAVE_DIR, exist_ok=True)

async def process_chunk(audio_chunk, chunk_id):
	"""Process each audio chunk: Save, Convert, Transcribe, and Return."""
	chunk_webm = os.path.join(SAVE_DIR, f"chunk_{chunk_id}.webm")
	chunk_wav = os.path.join(SAVE_DIR, f"chunk_{chunk_id}.wav")

	with open(chunk_webm, "wb") as f:
		f.write(audio_chunk)

	if not os.path.exists(chunk_webm) or os.path.getsize(chunk_webm) == 0:
		print(f"Error: {chunk_webm} is empty or was not saved correctly.")
		return {"transcription": ["Error: Empty or corrupted audio chunk"], "word_timestamps": []}

	convert_cmd = f"ffmpeg -i {chunk_webm} -acodec pcm_s16le -ar 16000 -ac 1 {chunk_wav} -y -loglevel error"

	try:
		subprocess.run(convert_cmd, shell=True, check=True)
	except subprocess.CalledProcessError as e:
		print(f"FFmpeg conversion failed for {chunk_webm}: {e}")
		return {"transcription": ["Error: FFmpeg conversion failed"], "word_timestamps": []}

	audio = np.memmap(chunk_wav, dtype=np.int16, mode='r').astype(np.float32) / 32768.0

	segments, _ = model.transcribe(audio, word_timestamps=True)
	segments = list(segments)

	result = {
		"transcription": [segment.text for segment in segments],
		"word_timestamps": [
			{"word": word.word, "start": word.start, "end": word.end}
			for segment in segments for word in segment.words
		]
	}

	return result

async def transcribe_audio(websocket):
	print("Client connected")

	chunk_id = 0

	try:
		async for message in websocket:
			chunk_id += 1
			print(f"Processing chunk {chunk_id}...")

			result = await process_chunk(message, chunk_id)

			await websocket.send(str(result))

	except websockets.exceptions.ConnectionClosed:
		print("Client disconnected")

async def main():
	async with websockets.serve(transcribe_audio, "0.0.0.0", 3001):
		print("WebSocket Server running on ws://localhost:3001")
		await asyncio.Future()

if __name__ == "__main__":
	asyncio.run(main())