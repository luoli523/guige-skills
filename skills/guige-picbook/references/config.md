# guige-picbook Configuration

The runtime reads normal process environment variables and these dotenv files:

```text
~/.guige-skills/.env
~/.guige-skills/guige-picbook/.env
./.guige-skills/.env
./.guige-skills/guige-picbook/.env
```

Process environment variables override dotenv values. Later dotenv files override earlier
dotenv files. The skill does not read plain `./.env` by default; use
`./.guige-skills/guige-picbook/.env` for project-local overrides.

## LLM

Set one provider and make it the default:

```bash
DEFAULT_LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=...
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

Supported providers:

| Provider | Key | Model var |
|----------|-----|-----------|
| `anthropic` | `ANTHROPIC_API_KEY` | `ANTHROPIC_MODEL` |
| `openai` | `OPENAI_API_KEY` | `OPENAI_MODEL` |
| `gemini` | `GOOGLE_API_KEY` | `GEMINI_MODEL` |
| `grok` | `GROK_API_KEY` | `GROK_MODEL` |

Optional:

```bash
OPENAI_BASE_URL=https://api.openai.com/v1
XAI_BASE_URL=https://api.x.ai/v1
MAX_TOKENS=4096
```

## Search

Search is best with Tavily or SerpAPI, but the generator can fall back to Wikipedia and LLM knowledge.

```bash
TAVILY_API_KEY=...
SERP_API_KEY=...
```

## NotebookLM

```bash
NOTEBOOKLM_NOTEBOOK_NAME=儿童绘本
```

Then run:

```bash
python3.11 skills/guige-picbook/scripts/main.py setup
notebooklm login
```

## Telegram

```bash
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

## Output

```bash
OUTPUT_DIR=./picbook
```
