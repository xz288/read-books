---
name: yt-dlp
description: "Download YouTube (and 1000+ other sites) videos or audio using yt-dlp."
---

# yt-dlp Skill

Download videos or audio from YouTube and other sites. Full path required on Windows.

**Binary path:** `C:\Users\Zach Zhang\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\yt-dlp.exe`

Use the variable `YTDLP` for brevity in examples below:
```
YTDLP="C:\Users\Zach Zhang\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\LocalCache\local-packages\Python311\Scripts\yt-dlp.exe"
```

## Download Audio (MP3)

```bash
"$YTDLP" -x --audio-format mp3 -o "F:/claw_download/%(title)s.%(ext)s" "URL"
```

## Download Video (best quality)

```bash
"$YTDLP" -f "bestvideo+bestaudio" --merge-output-format mp4 -o "F:/claw_download/%(title)s.%(ext)s" "URL"
```

## Download Video (specific quality, e.g. 720p)

```bash
"$YTDLP" -f "bestvideo[height<=720]+bestaudio" --merge-output-format mp4 -o "F:/claw_download/%(title)s.%(ext)s" "URL"
```

## Get video info without downloading

```bash
"$YTDLP" --dump-json --no-download "URL" | python -c "import sys,json; d=json.load(sys.stdin); print(d['title'], d['duration_string'], d['uploader'])"
```

## Download playlist (limit to first N)

```bash
"$YTDLP" --playlist-end 5 -o "C:/Users/Zach Zhang/Downloads/%(playlist_index)s-%(title)s.%(ext)s" "PLAYLIST_URL"
```

## Tips

- Default download folder: `C:/Users/Zach Zhang/Downloads/`
- Always show the output path after download completes
- If user doesn't specify quality, use best quality (default)
- Supports YouTube, Twitter/X, Reddit, TikTok, Twitch clips, and 1000+ sites
