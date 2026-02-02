# Quick Command Reference

## Single Movement Keys (Hold 5 seconds)

| Command | Key | What It Does |
|---------|-----|-------------|
| `w` / `forward` / `maju` / `gas` | W | Move forward/accelerate |
| `a` / `left` / `kiri` | A | Turn left |
| `s` / `backward` / `mundur` / `brake` | S | Move backward/brake |
| `d` / `right` / `kanan` | D | Turn right |

## Special Keys (Press briefly)

| Command | Key | What It Does |
|---------|-----|-------------|
| `space` / `jump` / `lompat` | SPACE | Jump / Drift handbrake |
| `shift` / `nitro` / `boost` / `turbo` | SHIFT | Nitro boost |
| `drift` / `handbrake` | SPACE | Drift |

## Combination Keys (Hold 5 seconds) - NEW!

| Command | Keys | What It Does |
|---------|------|-------------|
| `ws` | W + S | Drift (forward + brake) |
| `wd` | W + D | Forward + turn right |
| `as` | A + S | Backward + turn left |
| `sd` | S + D | Backward + turn right |

## Examples

### Scenario 1: Straight Racing
```
Viewer says: "w"
→ Mobil akselerasi maju selama 5 detik
```

### Scenario 2: Drifting
```
Viewer says: "ws"
→ Mobil akselerasi + brake bersamaan = DRIFT!
→ Hold 5 detik untuk drift yang smooth
```

### Scenario 3: Turn While Going Forward
```
Viewer says: "wd"
→ Mobil maju sambil belok kanan
→ Lebih natural daripada W terus diikuti D
```

### Scenario 4: Reverse Parking
```
Viewer says: "as" atau "sd"
→ Mundur sambil belok
→ Perfect untuk parking maneuver
```

## Tips

✅ **Best Practices**
- Combination keys (ws, wd, as, sd) untuk complex movement
- Single keys (w, a, s, d) untuk basic movement
- Mix dengan special keys (space, shift) untuk advanced tricks

❌ **Avoid**
- Menekan terlalu cepat (gunakan cooldown system)
- Complex commands yang terlalu lama
- Spam key commands

## Config Settings

Each game in `config.json` has its own settings:

```json
"NFS HEAT": {
  "debug_mode": true,
  "cooldown": 0.3,
  "hold_duration": 2.0,
  "custom_mappings": {}
}
```

- **debug_mode**: Safe test (no keyboard) or Production (real input)
- **cooldown**: Min delay between commands per viewer (seconds)
- **hold_duration**: How long W/A/S/D keys are held
- **custom_mappings**: Custom command → key mappings for this game

You can have different settings for each game!

## Debug Mode vs Production

**Debug Mode** (Safe Testing)
- No actual keyboard input
- Only logging
- Test commands safely

**Production Mode** (Real Input)
- Actual keyboard input to game
- Full control
- Be careful!

## Help!

**Q: My command didn't work?**
A: Check if it's in the mapping list above. Commands are case-insensitive.

**Q: Key is stuck?**
A: Restart the game or press that key manually.

**Q: Want custom commands?**
A: Edit `racing_config.json` and add to `custom_mappings`.

**Q: Want more combinations?**
A: Contact maintainer or edit code to add new combos.
