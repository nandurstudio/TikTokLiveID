# Quick Start Guide - Racing Game Controller

## Installation (5 minutes)

```bash
# Clone the repository
git clone <repo-url>
cd TikTokLiveID

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### Simplest Way:
```bash
python racing_app/launcher.py
```

### Step-by-Step:
1. **Select Mode**
   - `Real TikTok` - Connect to actual stream
   - `Mock` - Test with simulated viewers (recommended for first time)

2. **Select Debug Level**
   - `Debug` - Safe mode (no actual keyboard input)
   - `Production` - Real mode (actual keyboard input to game)

3. **Select Game**
   - `NFS HEAT`
   - `GTA V`
   - `MINECRAFT`

4. **Confirm Username**
   - Enter your TikTok username
   - Launcher verifies you're live

5. **Live!**
   - Viewers can now type commands in chat
   - Their commands control your game

---

## Testing Modes (Recommended)

### Option 1: Mock Mode (Safest)
```bash
python racing_app/launcher.py
# Select: Mock → Debug → Any Game
```
✅ **Result**: Simulated viewers, no TikTok needed, no keyboard input
- Perfect for learning
- Test logic safely
- No risk to real stream

### Option 2: Debug Mode (Safe with Real TikTok)
```bash
python racing_app/launcher.py
# Select: Real → Debug → Your Game
```
✅ **Result**: Real TikTok stream, but no actual keyboard input
- See real comments processing
- Verify setup works
- No risk to game controls

### Option 3: Production Mode (Live)
```bash
python racing_app/launcher.py
# Select: Real → Production → Your Game
```
✅ **Result**: Full live mode - viewers control your game
- Only after testing above options
- Be ready to stop if needed

---

## Configuration

Edit `racing_app/config.json` to:
- Change active game
- Adjust command cooldown
- Set movement key duration
- Add custom command mappings

See [MULTI_GAME_CONFIG.md](MULTI_GAME_CONFIG.md) for details.

---

## Troubleshooting

### Application won't start
```bash
# Check Python version
python --version  # Need 3.8+

# Check dependencies
pip install -r requirements.txt

# Test if config is valid JSON
python -m json.tool racing_app/config.json
```

### TikTok connection fails
- Verify username is correct
- Make sure you're actually LIVE
- Check internet connection
- Try Mock mode first

### Commands don't work
- Use Debug mode to see what's happening
- Verify game window is focused
- Check key mappings in config.json
- Ensure cooldown isn't blocking

---

## Next Steps

1. **Test with Mock Mode** - Get comfortable
2. **Read [ROADMAP.md](ROADMAP.md)** - Understand what's possible
3. **Review [COMMANDS_REFERENCE.md](COMMANDS_REFERENCE.md)** - See all available commands
4. **Explore [docs/](.)** - Detailed guides for each feature
5. **Start Live** - You're ready!

---

## Documentation

All guides are in `docs/` folder:
- `PROJECT_STRUCTURE.md` - Folder organization
- `MULTI_GAME_CONFIG.md` - Game configuration
- `ROADMAP.md` - Phase 1-3 features
- `COMMANDS_REFERENCE.md` - All commands
- `TESTING_GUIDE.md` - Testing procedures

---

**You're ready! 🚀**
- Verify mapping works
- Lihat latency TikTok

## 3️⃣ Go Live! (Production)

Setelah sure semuanya work:

Edit `examples/chat_to_keys.py`:
```python
DEBUG_MODE = False  # ← CHANGE THIS
```

```bash
python examples/chat_to_keys.py
```

⚠️ **Sebelum jalankan:**
1. ✅ Mock testing sudah pass
2. ✅ Debug mode sudah test
3. ✅ Username benar
4. ✅ Game sudah berjalan & in-focus
5. ✅ Ready untuk viewers!

---

## 📋 Testing Checklist

```
STEP 1: Mock Testing
□ python examples/test_mock.py
□ Semua commands diproses
□ Key presses tercatat

STEP 2: Debug Mode
□ Edit chat_to_keys.py dengan username
□ Set DEBUG_MODE = True
□ python examples/chat_to_keys.py
□ Kirim comment dari akun TikTok lain
□ Lihat di console komentar diterima

STEP 3: Production
□ Set DEBUG_MODE = False
□ Game in-focus
□ Jalankan python examples/chat_to_keys.py
□ Test dengan beberapa comments
□ Kalau work, go live dengan viewers!
```

---

## 🎮 Cara Pakai Saat Live

1. **Buka game/app** yang mau dikontrol
2. **Fokus window** game (click di gamenya)
3. **Jalankan script:**
   ```bash
   python examples/chat_to_keys.py
   ```
4. **Viewers bisa ketik di chat:**
   - `w` atau `maju` = Move forward
   - `a` atau `kiri` = Move left  
   - `s` atau `mundur` = Move back
   - `d` atau `kanan` = Move right
   - `jump` atau `lompat` = Jump
   - `attack` atau `serang` = Attack

---

## 🛠️ Customize Mappings

Edit file `examples/config_template.py` atau modify di code:

```python
from examples.chat_to_keys import ChatToKeyController

controller = ChatToKeyController(unique_id="your_username")

# Add custom mappings
controller.add_mapping("spell1", "q")
controller.add_mapping("heal", "r")
controller.add_mapping("dash", "shift")

controller.run()
```

---

## ⚠️ Important Notes

### Rate Limiting
- Built-in cooldown: 0.1 detik/command
- Prevents spam yang bisa ban
- Modifiable: `cooldown_duration`

### TikTok Ban Risk
- ✅ Mock testing = 0% risk
- ✅ Debug mode = ~1% risk  
- ⚠️ Production = follow guidelines

**Don't:**
- Spam requests ke TikTok
- Gunakan dengan bot/automated viewers
- Make rapid connection/disconnection
- Violate TikTok ToS

### Troubleshooting

**"Error: unknown username"**
- Pastikan username tanpa `@`
- Username case-sensitive
- User sedang live?

**"Key tidak dipress di game"**
- Game window harus in-focus
- Check DEBUG_MODE = False
- Verify key nama benar di mapping

**"Connection timeout"**
- Check internet connection
- TikTok server might be down
- Wait beberapa menit, retry

---

## 📚 Next Steps

Setelah basic working:

1. **Add Overlay** - Visual feedback di OBS
2. **Gift Reactions** - Different actions for gifts
3. **User Whitelist** - Only allow certain users
4. **Spam Protection** - Per-user cooldowns
5. **Analytics** - Track commands sent

---

## 📖 Full Documentation

- [LIVE_CONTROLLER_GUIDE.md](../docs/LIVE_CONTROLLER_GUIDE.md) - Project overview
- [TESTING_GUIDE.md](../docs/TESTING_GUIDE.md) - Detailed testing procedures
- [config_template.py](config_template.py) - All configuration options

---

**Ready? Start with:** `python examples/test_mock.py`

Good luck! 🚀
