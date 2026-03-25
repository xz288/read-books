"""
Transcribe an audio file using faster-whisper (local, GPU-accelerated).
Usage: python transcribe.py <audio_file_path>
First run downloads the Whisper model (~150MB for 'base', ~1.5GB for 'large-v3').
"""
import sys
import os

# Force UTF-8 output regardless of Windows console encoding
sys.stdout.reconfigure(encoding='utf-8')

# Ensure ffmpeg is in PATH (winget installs it here)
FFMPEG_BIN = r"C:\Users\Zach Zhang\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"
os.environ["PATH"] = FFMPEG_BIN + os.pathsep + os.environ.get("PATH", "")

if len(sys.argv) < 2:
    print("Usage: python transcribe.py <audio_file>")
    sys.exit(1)

audio_path = sys.argv[1]

if not os.path.exists(audio_path):
    sys.stderr.write(f"File not found: {audio_path}\n")
    sys.exit(1)

from faster_whisper import WhisperModel

# Use 'base' model for speed, 'small' for better accuracy, 'large-v3' for best quality
# device='cuda' uses GPU, 'cpu' as fallback
model = WhisperModel("small", device="cpu", compute_type="int8")


segments, info = model.transcribe(audio_path, beam_size=5)

text = " ".join(segment.text.strip() for segment in segments)
print(text)
