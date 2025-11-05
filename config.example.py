"""
Template konfigurasi untuk bot monitoring Shopee
Copy file ini ke config.py dan isi dengan data Anda
JANGAN commit config.py ke repository!
"""

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "8226924685:AAGACsPrGvqSI4iJ4AJyvERPBdK8wM0ICCM"
TELEGRAM_CHAT_ID = "6328135369"

# Products to monitor
PRODUCTS = [
    {
        'shop_id': 'your_shop_id',
        'item_id': 'your_item_id',
        'url': 'https://shopee.co.id/product-url'
    }
]
