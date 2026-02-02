# 🏎️ Racing Game Controller - WASD Key Binding

Script untuk mengontrol racing game dari TikTok Live chat dalam real-time.

## 🎮 Supported Games

Setiap game yang menggunakan WASD controls:
- ✅ Minecraft Racing
- ✅ GTA (Grand Theft Auto)
- ✅ Roblox Racing Games
- ✅ Need for Speed
- ✅ Forza
- ✅ Beamng.drive
- ✅ Assetto Corsa
- ✅ Dan game racing lainnya

## 📦 Installation

```bash
# Install dependencies
pip install TikTokLive pynput
```

## ⚙️ Setup

### Step 1: Run Script

```bash
python examples/racing_game_controller.py
```

Script akan menampilkan interactive setup menu.

### Step 2: Answer Setup Questions

1. **TikTok Username** - Masukkan username (tanpa @)
2. **Operation Mode** - Pilih Debug atau Production
3. **Cooldown** - Default 0.2s (bisa ubah)
4. **Custom Mappings** - Optional (skip dengan "no")

### Step 3: Done!

Script otomatis start setelah setup selesai.

---

## 📝 Setup Details

### Question 1: TikTok Username
```
Enter your TikTok username (without @): nandurstudio
```
- Input tanpa tanda `@`
- Case-insensitive
- User harus sedang live

### Question 2: Operation Mode
```
Use Debug Mode? (yes/no): yes
```
- **yes** = Debug Mode (Recommended - aman, no keyboard input)
- **no** = Production Mode (Real keyboard input)

### Question 3: Cooldown Duration
```
Per-user cooldown duration (seconds) [0.2]: 0.2
```
- Default: 0.2 seconds
- Options: 0.1s (fast), 0.2s (balanced), 0.3s (slow)

### Question 4: Custom Mappings
```
Add custom key mappings? (yes/no) [no]: no
```
- **yes** = Add custom commands
- **no** = Skip (use defaults)

If yes, format: `command → key`

Examples:
- `horn → h`
- `engine → e`
- `menu → esc`

---

## 🎯 Key Mapping

### Basic Racing Controls

| Chat Command | Key | Fungsi |
|--------------|-----|--------|
| `w` | W | Gas / Maju |
| `forward` | W | Gas / Maju |
| `maju` | W | Gas / Maju |
| `gas` | W | Gas / Accelerate |
| `accelerate` | W | Accelerate |
| `s` | S | Brake / Mundur |
| `backward` | S | Mundur |
| `brake` | S | Brake |
| `reverse` | S | Reverse |
| `a` | A | Turn Left / Kiri |
| `left` | A | Left |
| `kiri` | A | Left |
| `d` | D | Turn Right / Kanan |
| `right` | D | Right |
| `kanan` | D | Right |
| `space` | Space | Jump / Lompat |
| `jump` | Space | Jump |
| `drift` | Space | Drift / Handbrake |
| `handbrake` | Space | Handbrake |
| `drift_left` | Q | Drift Left |
| `drift_right` | E | Drift Right |
| `nitro` | Shift | Nitro / Boost |
| `boost` | Shift | Boost |
| `turbo` | Shift | Turbo |

### Custom Commands
Edit `main()` function untuk add custom commands:

```python
# Uncomment dan ubah sesuai kebutuhan game kamu
controller.add_mapping("sprint", "shift")
controller.add_mapping("crouch", "ctrl")
controller.add_mapping("interact", "e")
controller.add_mapping("menu", "esc")
```

## ⚙️ Advanced Configuration

### Adjust Cooldown (Anti-Spam)

```python
controller.set_cooldown(
    per_user_duration=0.15,  # Cooldown per user (seconds)
    global_duration=0.05      # Global cooldown (optional)
)
```

**Explain:**
- `per_user_duration`: Cooldown antar command dari user yang sama
- `global_duration`: Cooldown global untuk semua users
- Default: 0.2s per user (mencegah spam)

### Custom Key Press Duration

Edit di dalam `__init__`:
```python
self.press_duration = 0.1  # Berapa lama key ditekan (seconds)
```

## 📊 Features

### ✅ Per-User Cooldown
Setiap user memiliki cooldown sendiri:
- Mencegah satu user spam commands
- Viewers lain bisa command secara bersamaan

### ✅ Real-time Logging
```
👤 Adi                  → 'w             ' ➜ w
👤 Budi                 → 'kanan         ' ➜ d
👤 Citra                → 'drift         ' ➜ space
👤 Dedi                 → 'nitro         ' ➜ shift
```

### ✅ Session Statistics
Otomatis print saat stream selesai:
```
📊 RACING SESSION STATISTICS
============================================================
Duration: 3600.5 seconds
Total Commands: 2850
Unique Users: 156
Commands/Second: 0.79

Top Commands:
  w                 →   750x
  d                 →   420x
  a                 →   380x
  s                 →   340x
  space             →   250x
  shift             →   180x
```

