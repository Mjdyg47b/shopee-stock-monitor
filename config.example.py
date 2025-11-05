# ⚠️ JANGAN COMMIT FILE config.py KE REPOSITORY!
# Copy file ini ke config.py dan isi dengan kredensial Anda
# File config.py sudah ada di .gitignore

# Telegram Bot Configuration
# Dapatkan token dari @BotFather di Telegram
TELEGRAM_BOT_TOKEN = "your_bot_token_here"

# Chat ID untuk menerima notifikasi
# Dapatkan dari @userinfobot atau @getmyid_bot
TELEGRAM_CHAT_ID = "your_chat_id_here"

# Daftar produk yang akan dimonitor
# Format: {"shop_id": "xxx", "item_id": "yyy", "url": "zzz"}
PRODUCTS = [
    {
        "shop_id": "581472460",
        "item_id": "28841260015",
        "url": "https://shopee.co.id/Suno-Ai-Pro-Plan-Privaate-1-Bulan-i.581472460.28841260015"
    }
    # Tambahkan produk lain di sini jika diperlukan
]
