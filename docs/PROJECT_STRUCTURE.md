# Project Structure Guide

## Overview

This project maintains **two separate concerns**:

1. **TikTokLive Library** (Original - Read Only)
   - Source: `TikTokLive/` folder
   - From: https://github.com/isaackogan/TikTokLive
   - Purpose: Unofficial Python API for TikTok LIVE
   - Status: Original, unchanged

2. **Racing Game Controller** (Custom Application)
   - Source: `racing_app/` folder
   - Purpose: Real-time TikTok viewer game control
   - Build on top of TikTokLive library

---

## Directory Tree

```
TikTokLiveID/
│
├── TikTokLive/                    ← LIBRARY (do not modify)
│   ├── client/
│   │   ├── base.py
│   │   ├── client.py
│   │   ├── config.py
│   │   └── httpx.py
│   ├── proto/
│   │   ├── tiktok_schema_pb2.py
│   │   ├── tiktok_schema.proto
│   │   └── utilities.py
│   ├── types/
│   │   ├── errors.py
│   │   ├── events.py
│   │   └── objects.py
│   ├── __init__.py
│   └── utils.py
│
├── examples/                      ← LIBRARY EXAMPLES (reference)
│   ├── basic.py
│   ├── avatars.py
│   ├── discord.py
│   ├── gifts.py
│   └── ... (other examples)
│
├── racing_app/                    ← CUSTOM APPLICATION
│   ├── launcher.py               ← Main entry point
│   ├── racing_game_controller.py ← Core logic
│   ├── config.json              ← Game settings
│   ├── README.md                ← App documentation
│   ├── cache/                   ← Runtime cache
│   │   ├── avatars/            ← Profile pictures
│   │   └── gifts/              ← Gift icons
│   └── __init__.py
│
├── docs/                         ← ALL DOCUMENTATION
│   ├── QUICK_START.md           ← Getting started (5 min)
│   ├── ROADMAP.md               ← Phase 1-3 plan
│   ├── COMMANDS_REFERENCE.md    ← Available commands
│   ├── LIVE_CONTROLLER_GUIDE.md ← Features overview
│   ├── MULTI_GAME_CONFIG.md     ← Game configuration
│   ├── MULTI_GAME_QUICK_START.md
│   ├── COMBINATION_KEYS_GUIDE.md
│   ├── MOVEMENT_HOLD_GUIDE.md
│   ├── JSON_CONFIG_GUIDE.md
│   ├── RACING_GAME_GUIDE.md
│   ├── TESTING_GUIDE.md
│   ├── PHASE_2_CHECKLIST.md    ← What to build next
│   ├── PROJECT_STATUS.md       ← Project overview
│   ├── CLEANSING_SUMMARY.md    ← Historical cleanup
│   └── FINAL_SUMMARY.md        ← Final project state
│
├── ROOT FILES
│   ├── README.md               ← Main project readme
│   ├── LICENSE                 ← MIT License
│   ├── requirements.txt        ← Python dependencies
│   ├── pyproject.toml         ← Project metadata
│   ├── .gitignore             ← Git ignore rules
│   └── .gitattributes         ← Git attributes
│
└── scripts/                     ← UTILITIES (if any)
```

---

## Key Points

### TikTokLive Library
- **Location**: `TikTokLive/` folder
- **Status**: Read-only, original from GitHub
- **Do Not Modify**: Changes would break compatibility
- **Version**: As per `requirements.txt`

### Racing Application
- **Location**: `racing_app/` folder
- **Entry Point**: `python racing_app/launcher.py`
- **Configuration**: `racing_app/config.json`
- **Cache**: `racing_app/cache/` (auto-created at runtime)
- **Code**: `launcher.py` + `racing_game_controller.py`

### Documentation
- **Location**: `docs/` folder
- **No Redundancy**: Check existing docs before creating new ones
- **Update Only**: If better than existing, update rather than create new
- **Single Source of Truth**: Each topic has ONE authoritative doc

### Root Files
- **Entry Point**: `python racing_app/launcher.py`
- **Config**: In `racing_app/` folder
- **Dependencies**: `requirements.txt`
- **Project Info**: `README.md`

---

## Development Workflow

### Modifying TikTokLive Library
```
❌ DO NOT MODIFY - Keep original
  (If needed for custom feature, create wrapper in racing_app/)
```

### Adding Racing App Features
```
racing_app/
├── New feature code
├── Update racing_game_controller.py
└── Update config.json if needed
```

### Adding Documentation
```
1. Check docs/ folder for existing docs
2. If exists: UPDATE it
3. If new: Create in docs/ only (not in root)
4. Reference other docs with relative links
```

### Adding Dependencies
```
1. pip install package_name
2. Update requirements.txt
3. Test with racing_app/launcher.py
```

---

## File Organization Rules

### DO:
- ✅ Keep TikTokLive library untouched
- ✅ Put all .md files in `docs/` folder
- ✅ Keep racing_app code in `racing_app/` folder
- ✅ Config in `racing_app/config.json`
- ✅ Check existing docs before creating new ones
- ✅ Update docs instead of creating duplicates

### DON'T:
- ❌ Modify TikTokLive/ folder code
- ❌ Create .md files in root
- ❌ Create duplicate documentation
- ❌ Move library files
- ❌ Mix library and app code
- ❌ Create redundant guides

---

## Import Paths

### Correct (from racing_app):
```python
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, GiftEvent
from racing_game_controller import RacingGameController
import config  # config.json in same folder
```

### Wrong:
```python
from ..TikTokLive import ...  # Incorrect path
from racing_game_controller import ...  # From root (wrong)
from config import ...  # Won't work
```

---

## Running the Application

### From Root:
```bash
python racing_app/launcher.py
```

### From racing_app/:
```bash
python launcher.py
```

### With Config:
- Config loaded from: `racing_app/config.json`
- Relative paths work from wherever you run from

---

## Git Workflow

### Files to Commit:
```
racing_app/*.py
racing_app/config.json
racing_app/README.md
docs/*.md
README.md
requirements.txt
.gitignore
```

### Files NOT to Commit:
```
racing_app/cache/*       ← Auto-created
*.log                    ← Runtime logs
*.pyc                    ← Compiled Python
__pycache__/            ← Python cache
venv/                   ← Virtual env
.env                    ← Secrets (if used)
```

---

## Quick Reference

| Item | Location | Purpose |
|------|----------|---------|
| Entry Point | `racing_app/launcher.py` | Start the app |
| Controller Logic | `racing_app/racing_game_controller.py` | Core functionality |
| Configuration | `racing_app/config.json` | Game settings |
| Documentation | `docs/*.md` | All guides |
| Library | `TikTokLive/` | Read-only |
| Examples | `examples/` | Reference only |

---

## For Contributors

1. **Before Creating New Docs**
   - Check `docs/` folder
   - If similar exists: UPDATE it
   - If new: CREATE in docs/

2. **Before Modifying Code**
   - If in `TikTokLive/`: DON'T (unless critical bug)
   - If in `racing_app/`: YES, create features here

3. **Before Committing**
   - Check `.gitignore`
   - Don't commit cache or runtime files
   - Update docs if needed

---

**Last Updated**: After restructuring  
**Status**: Production-ready  
**Next Phase**: See [ROADMAP.md](ROADMAP.md)
