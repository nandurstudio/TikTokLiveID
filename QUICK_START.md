# ⚡ Quick Start Guide

## 1️⃣ Setup (5 menit)

```bash
# Clone atau download project
git clone https://github.com/isaackogan/TikTokLive.git
cd TikTokLiveID

# Install dependencies
pip install TikTokLive pynput

# (Opsional) Install advanced deps
pip install pygame  # Untuk pygame examples
```

## 2️⃣ Testing (10 menit) - HIGHLY RECOMMENDED!

### A. Mock Testing (NO TIKTOK CONNECTION)
```bash
python examples/test_mock.py
```
✅ **Output:** Lihat virtual comments diproses tanpa risiko
- Paling aman untuk dev
- Test logic tanpa TikTok
- Bisa repeat unlimited

### B. Debug Mode (SAFE TIKTOK CONNECTION)
Edit `examples/chat_to_keys.py`:
```python
TIKTOK_USERNAME = "your_username"  # Ganti username kamu
DEBUG_MODE = True                   # Safe mode - no keyboard input
```

Jalankan:
```bash
python examples/chat_to_keys.py
```
✅ **Output:** Live comments diterima, tapi keyboard tidak ditekan
- Safe untuk test dengan real stream
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
