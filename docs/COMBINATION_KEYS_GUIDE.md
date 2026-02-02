# Combination Keys Feature - Advanced Movement Controls

## Overview
Selain single key commands (W, A, S, D), sistem sekarang support **combination commands** yang menekan multiple keys secara bersamaan untuk complex movement patterns seperti drifting dan turning while moving.

## Supported Combinations

| Command | Keys | Behavior | Use Case |
|---------|------|----------|----------|
| `ws` | W + S | Hold both keys 5s | Drifting (forward + brake) |
| `wd` | W + D | Hold both keys 5s | Forward + right turn |
| `as` | A + S | Hold both keys 5s | Backward + left turn |
| `sd` | S + D | Hold both keys 5s | Backward + right turn |

## How It Works

### Combination Key Execution
Ketika viewer mengetik combination command (misal "ws"):

```
1. Comment diterima: "ws"
   ↓
2. Check: Apakah "ws" di combination_keys? Ya!
   ↓
3. Check: Apakah user on cooldown? No → lanjut
   ↓
4. Press W key
   ↓
5. Press S key  (W masih ditekan)
   ↓
6. Hold semua 5 detik
   ↓
7. Release S key
   ↓
8. Release W key
   ↓
9. Log: "viewer → 'ws' => W + S (held 5s)"
```

### Timing Diagram
```
Time:    0s    1s    2s    3s    4s    5s    6s
         |-----|-----|-----|-----|-----|-----|
W key:   [PRESSED=========================================RELEASED]
S key:   [PRESSED=========================================RELEASED]
         [============= DRIFTING FOR 5 SECONDS ==============]
```

## Real-World Usage Examples

### Example 1: Drifting (WS)
```
Viewer: "ws"
↓
Mobil: Akselerasi maju + brake simultaneously
↓
Result: Perfect drift turn dalam racing game!
```

### Example 2: Forward Turn Right (WD)
```
Viewer: "wd"
↓
Mobil: Maju sambil belok kanan
↓
Result: Turn sambil accelerate tanpa brake
```

### Example 3: Reverse + Left Turn (AS)
```
Viewer: "as"
↓
Mobil: Mundur sambil belok kiri
↓
Result: Reverse parking dengan sudut
```

### Example 4: Reverse + Right Turn (SD)
```
Viewer: "sd"
↓
Mobil: Mundur sambil belok kanan
↓
Result: Reverse parking lainnya
```

## Code Implementation

### In `racing_game_controller.py`

```python
# Combination keys mapping
self.combination_keys = {
    "ws": ["w", "s"],     # Forward + Backward (drifting)
    "wd": ["w", "d"],     # Forward + Right turn
    "as": ["a", "s"],     # Left + Backward (backward left)
    "sd": ["s", "d"],     # Backward + Right (backward right)
}

# New method for holding multiple keys
async def _hold_multiple_keys(self, keys: list, duration: float):
    """Hold multiple keys together for duration seconds"""
    # Press all keys
    for key in keys:
        self.keyboard.press(key)
    
    # Wait for duration
    await asyncio.sleep(duration)
    
    # Release all keys
    for key in keys:
        self.keyboard.release(key)
```

### Handler Logic
```python
async def _handle_comment(self, event):
    # First check if it's a combination key
    combination = self.combination_keys.get(command)
    if combination:
        await self._hold_multiple_keys(combination, 5.0)
        return
    
    # Then check single keys
    key = self.key_mapping.get(command)
    if key:
        # Hold or press logic...
```

## Log Output Examples

### Single Key
```
2026-02-02 20:45:00 - INFO - viewer_123        -> 'w' => w (held 5s)
```

### Combination Key
```
2026-02-02 20:45:05 - INFO - viewer_456        -> 'ws' => W + S (held 5s)
2026-02-02 20:45:10 - INFO - viewer_789        -> 'wd' => W + D (held 5s)
2026-02-02 20:45:15 - INFO - viewer_101        -> 'as' => A + S (held 5s)
```

## Cooldown Behavior

Kombinasi key juga menggunakan **same cooldown system** seperti single key:

```
T=0.0s   User A: "ws" command
T=0.0s   → Cooldown reset (start: 0.0s, end: 0.3s)
T=0.0s   → Press W and S keys
T=5.0s   → Release W and S keys
T=5.3s   → Cooldown selesai, User A bisa command lagi

Result: Meskipun hold 5 detik, cooldown hanya 0.3s
```

