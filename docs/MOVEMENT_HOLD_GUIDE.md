# Movement Key Hold Feature

## Overview
Saat viewer mengetik command W/A/S/D (movement keys), sekarang sistem akan **menahan key tersebut selama 5 detik** (atau durasi yang Anda atur), bukan hanya sekali sentuh. Ini membuat karakter bergerak lebih natural di racing game.

## Perilaku Default

### Movement Keys (Held for Duration)
Ketika ditekan, key ini akan **ditahan** selama durasi yang sudah dikonfigurasi (default 5 detik):

| Command | Key | Behavior | Hasil |
|---------|-----|----------|-------|
| `w` / `forward` / `maju` / `gas` | W | Hold 5s | Mobil akselerasi terus 5 detik |
| `a` / `left` / `kiri` | A | Hold 5s | Mobil belok kiri 5 detik |
| `s` / `backward` / `mundur` / `brake` | S | Hold 5s | Mobil mundur/rem 5 detik |
| `d` / `right` / `kanan` | D | Hold 5s | Mobil belok kanan 5 detik |

### Other Keys (Pressed Briefly)
Key lainnya akan **dipres sebentar** (~0.1 detik):

| Command | Key | Behavior | Hasil |
|---------|-----|----------|-------|
| `space` / `jump` / `lompat` | SPACE | Brief press | Jump sekali |
| `drift` / `handbrake` | SPACE | Brief press | Drift sekali |
| `shift` / `nitro` / `boost` | SHIFT | Brief press | Boost sekali |

## Konfigurasi Hold Duration

### Saat Setup Interaktif
```
🎮 MOVEMENT KEY HOLD DURATION
------------------------------------------
When viewers press W/A/S/D, how long to hold the key?
Recommended: 3-5 seconds
(Other keys like SPACE, SHIFT will be pressed briefly)

Hold duration for W/A/S/D (seconds): 5
✓ Hold Duration: 5s for W/A/S/D
```

### Default Values
- **Default hold duration**: 5 detik
- **Default press duration** (for other keys): 0.1 detik
- **Recommended range**: 3-5 detik

### Mengubah via Code
```python
# Setelah create controller
controller = RacingGameController("@username")

# Ubah hold duration
controller.set_hold_duration(4.0)  # Ubah ke 4 detik

# Atau di launcher (otomatis dari config)
if config.get("hold_duration"):
    controller.set_hold_duration(config.get("hold_duration"))
```

## File Config JSON

```json
{
  "username": "nandurstudio",
  "debug_mode": true,
  "cooldown": 0.3,
  "hold_duration": 5.0,
  "custom_mappings": {
    "horn": "h",
    "nitro": "shift"
  }
}
```

**Field baru**: `hold_duration` (float) - durasi dalam detik untuk menahan W/A/S/D

## Flow Execution

### Contoh 1: Viewer ketik "W"
```
[Input] Viewer: "w"
  ↓
[Check] Is mapped? Yes → W key
  ↓
[Check] Is movement key (W/A/S/D)? Yes!
  ↓
[Hold] Press W key for 5 seconds
  ↓
[Release] Release W key
  ↓
[Log] "username → 'w' => w (held 5s)"
```

### Contoh 2: Viewer ketik "SPACE"
```
[Input] Viewer: "space"
  ↓
[Check] Is mapped? Yes → SPACE key
  ↓
[Check] Is movement key (W/A/S/D)? No
  ↓
[Press] Press SPACE key for 0.1 seconds
  ↓
[Release] Release SPACE key
  ↓
[Log] "username → 'space' => space"
```

## Penggunaan

### Real Mode
```powershell
$ python launcher.py

SELECT MODE
1. REAL TikTok

Choose mode (1 or 2): 1

[Pre-flight checks...]

MOVEMENT KEY HOLD DURATION
Hold duration for W/A/S/D (seconds): 5
✓ Hold Duration: 5s for W/A/S/D

[STARTING] Racing Game Controller...

# Viewer mengetik "w" di chat
# → Karakter akan terus bergerak maju selama 5 detik!
```

### Debug Mode
```
[DEBUG] Would hold: w (5s)
[DEBUG] Would hold: a (5s)
[DEBUG] Would press: space (0.1s)
```
*Tidak ada actual keyboard input, hanya logging.*

