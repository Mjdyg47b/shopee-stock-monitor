"""
Template konfigurasi untuk bot monitoring Shopee
Copy file ini ke config.py dan isi dengan data Anda
JANGAN commit config.py ke repository!
"""

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "your_bot_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"

# Products to monitor
PRODUCTS = [
    {
        'shop_id': 'your_shop_id',
        'item_id': 'your_item_id',
        'url': 'https://shopee.co.id/product-url'
    }
]
