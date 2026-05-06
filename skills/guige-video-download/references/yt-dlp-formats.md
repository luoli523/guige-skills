# yt-dlp Format Notes

`guige-video-download` keeps format selection conservative and container-oriented:

- `mp4`: prefer `mp4` video + `m4a` audio, then fall back to any compatible best stream.
- `webm`: prefer `webm` video + `webm`/`opus` audio, then fall back.
- `mkv`: accept best video + best audio and merge to Matroska.
- quality caps such as `1080p` are encoded as `height<=1080`.
- audio-only uses `bestaudio/best` and `yt-dlp -x`.

`ffmpeg` is needed when yt-dlp must merge separate audio/video streams, convert audio formats, or convert containers. Without `ffmpeg`, some single-file downloads still work, but high-quality video and audio conversion may fail.

Avoid adding platform-specific scraping logic here. Let `yt-dlp` handle site extraction unless a future Gui Ge skill explicitly owns a first-party API integration.
