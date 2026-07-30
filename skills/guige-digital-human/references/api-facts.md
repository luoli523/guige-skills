# API Facts

Last reviewed: 2026-07-30

本文件是紧凑的事实基线。任务依赖确切请求字段、价格、模型可用性或配额时，先对照 MiniMax 与 HeyGen 官方文档再发起付费请求。

## MiniMax Voice Clone + T2A

官方文档：

- https://platform.minimax.io/docs/guides/speech-voice-clone
- https://platform.minimax.io/docs/api-reference/voice-cloning-clone
- https://platform.minimax.io/docs/api-reference/speech-t2a-http

本 skill 依赖的事实：

- 声音样本通过 `POST /v1/files/upload?GroupId=<group_id>` 上传，`purpose=voice_clone`。
- 声音克隆通过 `POST /v1/voice_clone?GroupId=<group_id>`，传 `file_id` + 自定义 `voice_id`。
- 文本转语音用 `POST /v1/t2a_v2?GroupId=<group_id>`，传 `model` + `text` + `voice_setting.voice_id`。
- 声音样本要求：MP3/M4A/WAV，10 秒–5 分钟，≤20MB。
- 克隆费按声音收取（Rapid 约 $1.5/个），首次用该 voice_id 做 T2A 合成时才扣费。
- TTS 按字符计费：speech-2.8-turbo 约 $60/百万字符，speech-2.8-hd 约 $100/百万字符。
- 长期不使用的克隆声音可能在保留窗口后被清理，克隆后尽快使用或验证。

生产建议：

- 声音样本干净：单人、无背景音乐、无明显混响、音量稳定。
- 长文案合成前先做短句测试。
- 同一说话人保持稳定 `voice_id` 以便复用。
- `speed` 建议 0.95–1.05，利于 HeyGen 中文口型跟踪。

## HeyGen Assets + Image-to-Video

官方文档：

- https://developers.heygen.com/image-to-video
- https://developers.heygen.com/assets
- https://developers.heygen.com/docs/pricing

本 skill 依赖的事实：

- 资产上传：`POST https://api.heygen.com/v3/assets`，header `x-api-key`，multipart `file` 字段；返回 `asset_id`。
- 标准上传上限 32MB；更大文件走三步直传（`/v3/assets/direct-uploads` → PUT → `/v3/assets/{id}/complete`）。
- 创建视频：`POST /v3/videos`，`type=image` + 图片 `asset_id` + `audio_asset_id`。
- `script + voice_id` 与 `audio_asset_id` 互斥；配音来自 MiniMax 时必须用后者。
- 轮询：`GET /v3/videos/{video_id}`，状态 `pending → processing → completed/failed`；完成时返回 `video_url`。
- API 走预付费钱包按秒计费：Avatar III 约 $0.0433/秒，Avatar IV 约 $0.05/秒。
- 轮询超时不等于任务失败，凭 `video_id` 续查。

生产建议：

- 预览用 720p + 便宜引擎，正式版才用 1080p。
- 视频生成完成后尽快下载，避免签名 URL 过期。
- 下载后对全片做解码校验，不要只看文件大小或开头几秒。

## Pricing And Availability

- 不要把历史价格硬编码进自动化逻辑。
- 大批量生产前，让用户确认当前 MiniMax / HeyGen 价格、账户额度与配额。
- 对 MiniMax / HeyGen 的网络调用一律视为付费外部动作，除非用户另有说明。