## Log Output

```
2026-02-02 20:30:00 - INFO - [HOLD] Movement keys (W/A/S/D) will be held for 5s
2026-02-02 20:30:05 - INFO - viewer_123        -> 'w' => w (held 5s)
2026-02-02 20:30:10 - INFO - viewer_456        -> 'a' => a (held 5s)
2026-02-02 20:30:15 - INFO - viewer_789        -> 'space' => space
```

## Timing Notes

### Cooldown Behavior
- **Cooldown timing**: Dimulai **sebelum** key di-hold
- **Jika hold duration 5s** dan **cooldown 0.3s per user**, user tersebut tidak bisa command lagi sampai 5s+ selesai ditambah cooldown reset

### Contoh Timeline:
```
T=0.0s  → User A ketik "w"
T=0.0s  → Cooldown User A reset = 0.3s
T=0.0s  → Press W, hold for 5s
T=0.3s  → Cooldown User A selesai, bisa command lagi
T=5.0s  → Release W key
```

**Jadi meskipun hold 5 detik, cooldown reset immediate**, memungkinkan user ketik command lagi setelah cooldown selesai.

## Advanced Configuration

### Mengubah Hold Duration Dinamis

```python
from examples.racing_game_controller import RacingGameController

# Create controller
controller = RacingGameController("@username")

# Ubah hold duration
controller.set_hold_duration(3.0)   # 3 detik
controller.set_hold_duration(10.0)  # 10 detik (lebih lama)

# Check current setting (via internal variable)
print(controller.movement_hold_duration)  # 5.0 (default)
```

### Custom Key Mapping dengan Hold

**Note**: Custom keys TIDAK otomatis di-hold, hanya W/A/S/D.

```python
# Jika buat custom mapping untuk movement
controller.add_mapping("forward", "w")  # Akan di-hold 5s
controller.add_mapping("special", "x")  # Akan di-press 0.1s saja

# Untuk hold custom key, perlu edit code atau use W/A/S/D
```

## Performance Impact

### Memory
- Minimal - hanya tracking `currently_pressed` set
- Default hold_duration=5.0 (float) tidak ada overhead

### CPU
- Tokong hold 5 detik → task async, tidak block thread lain
- Multiple viewer commands **bisa parallel** (async handling)

### Example Scenario
```
T=0.0s  User A: "w"  (hold 5s)
T=0.5s  User B: "d"  (hold 5s)
T=1.0s  User C: "a"  (hold 5s)

Result: Semua 3 key di-hold secara bersamaan!
(Mobil maju + belok kanan + belok kiri = complex movement)
```

## Troubleshooting

### Q: Key tidak terlepas (stuck)?
**A**: Jika error/crash saat hold, key mungkin tetap ditekan. Tekan key tersebut manually untuk release, atau restart game.

### Q: Hold duration terlalu lama?
**A**: Edit config JSON, ubah `"hold_duration": 5.0` ke nilai lebih kecil (contoh: 3.0)

### Q: Mau hold custom key juga?
**A**: Edit `movement_keys` set di `racing_game_controller.py`:
```python
self.movement_keys = {"w", "a", "s", "d", "your_key"}
```

### Q: Cooldown error dengan hold?
**A**: Cooldown reset **sebelum hold**, jadi normal. User bisa command lagi setelah cooldown duration selesai (tidak harus menunggu hold selesai).

## Best Practices

✅ **Do**
- Set hold duration 3-5 detik (most games comfortable)
- Test di debug mode dulu sebelum production
- Monitor log output untuk timing verify

❌ **Don't**
- Set hold duration terlalu panjang (>10s) → game unresponsive
- Set hold duration 0 (tidak effect)
- Ubah movement_keys tanpa tahu apa yang Anda lakukan

## Summary

| Fitur | Sebelum | Sesudah |
|-------|---------|--------|
| W/A/S/D behavior | Pressed sebentar | **Held 5 detik** |
| SPACE behavior | Pressed sebentar | **Tetap sebentar** |
| Config save | Tanpa hold duration | **Include `hold_duration`** |
| Customizable | No | **Yes via `set_hold_duration()`** |
| Log detail | Simple | **Include "(held 5s)" info** |

Fitur ini membuat gameplay lebih natural dan responsive untuk racing game! 🎮🏎️
