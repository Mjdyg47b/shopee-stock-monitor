# 🛍️ Shopee Stock Monitor Bot

Bot monitoring otomatis untuk memantau ketersediaan stok produk Shopee dengan notifikasi Telegram menggunakan GitHub Actions.

## ✨ Fitur Utama

- 🔄 **Monitoring Otomatis**: Cek stok produk Shopee setiap 15 menit
- 📱 **Notifikasi Telegram**: Notifikasi instan ke Telegram saat status stok berubah
- 🤖 **GitHub Actions**: Berjalan otomatis di cloud, tidak perlu server sendiri
- 💾 **State Management**: Tracking perubahan status dengan file JSON
- 🔒 **Secure**: Kredensial disimpan aman di GitHub Secrets
- 📊 **Detailed Info**: Nama produk, stok, harga, terjual, dan link produk
- ⚡ **Error Handling**: Handling error yang comprehensive dengan logging

## 🚀 Cara Setup

### 1. Fork/Clone Repository

```bash
git clone https://github.com/yourusername/shopee-stock-monitor.git
cd shopee-stock-monitor
```

### 2. Setup Telegram Bot

1. Buka Telegram dan cari **@BotFather**
2. Kirim perintah `/newbot` dan ikuti instruksinya
3. Simpan **Bot Token** yang diberikan (contoh: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Cari bot **@userinfobot** atau **@getmyid_bot** untuk mendapatkan **Chat ID** Anda
5. Start bot Anda agar bisa menerima pesan

### 3. Setup GitHub Secrets

⚠️ **PENTING**: Jangan pernah commit token atau chat ID ke repository!

1. Buka repository Anda di GitHub
2. Klik **Settings** → **Secrets and variables** → **Actions**
3. Klik **New repository secret**
4. Tambahkan 2 secrets berikut:

   **Secret 1:**
   - Name: `TELEGRAM_BOT_TOKEN`
   - Value: Token bot Anda dari BotFather

   **Secret 2:**
   - Name: `TELEGRAM_CHAT_ID`
   - Value: Chat ID Anda

### 4. Aktifkan GitHub Actions

1. Buka tab **Actions** di repository GitHub Anda
2. Jika diminta, klik **I understand my workflows, go ahead and enable them**
3. Workflow akan berjalan otomatis setiap 15 menit

### 5. Test Manual (Opsional)

Untuk test secara manual:

1. Buka tab **Actions**
2. Pilih workflow **Shopee Stock Monitor**
3. Klik **Run workflow** → **Run workflow**
4. Lihat log untuk memastikan berjalan dengan baik

## 📦 Menambah Produk Baru

Edit file `monitor.py` dan tambahkan produk ke dalam list `PRODUCTS`:

```python
PRODUCTS = [
    {
        "shop_id": "581472460",
        "item_id": "28841260015",
        "url": "https://shopee.co.id/Suno-Ai-Pro-Plan-Privaate-1-Bulan-i.581472460.28841260015"
    },
    {
        "shop_id": "YOUR_SHOP_ID",
        "item_id": "YOUR_ITEM_ID",
        "url": "YOUR_PRODUCT_URL"
    }
]
```

### Cara Mendapatkan Shop ID dan Item ID

Dari URL Shopee seperti:
```
https://shopee.co.id/Product-Name-i.581472460.28841260015
```

- **Shop ID**: Angka setelah `-i.` → `581472460`
- **Item ID**: Angka setelah Shop ID → `28841260015`

Format URL Shopee:
```
https://shopee.co.id/[nama-produk]-i.[shop_id].[item_id]
```

## ⚙️ Konfigurasi

### Mengubah Schedule Monitoring

Edit file `.github/workflows/monitor.yml` pada bagian `cron`:

```yaml
schedule:
  - cron: '*/15 * * * *'  # Setiap 15 menit
  # - cron: '*/30 * * * *'  # Setiap 30 menit
  # - cron: '0 * * * *'     # Setiap jam
  # - cron: '0 */2 * * *'   # Setiap 2 jam
```

### Run Lokal (Development)

Untuk testing lokal:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN="your_token"
   export TELEGRAM_CHAT_ID="your_chat_id"
   ```

3. Run script:
   ```bash
   python monitor.py
   ```

## 📱 Format Notifikasi

Saat status stok berubah, Anda akan menerima notifikasi seperti ini:

```
🔔 NOTIFIKASI STOK SHOPEE

📦 Produk: Suno Ai Pro Plan Privaate 1 Bulan
🏪 Toko: My Shop
📊 Status: ✅ TERSEDIA / ❌ HABIS
📦 Stok: 10 unit
💰 Harga: Rp 50,000
🛒 Terjual: 150 item

🔗 [Link ke produk]

⏰ Waktu: 2025-11-05 20:15:30 WIB

⚡ STATUS BERUBAH! Cek sekarang!
```

## 🔧 Troubleshooting

### Tidak Menerima Notifikasi

1. ✅ Pastikan GitHub Secrets sudah benar
2. ✅ Pastikan sudah `/start` bot Telegram Anda
3. ✅ Check log di GitHub Actions untuk error
4. ✅ Test bot token dengan: `https://api.telegram.org/bot<YOUR_TOKEN>/getMe`
5. ✅ Pastikan Chat ID benar (angka, bukan username)

### Workflow Tidak Berjalan

1. ✅ Pastikan GitHub Actions sudah diaktifkan
2. ✅ Check tab Actions untuk melihat error
3. ✅ Pastikan syntax YAML workflow benar
4. ✅ Cron schedule kadang delay beberapa menit

### Error "Failed to fetch data"

1. ✅ Shopee API mungkin down atau berubah
2. ✅ Product ID atau Shop ID salah
3. ✅ Check log untuk detail error

### Stock State Tidak Ter-commit

1. ✅ Pastikan workflow punya permission untuk write
2. ✅ Check error di step "Commit and push"
3. ✅ Pastikan tidak ada conflict di stock_state.json

## 🔄 Cara Kerja Sistem

```
┌─────────────────────────────────────────────────────────┐
│  GitHub Actions (Every 15 minutes)                      │
└─────────────────────────────────────────────────────────┘
                          │
                          ↓
         ┌────────────────────────────────┐
         │  Run monitor.py                │
         └────────────────────────────────┘
                          │
                          ↓
         ┌────────────────────────────────┐
         │  Load stock_state.json         │
         └────────────────────────────────┘
                          │
                          ↓
         ┌────────────────────────────────┐
         │  Fetch data from Shopee API    │
         │  (Product info, stock, price)  │
         └────────────────────────────────┘
                          │
                          ↓
         ┌────────────────────────────────┐
         │  Compare with previous state   │
         │  (Stock available/out check)   │
         └────────────────────────────────┘
                          │
                          ↓
              ┌──────────┴──────────┐
              │                     │
              ↓                     ↓
     ┌────────────────┐    ┌───────────────┐
     │  Status Changed│    │  No Change    │
     └────────────────┘    └───────────────┘
              │                     │
              ↓                     │
     ┌────────────────┐            │
     │ Send Telegram  │            │
     │  Notification  │            │
     └────────────────┘            │
              │                     │
              └──────────┬──────────┘
                         ↓
         ┌────────────────────────────────┐
         │  Update & Save state to JSON   │
         └────────────────────────────────┘
                          │
                          ↓
         ┌────────────────────────────────┐
         │  Commit changes to GitHub      │
         └────────────────────────────────┘
```

## 🔐 Security Best Practices

- ✅ **Jangan** commit file `config.py` atau `.env` yang berisi credentials
- ✅ **Gunakan** GitHub Secrets untuk menyimpan token
- ✅ File `.gitignore` sudah dikonfigurasi untuk mencegah commit credentials
- ✅ Bot token dan Chat ID hanya tersimpan di GitHub Secrets (encrypted)
- ✅ Regenerate bot token jika terlanjur ter-expose

## 📝 File Structure

```
shopee-stock-monitor/
├── .github/
│   └── workflows/
│       └── monitor.yml          # GitHub Actions workflow
├── .gitignore                   # Git ignore file
├── config.example.py            # Configuration template
├── monitor.py                   # Main monitoring script
├── README.md                    # Documentation (this file)
├── requirements.txt             # Python dependencies
└── stock_state.json            # State tracking file (auto-generated)
```

## 📊 Data Produk yang Dimonitor

Saat ini bot memonitor:
- **Produk**: Suno Ai Pro Plan Privaate 1 Bulan
- **Shop ID**: 581472460
- **Item ID**: 28841260015
- **URL**: https://shopee.co.id/Suno-Ai-Pro-Plan-Privaate-1-Bulan-i.581472460.28841260015

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 📄 License

This project is [MIT](LICENSE) licensed.

---

**Made with ❤️ for Shopee shoppers**

💡 **Tips**: 
- Set schedule lebih sering untuk produk populer yang cepat habis
- Gunakan multiple products untuk monitor beberapa produk sekaligus
- Check GitHub Actions usage quota Anda (2000 menit/bulan untuk free tier)
