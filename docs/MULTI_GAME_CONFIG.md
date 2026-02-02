# Multi-Game Configuration System

## Overview
Satu file `config.json` dapat menyimpan konfigurasi untuk multiple games. Setiap game memiliki unique key mappings, cooldown, dan hold duration sendiri.

## Config Structure

```json
{
  "active_game": "NFS HEAT",
  "username": "nandurstudio",
  "games": {
    "NFS HEAT": {
      "debug_mode": true,
      "cooldown": 0.3,
      "hold_duration": 2.0,
      "custom_mappings": { ... }
    },
    "GTA V": {
      "debug_mode": true,
      "cooldown": 0.3,
      "hold_duration": 2.0,
      "custom_mappings": { ... }
    },
    "MINECRAFT": {
      "debug_mode": true,
      "cooldown": 0.3,
      "hold_duration": 1.5,
      "custom_mappings": { ... }
    }
  }
}
```

## Key Fields

### Top Level
- **`active_game`** (string) - Default game to display when selecting (untuk kenyamanan user)
- **`username`** (string) - TikTok username yang sama untuk semua game

### Per-Game Config
- **`debug_mode`** (boolean) - Debug atau production mode
- **`cooldown`** (float) - Per-user cooldown dalam detik
- **`hold_duration`** (float) - Durasi hold untuk movement keys (W/A/S/D)
- **`custom_mappings`** (object) - Command → Key mapping untuk game tersebut

## Launcher Flow

### Game Selection Process

```
launcher.py
  ↓
Load config.json
  ↓
Select Mode (Real/Mock)
  ↓
Select Debug (Yes/No)
  ↓
SELECT GAME:
1. NFS HEAT [CURRENT]
2. GTA V
3. MINECRAFT

Choose game (1-3): 1
  ↓
Load NFS HEAT config
  ↓
Pre-flight checklist (username validation)
  ↓
Create controller with game-specific settings
  ↓
Connect to TikTok LIVE
  ↓
Display: Game: NFS HEAT | [CONNECTED] @nandurstudio
```

## Adding New Game

Edit `config.json` dan tambahkan game baru:

```json
{
  "active_game": "NFS HEAT",
  "username": "nandurstudio",
  "games": {
    "NFS HEAT": { ... },
    "GTA V": { ... },
    "MINECRAFT": { ... },
    "FORZA HORIZON": {
      "debug_mode": true,
      "cooldown": 0.3,
      "hold_duration": 2.0,
      "custom_mappings": {
        "gas": "w",
        "maju": "w",
        "rem": "s",
        ...
      }
    }
  }
}
```

Restart launcher, Forza Horizon akan muncul di game selection list.

## Example: Switching Games

### Scenario: User ingin ganti dari NFS HEAT ke GTA V

```
$ python launcher.py

SELECT GAME
1. NFS HEAT [CURRENT]
2. GTA V
3. MINECRAFT

Choose game (1-3): 2

[LOADED] Game: GTA V
[LOADED] User: @nandurstudio

[Pre-flight checklist...]
[CONNECTED] @nandurstudio (Room ID: xxxxx)
Game: GTA V | Racing Game Controller [DEBUG MODE]
```

GTA V config akan di-load:
- cooldown: 0.3s
- hold_duration: 2.0s
- custom_mappings untuk GTA V

## Customization Guide

### Mengubah Command Mapping untuk Game Tertentu

Edit `config.json`, cari game yang diinginkan:

```json
"GTA V": {
  "debug_mode": true,
  "cooldown": 0.3,
  "hold_duration": 2.0,
  "custom_mappings": {
    "gas": "w",          ← Change this
    "maju": "w",
    "rem": "s",
    ...
  }
}
```

Contoh: untuk GTA V, ubah "horn" mapping:

```json
"custom_mappings": {
  "gas": "w",
  "horn": "e",         ← Changed from "h"
  "klakson": "e"
}
```

### Per-Game Hold Duration