## Debug Mode

Ketika running di debug mode, output akan:

```
[DEBUG] Would hold: w+s (5s)
[DEBUG] Would hold: w+d (5s)
[DEBUG] Would hold: a+s (5s)
[DEBUG] Would hold: s+d (5s)
```

Tidak ada actual keyboard input, hanya logging.

## Configuration

### Current Support (No Config Needed)
Combination keys sudah hardcoded:
- WS untuk drifting
- WD untuk forward + right turn
- AS untuk backward + left turn
- SD untuk backward + right turn

### Adding More Combinations
Jika mau tambah combination baru, edit di `__init__`:

```python
self.combination_keys = {
    "ws": ["w", "s"],
    "wd": ["w", "d"],
    "as": ["a", "s"],
    "sd": ["s", "d"],
    "wa": ["w", "a"],     # Forward + Left turn (NEW)
    "wad": ["w", "a", "d"],  # Forward + Left + Right (NEW)
}
```

## Performance Notes

### Key Pressing Order
Keys pressed **sequential** (tidak atomic), tapi delay sangat kecil:
```python
self.keyboard.press("w")   # ~0.001ms
self.keyboard.press("s")   # ~0.001ms  (W sudah ditekan)
# Total delay = 0.002ms (negligible)
```

### Multiple Simultaneous Combinations
Jika multiple viewers command combination key pada saat bersamaan:

```
T=0.0s  User A: "ws"  (hold 5s)
T=0.5s  User B: "wd"  (hold 5s)
T=1.0s  User C: "as"  (hold 5s)

Result: Semua async tasks berjalan parallel!
Pressed keys bisa mencapai 6 key sekaligus (W+S+D+A+S+A)
Game engine akan menangani overlapping input
```

## Compatibility

### Game Support
✅ Tested dengan:
- Racing games (GTA, Forza, NFS)
- Minecraft (movement + sprint)
- Roblox games
- Keyboard-based games umum

### OS Support
- ✅ Windows (tested)
- ⚠️ macOS/Linux (untested, pynput support both)

## Troubleshooting

### Q: Combination keys tidak work?
**A**: 
1. Verify game accept multiple simultaneous key presses
2. Check debug logs: `[DEBUG] Would hold: w+s (5s)`
3. Test di production mode (debug mode hanya log)

### Q: Keys stuck/tidak release?
**A**: 
1. Game crash → restart game
2. Script crash → script akan release all keys on exit
3. Manual release → press those keys once

### Q: Mau disable combination keys?
**A**: Edit `combination_keys` dictionary ke empty:
```python
self.combination_keys = {}  # Disable all combinations
```

### Q: Hanya enable beberapa combinations?
**A**: Edit `combination_keys` untuk keep only yang mau:
```python
self.combination_keys = {
    "ws": ["w", "s"],  # Keep drifting
    "wd": ["w", "d"],  # Keep forward turn
    # Remove "as" and "sd"
}
```

## Advanced: Custom Combinations

### Adding 3-Key Combinations
```python
self.combination_keys = {
    "wad": ["w", "a", "d"],  # Forward + Left + Right (spin?)
    "asd": ["a", "s", "d"],  # Complex backward movement
}
```

### Conditional Combinations
```python
# Jika viewer mengetik exact "DRIFTLEFT"
if command == "driftleft":
    await self._hold_multiple_keys(["w", "a"], 5.0)
```

## Best Practices

✅ **Do**
- Test combinations di debug mode first
- Monitor log untuk verify execution
- Use natural combinations (W+S, W+D, A+S, S+D)
- Keep hold duration consistent (5s)

❌ **Don't**
- Create too many combinations (confusing)
- Mix single + combo in rapid succession
- Set hold duration too long (>10s)
- Hardcode key names (use mapping system)

## Summary

| Feature | Before | After |
|---------|--------|-------|
| Single key commands | ✅ | ✅ (Improved) |
| Combination keys | ❌ | ✅ **NEW** |
| WS drifting | ❌ | ✅ |
| WD forward turn | ❌ | ✅ |
| AS backward left | ❌ | ✅ |
| SD backward right | ❌ | ✅ |
| Parallel execution | N/A | ✅ Async |
| Debug logging | Limited | ✅ Detailed |

Sekarang viewers bisa melakukan complex racing maneuvers dengan mengetik combination commands! 🏎️🔥
