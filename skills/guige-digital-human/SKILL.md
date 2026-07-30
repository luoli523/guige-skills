---
name: guige-digital-human
description: Produce authorized digital-human talking-head videos with MiniMax voice cloning and HeyGen Image-to-Video. Use when the user asks for 数字人, 口播视频, 数字人口播, talking-head video, voice clone narration video, a 15-second digital-human preview, or batch digital-human production from a script, portrait, and voice sample. Enforces asset preflight, a 15-second preview gate before full 1080p generation, and job-state tracking for resumable paid workflows.
version: 0.1.0
metadata:
  openclaw:
    requires:
      anyBins:
        - python3
---

# Gui Ge Digital Human

数字人口播视频生产线：MiniMax 负责声音克隆与配音，HeyGen 负责照片驱动的口型视频。

## Core Rule

MiniMax 出声音，HeyGen 出画面。有 MiniMax 配音文件时，HeyGen 一律用 `audio_asset_id` 驱动；除非用户明确要求使用 HeyGen 自带 TTS，否则不要切换到 HeyGen `script + voice_id` 模式。

始终保留生产 gate：

```text
资产校验 -> MiniMax 配音 -> 15秒 HeyGen 预览 -> 用户 approve -> 1080p 正式版 -> 下载QA -> 归档 state
```

## Operating Boundaries

- 密钥只从 guige-scoped 配置读取：`MINIMAX_API_KEY`、`MINIMAX_GROUP_ID`、`HEYGEN_API_KEY`。
- 永远不打印完整 API key、Authorization header、签名临时 URL。
- MiniMax 克隆/TTS 和 HeyGen 视频生成都是付费外部动作，每轮首次付费调用前必须获得用户明确确认。
- 克隆声音或生成视频前，要求用户确认声音、肖像、文案与用途均已获授权；不提供法律意见，合规问题提示用户自行核实（详见 [safety.md](references/safety.md)）。
- 用户要正式版时，仍先出 15 秒预览，除非用户明确豁免预览 gate。
- 每个外部任务阶段前后都更新 `work/job-state.json`；已有 state 且源文件未变时，复用既有 `voice_id`、`asset_id`、`video_id`，不重复克隆、不重复提交付费任务。
- 生成物只写入任务目录（默认 `digital-human/<task-slug>/`），不污染其他运行时输出目录。

## Directory Layout

```text
digital-human/<task-slug>/
├── inputs/
│   ├── portrait.jpg          # 人像：PNG/JPEG，正脸、嘴部清晰
│   ├── voice-source.mp3      # 声音样本：MP3/M4A/WAV，10秒–5分钟，≤20MB
│   └── script.md             # 口播文案
├── work/
│   ├── voiceover-full.mp3    # 完整配音
│   ├── preview-15s.mp3       # 前15秒配音
│   └── job-state.json        # 状态追踪（可断点续跑）
└── outputs/
    ├── preview-15s.mp4       # 720p 预览
    └── final-1080p.mp4       # approve 后的正式版
```

## Configuration

密钥放 guige-scoped env 文件（加载优先级同 `guige-imagen`）：

```text
<cwd>/.guige-skills/.env > ~/.guige-skills/.env
```

```bash
MINIMAX_API_KEY=...
MINIMAX_GROUP_ID=...
HEYGEN_API_KEY=...
```

默认忽略 shell 中的同名环境变量；如需使用，导出 `GUIGE_ALLOW_AMBIENT_PROVIDER_ENV=1`。永远不要读取 `.baoyu-skills`。

## Workflow

### 1. Init & Preflight

```bash
python3 {baseDir}/scripts/main.py init --task <task-slug>
python3 {baseDir}/scripts/main.py preflight --task <task-slug>
```

`preflight` 校验：声音样本格式/时长/大小、人像格式、HeyGen 32MB 上传限制、文案是否为空。任何一项失败就停下，提出最小修复建议，不要发起付费调用。

### 2. MiniMax 配音

```bash
python3 {baseDir}/scripts/main.py narrate --task <task-slug>
```

上传声音样本 → 创建/复用 `voice_id`（命名如 `guige_<slug>_yyyymmdd`）→ 用克隆声音合成完整配音 → 产出 `work/voiceover-full.mp3` 和 `work/preview-15s.mp3`。

中文口型别扭时，用 `--speed 0.95`~`1.05` 重做配音，再重新生成视频。

### 3. HeyGen 15秒预览

```bash
python3 {baseDir}/scripts/main.py preview --task <task-slug>
```

上传人像与预览音频为 HeyGen 资产 → 提交 720p Image-to-Video 任务 → 轮询到 `completed` → 下载 `outputs/preview-15s.mp4` 并做解码校验。

### 4. 暂停等待 approve

停下来让用户按 [checklists.md](references/checklists.md) 的清单检查：声音相似度、中文口型、面部形变、眨眼/头肩动作、构图。用户明确同意前不生成正式版。

用户确认后记录 approve：

```bash
python3 {baseDir}/scripts/main.py approve --task <task-slug>
```

### 5. 正式版

```bash
python3 {baseDir}/scripts/main.py final --task <task-slug>
```

`final` 要求 state 中 `approved_by_user=true`，否则拒绝执行。上传完整配音 → 提交 1080p 任务 → 轮询（超时不等于失败，凭 `video_id` 续轮询，不重复提交）→ 下载 `outputs/final-1080p.mp4` → 全片解码校验 → 更新 state。

### 6. 查看状态 / 断点续跑

```bash
python3 {baseDir}/scripts/main.py status --task <task-slug>
```

任何阶段中断后重跑对应子命令即可：state 里已有的 `voice_id`/`asset_id`/`video_id` 会被复用。

## Batch Mode

多条文案时：每条文案一个 task 目录、独立 state；默认只出预览，放 `outputs/previews/`；生成一份 review 表（路径、时长、`video_id`、备注）；用户逐条 approve 后才生成对应正式版。

## Failure Policy

- API 返回明确 `failed`：记录原因，询问用户后再重试付费生成。
- 轮询超时：不视为失败，凭 `video_id` 恢复轮询。
- 下载失败或 MP4 损坏：先重试下载，不要重新生成视频。
- 签名 URL 过期：重新查询任务状态换取新 URL，不要新开付费任务。

## Optional Upload

用户要求上传时，通过 `guige-drive-upload` CLI 上传 materials 到 `guige-skills/guige-digital-human/<task-slug>/`。

## References

按需阅读：

- [api-facts.md](references/api-facts.md) — MiniMax 与 HeyGen 的 API 事实基线；涉及确切参数或价格时先对照官方文档。
- [checklists.md](references/checklists.md) — state 模板、预览审核清单、批量 review 表模板。
- [safety.md](references/safety.md) — 授权、同意、披露与公开发布边界。
