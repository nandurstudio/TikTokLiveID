# Configuration Management - JSON Format

## Overview
Konfigurasi setup Anda sekarang otomatis disimpan dalam format JSON setelah setiap kali setup. Pada launch berikutnya, Anda bisa memilih untuk menggunakan kembali konfigurasi yang lama.

## File Configuration
**Nama file:** `racing_config.json`  
**Lokasi:** Root folder project (g:\GitHub\TikTokLiveID\)  
**Format:** JSON dengan UTF-8 encoding

## Struktur JSON

```json
{
  "username": "nandurstudio",
  "debug_mode": true,
  "cooldown": 0.3,
  "custom_mappings": {
    "horn": "h",
    "drift": "shift"
  }
}
```

### Field Penjelasan:
- **username** *(string)* - Username TikTok tanpa @
- **debug_mode** *(boolean)* - true = DEBUG (aman), false = PRODUCTION (real)
- **cooldown** *(float)* - Durasi cooldown per user dalam detik (default 0.2s)
- **custom_mappings** *(object)* - Mapping custom command → key

## Cara Kerja

### Flow Pertama Kali
```
launcher.py
  ↓
[Cek racing_config.json]
  ↓
[File tidak ada]
  ↓
[Jalankan pre-flight checklist]
  ↓
[Interactive setup]
  ↓
[Save config → racing_config.json] ✅
  ↓
[Jalankan controller]
```

### Flow Kedua Kali+
```
launcher.py
  ↓
[Cek racing_config.json]
  ↓
[File ditemukan!]
  ↓
[Tampilkan: "Found existing configuration"]
  ↓
[Tanya user: Use existing? (yes/no)]
  ↓
JIKA YES:
  ↓
  [Load config dari JSON]
  ↓
  [Skip pre-checklist & setup]
  ↓
  [Langsung jalankan controller] ⚡ CEPAT
  
JIKA NO:
  ↓
  [Jalankan pre-checklist & setup baru]
  ↓
  [Overwrite racing_config.json]
  ↓
  [Jalankan controller]
```

## Contoh Penggunaan

### Scenario 1: Setup Pertama
```
$ python launcher.py

SELECT MODE
1. REAL TikTok
2. MOCK
Choose mode (1 or 2): 1

SELECT DEBUG MODE
Use DEBUG mode? (yes/no): yes

[Pre-checklist & Setup...]

[CONFIG] Saved to racing_config.json ✅

[STARTING] Racing Game Controller...
```

### Scenario 2: Launch Berikutnya
```
$ python launcher.py

SELECT MODE
1. REAL TikTok
2. MOCK
Choose mode (1 or 2): 1

SELECT DEBUG MODE
Use DEBUG mode? (yes/no): yes

Found existing configuration: racing_config.json
Use existing config? (yes/no): yes

[LOADED] Config for @nandurstudio

[STARTING] Racing Game Controller...
```

## Keuntungan

✅ **Lebih Cepat**: Setup berikutnya tinggal confirm config lama  
✅ **Konsisten**: Semua settings tersimpan dengan rapi  
✅ **Fleksibel**: Bisa load ulang atau setup baru kapan saja  
✅ **Transparan**: Semua data dalam format text (JSON) yang readable  
✅ **Backup-able**: Bisa backup `racing_config.json` untuk restore later

## Mengelola Config File

### View Current Config
```powershell
Get-Content racing_config.json | ConvertFrom-Json | Format-Table
```

### Manual Edit
Buka `racing_config.json` dengan text editor:
```json
{
  "username": "nandurstudio",
  "debug_mode": false,
  "cooldown": 0.5,
  "custom_mappings": {}
}
```

### Delete Config (Reset)
```powershell
Remove-Item racing_config.json
```

Launching ulang akan meminta setup dari awal.

## Technical Details

### Save Config
- Fungsi: `save_config(config_data, filename="racing_config.json")`
- Lokasi: `examples/racing_game_controller.py`
- Dipanggil: Di akhir `interactive_setup()`
- Encoding: UTF-8 with `ensure_ascii=False`

### Load Config  
- Fungsi: `load_config(filename="racing_config.json")`
- Lokasi: `examples/racing_game_controller.py`
- Dipanggil: Di awal `run_real_mode()` dalam launcher
- Error handling: Return `None` jika file tidak ada atau corrupt

### Integration dalam Launcher
```python
# launcher.py - run_real_mode function

existing_config = load_config("racing_config.json")

if existing_config:
    print("Found existing configuration: racing_config.json")
    use_existing = input("Use existing config? (yes/no): ")
    
    if use_existing in ['yes', 'y']:
        config = existing_config  # Load from JSON
    else:
        config = interactive_setup(username)  # Setup baru
else:
    config = interactive_setup(username)  # Setup pertama kali
```

## Troubleshooting

### Q: Config tidak ke-load?
**A:** Check file encoding. Harus UTF-8 tanpa BOM.

### Q: Mau reset config?
**A:** Hapus `racing_config.json` → launch ulang akan setup dari awal

### Q: Bisa backup config?
**A:** Ya! Copy `racing_config.json` ke folder backup. Restore dengan copy balik.

### Q: Format JSON salah?
**A:** Hapus file, launcher akan auto-create yang benar on next setup

## Log Messages

```
[CONFIG] Saved to racing_config.json      ← Setiap kali setup selesai
[CONFIG] Loaded from racing_config.json   ← Saat load existing config
[CONFIG] Failed to save: [error message]  ← Saat terjadi error write
[CONFIG] Failed to load: [error message]  ← Saat terjadi error read
```

Semua messages ini akan muncul di `racing_controller.log`
