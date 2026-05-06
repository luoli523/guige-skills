# Troubleshooting

## yt-dlp missing

Install `yt-dlp` and retry:

```bash
brew install yt-dlp
```

## ffmpeg missing

Install `ffmpeg` if stream merging or audio conversion fails:

```bash
brew install ffmpeg
```

## Login required

If the user can access the video in their browser, retry with:

```bash
--cookies-from-browser chrome
```

Use `safari` or `firefox` if that is where the user is logged in.

## X/Twitter video has no downloadable media

Some posts contain no video, contain only externally embedded players, or are restricted. Keep yt-dlp's exact error text in the final report.

## Private, paid, region-locked, or DRM content

Do not bypass access controls. Report that the content cannot be downloaded by this skill.
