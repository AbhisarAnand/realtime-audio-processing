import os
import subprocess

SAVE_DIR = "recordings"
FINAL_WEBM = "final_audio.webm"
FINAL_WAV = "final_audio.wav"

def convert_to_wav():
	if not os.path.exists(os.path.join(SAVE_DIR, FINAL_WEBM)):
		print("Merged WebM file not found!")
		return

	convert_cmd = f"ffmpeg -i {os.path.join(SAVE_DIR, FINAL_WEBM)} -acodec pcm_s16le -ar 16000 -ac 1 {os.path.join(SAVE_DIR, FINAL_WAV)}"
	subprocess.run(convert_cmd, shell=True, check=True)

	print(f"Converted to WAV: {os.path.join(SAVE_DIR, FINAL_WAV)}")

if __name__ == "__main__":
	convert_to_wav()