### ✅ Automatic Logging
- Semua activity di-log ke `racing_controller.log`
- Console output untuk realtime monitoring

## 🚀 Usage

### Scenario 1: Test dengan Debug Mode
```bash
# Edit file
# TIKTOK_USERNAME = "your_username"
# DEBUG_MODE = True

python examples/racing_game_controller.py

# Output:
# [DEBUG] Would press: w (0.1s)
# [DEBUG] Would press: d (0.1s)
```

✅ Aman - tidak tekan keyboard sebenarnya

### Scenario 2: Production dengan Real Account
```bash
# Edit file
# TIKTOK_USERNAME = "your_username"
# DEBUG_MODE = False

# PENTING: Game harus berjalan & in-focus!
python examples/racing_game_controller.py

# Viewers bisa ketik di chat:
# User: "w"        → Character maju
# User: "d"        → Character belok kanan
# User: "drift"    → Handbrake/Drift
# User: "nitro"    → Boost
```

⚡ Real keyboard input!

## ⚠️ Important Notes

### Before Going Live
- [ ] Test dengan `DEBUG_MODE = True` dulu
- [ ] Verify semua commands di-recognize
- [ ] Game sudah berjalan
- [ ] Game window in-focus (kalau tidak, keyboard tidak diproses game)
- [ ] Internet stable
- [ ] TikTok user sedang live

### Troubleshooting

**"Keys tidak diproses game"**
- Game window harus in-focus (click di game)
- Verify `DEBUG_MODE = False`
- Check TikTok username benar

**"Connection timeout"**
- Check internet connection
- Verify user sedang live
- Wait beberapa menit, retry

**"One user spamming commands"**
- Per-user cooldown mencegah ini
- Cooldown default: 0.2 detik per user
- Adjust dengan `set_cooldown()`

### Performance Tips

1. **Reduce Log Output**
   - Comment out `logging.FileHandler` untuk faster execution
   - Atau set `logging.basicConfig(level=logging.WARNING)`

2. **Optimize Cooldown**
   - Terlalu pendek (0.05s) → bisa "jittery"
   - Terlalu panjang (0.5s) → terasa lambat
   - Default 0.2s bagus untuk kebanyakan games

3. **Monitor Statistics**
   - Check `racing_controller.log` untuk analyze usage
   - Adjust commands/cooldown berdasarkan feedback

## 🎬 Example: Running Live Stream

```
1. Setup game (e.g., GTA, Minecraft Racing)
2. Open TikTok Live
3. Run: python examples/racing_game_controller.py
4. Share username di overlay/comments
5. Viewers ketik:
   - "w" atau "maju" → Gas
   - "a" atau "kiri" → Turn left
   - "d" atau "kanan" → Turn right
   - "s" atau "brake" → Brake
   - "drift" → Handbrake
   - "nitro" atau "turbo" → Boost
6. Watch character controlled by viewers!
```

## 📝 Logs

Log file: `racing_controller.log`

**Format:**
```
2026-02-02 19:45:30,123 - INFO - ✅ Connected to @nandurstudio (Room ID: 123456)
2026-02-02 19:45:31,456 - INFO - 🎮 Racing Game Controller [PRODUCTION MODE]
2026-02-02 19:45:35,789 - INFO - 👤 Adi                  → 'w             ' ➜ w
2026-02-02 19:45:36,234 - INFO - 👤 Budi                 → 'kanan         ' ➜ d
...
```

## 🔐 Security & Safety

✅ **Safe by Default**
- Debug mode prevents accidental keyboard presses
- Per-user cooldown prevents spam
- Error handling untuk connection issues

✅ **No Malicious Code**
- Open source
- Simple, readable code
- No credentials stored in script

⚠️ **TikTok Guidelines**
- Normal connection patterns
- Reasonable request rates
- Not spam/abuse

## 📚 File Reference

- `racing_game_controller.py` - Main script
- `racing_controller.log` - Automatic log file
- `config_template.py` - Configuration reference

## 🤝 Customize Further

### Add Game-Specific Commands
```python
# For GTA
controller.add_mapping("horn", "h")
controller.add_mapping("handbrake", "space")
controller.add_mapping("engine", "e")

# For Minecraft Racing
controller.add_mapping("sneak", "shift")
controller.add_mapping("sprint", "ctrl")
```

### Add Event Reactions (Future)
Monitor chat for special events:
```python
# When someone donates gift
if event.type == "gift":
    await controller._press_key("space", duration=1.0)  # Drift!
```

---

**Status:** ✅ Production Ready

**Last Updated:** 2 Februari 2026

**Ready to race?** 🏎️💨