Minecraft bisa pakai hold_duration lebih pendek (1.5s) karena movement cepat:

```json
"MINECRAFT": {
  "hold_duration": 1.5,  ← Shorter for fast-paced game
  ...
}
```

NFS HEAT bisa pakai 2.0s untuk smooth drift:

```json
"NFS HEAT": {
  "hold_duration": 2.0,  ← Longer for racing
  ...
}
```

## File Format Notes

### Valid JSON Structure
```json
{
  "active_game": "string",
  "username": "string",
  "games": {
    "GAME_NAME": {
      "debug_mode": boolean,
      "cooldown": number (float),
      "hold_duration": number (float),
      "custom_mappings": {
        "command": "key",
        ...
      }
    }
  }
}
```

### Common Mistakes ❌

```json
// WRONG: Trailing comma
"games": {
  "NFS HEAT": { ... },
  "GTA V": { ... },  ← This comma is invalid!
}

// WRONG: Unquoted keys
{
  active_game: "NFS HEAT",  ← Should be "active_game"
}

// WRONG: Single quotes
{
  'username': 'nandurstudio'  ← Should be double quotes
}
```

## Debug Tips

### Validate JSON
```powershell
Get-Content config.json | ConvertFrom-Json
```
Jika error → JSON format salah

### List Available Games
```powershell
Get-Content config.json | ConvertFrom-Json | Select-Object -ExpandProperty games | Get-Member -MemberType NoteProperty | Select-Object Name
```

### Check Active Game
```powershell
(Get-Content config.json | ConvertFrom-Json).active_game
```

## Best Practices

✅ **Do**
- Keep config.json well-formatted (use JSON formatter)
- Use same username for all games
- Document custom mappings for each game
- Backup config.json regularly
- Test new game mapping in debug mode first

❌ **Don't**
- Mix game configs in multiple files
- Use different usernames per game
- Leave trailing commas
- Use single quotes
- Edit during runtime (close launcher first)

## Troubleshooting

### Q: Game selection tidak muncul?
**A**: Check if config.json has valid JSON format. Run:
```powershell
Get-Content config.json | ConvertFrom-Json
```

### Q: Config tidak load untuk game tertentu?
**A**: Verify game name spelling matches exactly:
```json
"NFS HEAT"  ← Exact match required
```

### Q: Semua games pakai same settings?
**A**: Normal! Modifikasi per-game di config.json:
```json
"NFS HEAT": { "cooldown": 0.3, ... },
"GTA V": { "cooldown": 0.4, ... }  ← Different cooldown
```

## File Location

- **Config file**: `config.json` (root folder)
- **No other config files needed** - everything in one file
- **Backup location**: Optional but recommended

## Example Complete Config

```json
{
  "active_game": "NFS HEAT",
  "username": "nandurstudio",
  "games": {
    "NFS HEAT": {
      "debug_mode": true,
      "cooldown": 0.3,
      "hold_duration": 2.0,
      "custom_mappings": {
        "gas": "w",
        "maju": "w",
        "w": "w",
        "rem": "s",
        "mundur": "s",
        "s": "s",
        "kiri": "a",
        "a": "a",
        "kanan": "d",
        "d": "d",
        "drift": "space",
        "nitro": "shift",
        "horn": "h"
      }
    },
    "GTA V": {
      "debug_mode": true,
      "cooldown": 0.3,
      "hold_duration": 2.0,
      "custom_mappings": {
        "gas": "w",
        "rem": "s",
        "kiri": "a",
        "kanan": "d",
        "horn": "h"
      }
    },
    "MINECRAFT": {
      "debug_mode": true,
      "cooldown": 0.3,
      "hold_duration": 1.5,
      "custom_mappings": {
        "maju": "w",
        "mundur": "s",
        "kiri": "a",
        "kanan": "d",
        "lompat": "space",
        "sprint": "shift"
      }
    }
  }
}
```

Sekarang Anda bisa easily manage multiple games dengan satu config file! 🎮
