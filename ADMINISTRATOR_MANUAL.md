# JARVIS AI OS - Administrator & Systems Manual

This manual is for administrators, engineers, and support teams managing JARVIS AI OS deployments.

---

## ⚙️ Configuration Management

System settings are managed using the `.env` file in the root workspace directory.

### Key Configuration Variables

| Key | Default | Description |
| :--- | :--- | :--- |
| `JARVIS_ENV` | `development` | Setting environment stage (`development`, `production`). |
| `LOG_LEVEL` | `INFO` | Standard log filter level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `OPENAI_API_KEY` | (None) | OpenAI account API key. |
| `GEMINI_API_KEY` | (None) | Gemini account API key. |
| `VOICE_ENABLED` | `true` | Turns wake word and speech engine on or off. |
| `STT_PROVIDER` | `google` | Choice of Speech-To-Text provider. |
| `VISION_ENABLED` | `false` | Enables webcam loops and active frame OCR analysis. |
| `ALLOW_UNSAFE_COMMANDS`| `false` | Security guardrail for automation scripts. |

---

## 🗄️ Database Management

All relational memories, intent contexts, configuration metrics, and research caching records are persisted in a local SQLite file:
* **Default Database Path**: `jarvis_memory.db`
* **Journal Mode**: Write-Ahead Logging (WAL) for concurrent read/write stability.

### Schema Tables
1. `memories`: Key-value storage of facts and user profiles.
2. `research_cache`: Queries, scraped sources lists, and compiled reports.
3. `diagnostics_logs`: Session histories and system alerts.

---

## 📁 Rotating Logs

Core server outputs are recorded and rotated:
* **Log Location**: `logs/jarvis.log`
* **Rotation Policy**: Rotates when log size reaches 5MB. Retains up to 5 historical log backups.
* **Format**: Standard JSON log format or structured console logs.
