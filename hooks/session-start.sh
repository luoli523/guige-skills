#!/usr/bin/env bash
# SessionStart hook — print available guige skills as a quick reference.
# Runs once per session start. Output goes to the user-visible session log.

cat <<'EOF'
🎨 guige skills available — 触发关键词速查:
  /imagen              图片生成 (OpenAI / Google API)
  /infographic         鬼哥风格信息图
  /hand-write-pic      一页式手绘知识卡
  /disassembly-diagram 拆解图 / 爆炸图 / 剖面图
  /svg                 可编辑 SVG 图表 (matrix / flowchart / timeline)
  /slides              图片式幻灯片 (PPTX / PDF)
  /picbook             儿童科普绘本
  /blog-post           写 Hugo 博客文章
  /x-to-blog           X 推文改写为博客
  /x-2-md              X / Twitter 转 Markdown
  /to-wechat           微信公众号草稿
  /video-download      视频 / 音频下载
  /digital-human       数字人口播视频 (MiniMax 声音克隆 + HeyGen)
  /wuxia-writing       原创武侠构思、创作、改写与审校
  /drive-upload        上传到 Google Drive
EOF
