# Spec Schema

All diagram types share these fields:

```json
{
  "title": "Diagram title",
  "subtitle": "Optional subtitle",
  "type": "matrix",
  "theme": "guige-light",
  "canvas": { "ratio": "16:9" },
  "footer": "Optional footer"
}
```

## Matrix

```json
{
  "type": "matrix",
  "sections": [
    {
      "title": "周一",
      "items": [
        { "label": "糖糖", "text": "白天体育课", "icon": "school" },
        { "label": "瓜瓜", "text": "5:45-6:30 游泳", "icon": "swim" }
      ]
    }
  ],
  "highlights": [
    { "label": "A档", "text": "周三 5:40-7:10", "icon": "dumbbell" }
  ]
}
```

## Flowchart

```json
{
  "type": "flowchart",
  "nodes": [
    { "id": "start", "label": "开始", "kind": "start" },
    { "id": "check", "label": "是否通过？", "kind": "decision" },
    { "id": "done", "label": "完成", "kind": "end" }
  ],
  "edges": [
    { "from": "start", "to": "check" },
    { "from": "check", "to": "done", "label": "是" }
  ]
}
```

## Timeline

```json
{
  "type": "timeline",
  "events": [
    { "date": "2026 Q1", "title": "启动", "text": "定义目标", "icon": "flag" }
  ]
}
```

## Architecture

```json
{
  "type": "architecture",
  "nodes": [
    { "id": "web", "label": "Web App", "text": "React", "group": "Client" },
    { "id": "api", "label": "API", "text": "FastAPI", "group": "Backend" }
  ],
  "edges": [
    { "from": "web", "to": "api", "label": "HTTPS" }
  ]
}
```
