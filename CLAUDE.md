# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an Obsidian vault (knowledge management system) with several automation tools and subprojects. The primary language is Japanese.

## Key Subprojects

### Discord勤怠報告分析 (`UnionAI_勤怠報告分析/`)
Automated Discord attendance reporting system.

```powershell
# Setup Discord token
cd "C:\ドキュメント\vault\UnionAI_勤怠報告分析"
.\setup_token.ps1 -Token "YOUR_DISCORD_TOKEN"

# Daily sync all members
python scripts/daily_sync.py

# Analyze efficiency (daily/weekly/monthly)
python scripts/analyze_efficiency.py -p daily -d 2026-01-22 --all
python scripts/analyze_efficiency.py -p weekly -d 2026-01-22 -m メンバー名

# Register scheduled task
.\scripts\register_daily_task.ps1
```

Configuration: `config/channels.json` maps member names to Discord channel IDs.

### Discord Claude Bot (`discord-claude-bot/`)
Bot that runs Claude Code via Discord mentions.

```bash
cd discord-claude-bot
npm install
npm start
```

Requires `.env` with `DISCORD_TOKEN`, `ALLOWED_USER_IDS`, and `WORKING_DIR`.

### Screenpipe Scripts (`screenpipe_all/scripts/`)
Screen activity capture and analysis automation.

```powershell
# Export raw data
.\scripts\run_export.cmd

# Hourly summary
.\scripts\run_hourly.cmd

# Daily summary
.\scripts\run_daily.cmd
```

Python scripts: `discord_export.py`, `analyze_kintai.py`

## Folder Structure

| Folder | Purpose |
|--------|---------|
| `00_Notes/` | General notes |
| `01_Daily/` | Daily notes |
| `02_Templates/` | Obsidian templates |
| `03_Sources/` | Source materials |
| `04_Books/` | Book notes |
| `inbox/` | Unsorted items |
| `LINE inbox/` | LINE message imports |
| `copilot/` | Copilot custom prompts |

## Working with This Vault

- Obsidian plugins are in `.obsidian/plugins/`
- Use `[[wikilinks]]` for internal links
- Templates use Templater plugin syntax
- Git is configured for vault backup (see `.gitignore`)

## Environment Requirements

- Python 3.7+ with `requests` library
- PowerShell 7+ (Windows)
- Node.js for discord-claude-bot
- Obsidian (for vault usage)
