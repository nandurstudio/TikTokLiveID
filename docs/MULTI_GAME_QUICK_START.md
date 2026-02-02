# Multi-Game Configuration - Quick Start

## What's Changed

✅ **One Config File**: `config.json` contains ALL games  
✅ **Multiple Games**: NFS HEAT, GTA V, MINECRAFT (easily add more)  
✅ **Per-Game Settings**: Each game has unique mappings, cooldown, hold duration  
✅ **Game Selection**: Launcher asks which game when starting  

## File Structure

```
config.json
├── active_game: "NFS HEAT"
├── username: "nandurstudio"
└── games:
    ├── NFS HEAT
    │   ├── debug_mode: true
    │   ├── cooldown: 0.3
    │   ├── hold_duration: 2.0
    │   └── custom_mappings: { ... }
    ├── GTA V
    │   └── custom_mappings: { ... }
    └── MINECRAFT
        └── custom_mappings: { ... }
```

## How To Use

### 1. Launch Application
```powershell
python launcher.py
```

### 2. Select Mode
```
SELECT MODE
1. REAL TikTok
2. MOCK

Choose mode (1 or 2): 1
```

### 3. Select Debug
```
SELECT DEBUG MODE
Use DEBUG mode? (yes/no): yes
```

### 4. Select Game
```
SELECT GAME
1. NFS HEAT [CURRENT]
2. GTA V
3. MINECRAFT

Choose game (1-3): 1
```

### 5. Pre-flight Check
```
PRE-FLIGHT CHECKLIST
STEP 1: USERNAME VALIDATION
Enter your TikTok username (without @): nandurstudio
Username valid: @nandurstudio

STEP 2: CHECKING IF STREAM IS LIVE
Checking @nandurstudio...
Stream is LIVE!
```

### 6. Connected!
```
[CONNECTED] @nandurstudio (Room ID: 7602255114040773394)
Game: NFS HEAT | Racing Game Controller [DEBUG MODE]
```

## Adding New Game

1. Open `config.json`
2. Add new game under `games`:

```json
"FORZA HORIZON": {
  "debug_mode": true,
  "cooldown": 0.3,
  "hold_duration": 2.0,
  "custom_mappings": {
    "gas": "w",
    "rem": "s",
    ...
  }
}
```

3. Restart launcher
4. New game will appear in selection list!

## Editing Command Mappings

### Example: Change horn key in NFS HEAT

Edit `config.json`:
```json
"NFS HEAT": {
  "custom_mappings": {
    "horn": "h",        ← Current
    ...
  }
}
```

Change to:
```json
"NFS HEAT": {
  "custom_mappings": {
    "horn": "y",        ← New key
    ...
  }
}
```

Save and restart launcher.

## Common Commands

### NFS HEAT
```
gas / maju / w           → Accelerate
rem / mundur / s         → Brake
kiri / a                 → Turn left
kanan / d                → Turn right
drift / handbrake        → Drift
nitro / nos / shift      → Nitro boost
ws                       → Drift maneuver (W+S)
wd                       → Forward turn right (W+D)
```

### GTA V
```
w / s / a / d           → Basic movement
space                   → Jump/interaction
shift                   → Run
h                       → Horn
```

### MINECRAFT
```
w / maju                → Move forward
s / mundur              → Move backward
a / kiri                → Strafe left
d / kanan               → Strafe right
space / lompat / jump   → Jump
shift / sprint          → Sprint
```

## Tips

💡 **Pro Tips**
- Use debug mode first to test new games
- Keep cooldown 0.3-0.5 for smooth control
- Hold duration depends on game (2.0s for racing, 1.5s for action)
- Custom mappings let viewers use Indonesian commands

🎮 **Best Settings**
- Racing games: hold_duration 2.0s, cooldown 0.3s
- Minecraft: hold_duration 1.5s, cooldown 0.2s
- GTA: hold_duration 2.0s, cooldown 0.3s

## File Locations

- `config.json` - Main configuration
- `launcher.py` - Game launcher
- `examples/racing_game_controller.py` - Core controller
- `docs/MULTI_GAME_CONFIG.md` - Detailed documentation

## Need Help?

See `docs/MULTI_GAME_CONFIG.md` for:
- Detailed configuration guide
- Adding custom games
- Troubleshooting
- JSON format validation

See `COMMANDS_REFERENCE.md` for:
- All available commands
- Custom mapping examples
- Key codes and special keys

## Summary

Old way: Multiple config files (racing_config.json, gta_config.json, etc.)  
**New way**: One config.json with all games, select at startup

Clean, simple, organized! ✨
