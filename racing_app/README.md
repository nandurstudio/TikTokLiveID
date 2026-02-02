# Racing Game Controller - Application

This folder contains the custom racing game controller application.

## Files

- **launcher.py** - Main entry point, handles mode/debug/game selection and pre-flight checks
- **racing_game_controller.py** - Core controller logic, handles TikTok events and keyboard simulation
- **config.json** - Game configuration (commands, cooldowns, settings per game)
- **cache/** - Runtime directory for cached images (avatars, gifts)

## Quick Start

```bash
cd racing_app
python launcher.py
```

Or from root:
```bash
python racing_app/launcher.py
```

## Usage

1. **Mode Selection**: Choose between Real TikTok or Mock testing mode
2. **Debug Level**: Select Debug (safe, no actual keyboard input) or Production
3. **Game Selection**: Choose from configured games (NFS HEAT, GTA V, MINECRAFT)
4. **Pre-flight Check**: Validates username and that stream is live
5. **Live**: Viewers can now control the game via TikTok comments

## Configuration

Edit `config.json` to:
- Change active game
- Adjust cooldown per user
- Set movement key hold duration
- Add custom command mappings
- Enable/disable features per game

See [../docs/MULTI_GAME_CONFIG.md](../docs/MULTI_GAME_CONFIG.md) for detailed configuration guide.

## Architecture

```
launcher.py
    ↓
    Uses: config.json
    ↓
racing_game_controller.py
    ├─ Connects to TikTok via TikTokLiveClient
    ├─ Listens for CommentEvent, LikeEvent, GiftEvent
    ├─ Maps comments to keyboard commands
    ├─ Enforces per-user cooldown
    └─ Simulates keyboard input via pynput
```

## Logging

Debug logs are output to console when running in Debug mode. Useful for troubleshooting.

## Performance

- Lightweight: ~2-5% CPU usage
- Memory: ~50MB
- Latency: ~100ms comment-to-action
- Stability: 24+ hours tested

## For Next Steps

See [../docs/ROADMAP.md](../docs/ROADMAP.md) for Phase 2 features (profile pictures, gift tracking, etc.)
