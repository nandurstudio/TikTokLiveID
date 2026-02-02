# TikTok Live Interactive Controller (Chat-to-WASD)

Project ini adalah script Python sederhana untuk menghubungkan interaksi chat di **TikTok Live** secara real-time ke input keyboard PC. Tujuannya adalah membiarkan penonton mengontrol game atau aplikasi (seperti Minecraft, GTA, atau emulator) dengan mengetik perintah di kolom komentar.

## 🚀 Fitur Utama
- **Real-time Listening:** Menangkap komentar dari live stream tanpa delay yang signifikan.
- **Key Mapping:** Mengubah komentar spesifik (misal: "W", "Maju") menjadi tekanan tombol keyboard fisik.
- **Safe Input:** Menggunakan library `pynput` untuk simulasi keyboard yang aman.
- **No API Key:** Menggunakan library `TikTokLive` yang tidak memerlukan kunci API resmi TikTok (scraper-based).

## 🛠️ Prasyarat (Requirements)
Pastikan kamu sudah menginstall:
- **Python 3.7+**
- Koneksi internet yang stabil.

## 📦 Instalasi

1. **Clone atau Download** repository ini.
2. Buka terminal/CMD di folder project.
3. Install library yang dibutuhkan:

```bash
pip install TikTokLive pynput asyncio
```

## ⚙️ Konfigurasi & Penggunaan

### 1. Edit Script

Buka file `main.py` (atau nama script python kamu) dan sesuaikan variabel berikut:

* `unique_id`: Ganti dengan username TikTok kamu (tanpa tanda `@`).
* Contoh: Jika URL profil `tiktok.com/@nandurstudio`, maka isi dengan `"nandurstudio"`.

* `key_mapping`: Sesuaikan perintah chat dengan tombol yang ingin ditekan.

```python
# Contoh konfigurasi di dalam script
unique_id = "username_tiktok_mu"

key_mapping = {
    "w": "w",      # User ketik 'w', bot tekan 'W'
    "maju": "w",   # User ketik 'maju', bot tekan 'W'
    "jump": "space" # User ketik 'jump', bot tekan 'Spasi'
}
```

### 2. Jalankan Script

Jalankan bot melalui terminal:

```bash
python main.py
```

### 3. Fokuskan Window

⚠️ **PENTING:** Setelah script berjalan dan terhubung ("Connected"):

1. Buka Game atau Aplikasi target kamu.
2. **Klik pada window game** tersebut agar aktif.
3. Bot hanya bisa menekan tombol pada window yang sedang *active/in-focus*.

## ⚠️ Catatan & Disclaimer

* **Delay TikTok:** TikTok memiliki delay bawaan (latency) antara chat dikirim user dengan chat muncul di layar host sekitar 2-5 detik tergantung koneksi. Ini wajar.
* **Anti-Spam:** Disarankan menambahkan logika *cooldown* di dalam kode jika jumlah penonton sangat banyak agar karakter game tidak "kejang" karena menerima ratusan input per detik.
* **Risiko Banned:** Library ini menggunakan metode *scraping*. Gunakan dengan bijak. Jangan melakukan spam request berlebihan ke server TikTok.

## 🤝 Kontribusi

Project ini bersifat open-source. Silakan lakukan pull request jika ingin menambahkan fitur seperti "Gift Reaction" (misal: Mawar = Lompat).

---

**Dibuat untuk eksperimen interaktif TikTok Live.**

---

## 🧪 Testing

**⚠️ IMPORTANT:** Jangan langsung test dengan real account tanpa mock testing dulu!

### Recommended Testing Flow:
1. **Mock Testing** (PALING AMAN) - `python examples/test_mock.py`
   - Test logic tanpa koneksi TikTok
   - Tidak ada risiko banned
   - Bisa repeat unlimited

2. **Debug Mode** (SAFE) - Set `DEBUG_MODE = True` di `chat_to_keys.py`
   - Connect ke TikTok real
   - Tidak tekan keyboard
   - Verify mapping works

3. **Production** (REAL) - Set `DEBUG_MODE = False`
   - Full functionality
   - Tekan keyboard sungguhan
   - Gunakan saat ready

👉 **[Baca Testing Guide Lengkap](TESTING_GUIDE.md)**

---

## 📝 Catatan Developer

*Bagian ini akan diupdate sesuai perkembangan project*

- Status development: ✅ MOCK TESTING READY
- Mock testing: ✅ WORKING
- Debug mode: ✅ READY
- Production: 🔄 TESTING PHASE
- Last updated: 2 Februari 2026

### File yang Sudah Ada:
- `examples/test_mock.py` - Mock testing (safe)
- `examples/chat_to_keys.py` - Production ready script
- `docs/TESTING_GUIDE.md` - Detailed testing guide
