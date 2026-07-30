# Checklists

## State Template

`work/job-state.json`，由 `main.py init` 生成、各阶段自动维护：

```json
{
  "task": "demo",
  "created_at": "2026-07-30",
  "minimax": {
    "source_file_id": null,
    "voice_id": null,
    "tts_model": "speech-2.8-hd",
    "full_audio": "work/voiceover-full.mp3",
    "preview_audio": "work/preview-15s.mp3"
  },
  "heygen": {
    "image_asset_id": null,
    "preview_audio_asset_id": null,
    "preview_video_id": null,
    "full_audio_asset_id": null,
    "full_video_id": null
  },
  "status": {
    "narration": "not_started",
    "preview": "not_started",
    "approved_by_user": false,
    "final": "not_started"
  },
  "outputs": {
    "preview_video": "outputs/preview-15s.mp4",
    "final_video": null
  }
}
```

永远不要把 API key、Authorization header、签名临时 URL 写进 state 文件。

## 预览审核清单

用户 approve 前逐项检查：

- 声音听起来像目标说话人。
- 中文口型自然跟随音频。
- 脸型、牙齿、嘴唇、下颌无扭曲。
- 眨眼、点头、肩部动作自然。
- 构图适配目标平台（竖屏/横屏）。
- 语速不快于口型可跟踪范围。
- 开头结尾没有吞字或截断。

## 批量 Review 表模板

批量模式下生成 `outputs/preview-review.md`：

```markdown
| # | 文案 | 预览路径 | 时长 | video_id | 备注 | approve |
|---|------|---------|------|----------|------|---------|
| 1 | scripts/ep01.md | outputs/previews/ep01.mp4 | 15s | redacted | 口型OK | [ ] |
```

## 常用调用

```bash
# 只出15秒预览
python3 scripts/main.py init --task demo
python3 scripts/main.py preflight --task demo
python3 scripts/main.py narrate --task demo
python3 scripts/main.py preview --task demo

# approve 后出正式版
python3 scripts/main.py approve --task demo
python3 scripts/main.py final --task demo

# 查看进度 / 断点续跑
python3 scripts/main.py status --task demo
```
