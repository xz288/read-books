---
name: whisper
description: "Transcribe voice messages and audio files to text using faster-whisper running locally on GPU."
---

# Whisper Skill

Transcribe any audio file (OGG, MP3, WAV, M4A, etc.) to text using faster-whisper locally.

## Transcribe a voice message

```bash
python "C:\Users\Zach Zhang\.openclaw\workspace\skills\whisper\transcribe.py" "PATH_TO_AUDIO_FILE"
```

The script outputs the transcribed text to stdout. First run will download the Whisper base model (~150MB) automatically.

## When receiving a Telegram voice message

Telegram delivers voice messages as `.ogg` files. The file path will be provided by OpenClaw. Run:

```bash
python "C:\Users\Zach Zhang\.openclaw\workspace\skills\whisper\transcribe.py" "PATH_TO_OGG_FILE"
```

Then treat the transcribed text as the user's actual message and respond to it.

## Models

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| `base` | ~150MB | fastest | good for casual speech |
| `small` | ~500MB | fast | better accuracy |
| `large-v3` | ~1.5GB | slower | best accuracy |

Default is `base`. Edit `transcribe.py` to change the model name if needed.
