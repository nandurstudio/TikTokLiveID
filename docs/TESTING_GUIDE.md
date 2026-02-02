# Testing Guide - Chat to WASD Controller

## 🔒 Safe Testing Strategy

### Phase 1: Mock Testing (RECOMMENDED FIRST)
**File:** `examples/test_mock.py`

Cara testing TANPA koneksi TikTok sama sekali:

```bash
python examples/test_mock.py
```

✅ **Keuntungan:**
- Tidak ada risiko banned TikTok
- Test logic dengan data simulasi
- Bisa modify test messages sesuai kebutuhan
- Repeat testing unlimited

---

### Phase 2: Debug Mode (SAFE CONNECTION)
**File:** `examples/chat_to_keys.py` dengan `DEBUG_MODE = True`

Cara connect ke TikTok tapi TIDAK tekan keyboard:

```python
# chat_to_keys.py
DEBUG_MODE = True  # ← Set ini ke True!
TIKTOK_USERNAME = "username_kamu"
```

Jalankan:
```bash
python examples/chat_to_keys.py
```

✅ **Keuntungan:**
- Connect ke TikTok real
- Log semua incoming comments
- Tidak tekan keyboard (safe!)
- Verify mapping logic bekerja

---

### Phase 3: Real Mode (PRODUCTION)
**File:** `examples/chat_to_keys.py` dengan `DEBUG_MODE = False`

Setelah sure logic bekerja:

```python
# chat_to_keys.py
DEBUG_MODE = False  # ← Set ke False untuk production
TIKTOK_USERNAME = "username_kamu"
```

Jalankan:
```bash
python examples/chat_to_keys.py
```

⚠️ **Precautions:**
1. Test dengan game yang berjalan dalam window
2. Jalankan di environment yang terisolasi dulu
3. Monitor untuk spam commands
4. Matikan saat tidak diperlukan

---

## 🛡️ Protection Against Ban

### Rate Limiting Built-in
- Default cooldown: 0.1 detik per command
- Prevents spam presses
- Modifiable: `self.cooldown_duration`

### Best Practices
1. **Test with mock first** - Always start with `test_mock.py`
2. **Use debug mode** - Connect to TikTok without pressing keys
3. **Monitor comments** - Check if mapping works correctly
4. **Start with low viewers** - Test with private stream or test account
5. **Monitor TikTok terms** - Don't spam or misuse

### If Rate Limited
TikTok might temporarily block if:
- Sending too many API requests
- Rapid repeated commands
- Suspicious connection patterns

**Solution:**
- Wait 15-30 minutes before reconnecting
- Increase cooldown duration
- Add per-user cooldowns (coming soon)

---

## 📊 Testing Checklist

- [ ] Run `test_mock.py` - Verify logic works
- [ ] Edit `chat_to_keys.py` - Set your username
- [ ] Set `DEBUG_MODE = True` - Safe connection
- [ ] Run `chat_to_keys.py` - Test with real stream
- [ ] Verify comments are logged correctly
- [ ] Test key mapping is accurate
- [ ] Check cooldown prevents spam
- [ ] Set `DEBUG_MODE = False` when ready
- [ ] First run with low activity stream
- [ ] Monitor for issues before full deployment

---

## 🔧 Customization

### Add New Mappings
```python
controller = ChatToKeyController(unique_id="username")

# Add custom mappings
controller.add_mapping("spell1", "q")
controller.add_mapping("spell2", "e")
controller.add_mapping("heal", "r")
```

### Adjust Cooldown
```python
controller.cooldown_duration = 0.05  # Faster (more spam risk)
controller.cooldown_duration = 0.5   # Slower (less spam)
```

### Per-User Cooldowns (Advanced)
Modify `_handle_comment()` to add user-specific cooldowns:
```python
user_key = f"{event.user.unique_id}:{command}"
# Check cooldown per user
```

---

## 📝 Logs

### What to Look For
- ✅ `Connected to @username` - Successfully connected
- ✅ `[KEY PRESS]` - Mapping working
- ⚠️ `Cooldown` - Command ignored (too fast)
- ❌ `Error` - Connection or input issues

### Debug Logs Example
```
✅ Connected to @nandurstudio (Room ID: 123456)
👤 Adi -> w ➜ w
👤 Budi -> maju ➜ w
👤 Citra -> jump ➜ space
```

---

## ❌ Troubleshooting

### "Already up to date" or Connection Error
- Check TikTok username is correct
- Ensure internet connection is stable
- Verify user is currently live

### Comments not being registered
- Check cooldown isn't too strict
- Verify mapping is added
- Enable logging: `logging.basicConfig(level=logging.DEBUG)`

### Keyboard not working in game
- Ensure game window is in focus
- Check `DEBUG_MODE = False`
- Verify pynput is installed: `pip install pynput`

### TikTok blocking connection
- Wait 15-30 minutes
- Reduce request frequency
- Use sign_api_key for higher limits (optional)

---

## 📚 Next Steps

After successful testing:
1. Deploy to your streaming environment
2. Add visual feedback (OBS overlay)
3. Implement gift reactions
4. Add user whitelist/blacklist
5. Create moderation commands

---

**Last Updated:** 2 Februari 2026
**Status:** Production Ready ✅
