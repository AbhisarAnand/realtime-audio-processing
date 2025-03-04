import asyncio
import websockets
import numpy as np
import io
import soundfile as sf
from faster_whisper import WhisperModel

# Load Whisper model
model = WhisperModel("small.en", compute_type="float32")

async def process_audio(audio_bytes):
    """Processes raw PCM 16-bit 16kHz mono audio chunks and transcribes."""
    
    # Convert raw PCM bytes to a NumPy array
    with io.BytesIO(audio_bytes) as audio_file:
        audio, samplerate = sf.read(audio_file, dtype="int16", channels=1, samplerate=16000)

    # Normalize audio to float32
    audio = audio.astype(np.float32) / 32768.0

    # Transcribe using Whisper
    segments, _ = model.transcribe(audio, word_timestamps=True)
    segments = list(segments)

    # Format response
    return {
        "transcription": [segment.text for segment in segments],
        "word_timestamps": [
            {"word": word.word, "start": word.start, "end": word.end}
            for segment in segments for word in segment.words
        ]
    }

async def transcribe_audio(websocket):
    print("Client connected")

    try:
        async for message in websocket:
            print(f"Received {len(message)} bytes of PCM audio chunk.")

            # Process and transcribe in real-time
            result = await process_audio(message)

            # Send real-time transcription
            await websocket.send(str(result))

    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    async with websockets.serve(transcribe_audio, "0.0.0.0", 3001):
        print("WebSocket Server running on ws://localhost:3001")
        await asyncio.Future()  # Keep running forever

if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import websockets

async def receive_audio(websocket):
    print("Client connected, waiting for audio data...")

    try:
        async for message in websocket:
            print(f"Received {len(message)} bytes of raw PCM audio")
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    async with websockets.serve(receive_audio, "0.0.0.0", 3001):
        print("WebSocket Server running on ws://localhost:3001")
        await asyncio.Future()  # Keep running forever

if __name__ == "__main__":
    asyncio.run(main())



