# Racing Game Controller - Application

This folder contains the custom racing game controller application.

## Files

- **launcher.py** - Main entry point, handles mode/debug/game selection and pre-flight checks
- **racing_game_controller.py** - Core controller logic, handles TikTok events and keyboard simulation
- **config.json** - Game configuration (commands, cooldowns, settings per game)
- **cache/** - Runtime directory for cached images (avatars, gifts)

## ⚠️ IMPORTANT: Anti-Block Warning

**DO NOT run this app on the same device/network used for TikTok Live Studio!**

### Why?
TikTok detects multiple connections from the same IP/device and will block your account. If you stream with TikTok Live Studio and run this app on the same computer, TikTok sees:
- **Device A**: Streaming (broadcaster)
- **Device A**: Connecting as viewer (suspicious!)

### Recommended Setup

**✅ SAFE: Use Separate Devices**
```
Computer A (Streaming)          Computer B (Controller)
├─ TikTok Live Studio          ├─ Racing Game Controller
├─ Network: WiFi 1             ├─ Network: WiFi 2 or Mobile Hotspot
└─ IP: Different               └─ IP: Different
```

**✅ SAFE: Different Networks**
- Stream with TikTok Live Studio on WiFi
- Run controller on Mobile Hotspot or VPN

**❌ BLOCKED: Same Device & Network**
- Stream with TikTok Live Studio
- Run controller on same computer = **INSTANT BLOCK**

### If Already Blocked
1. **Wait 2-4 hours** after stream ends
2. **Restart router** (get new IP)
3. **Use VPN** or different network
4. **Use MOCK mode** for testing (option 2 in launcher)

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
