
import requests
import json
import os
from datetime import datetime
from pathlib import Path

# Konfigurasi dari Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8226924685:AAHuVRWe4mSbzjkWwGohSJ7RsISTiwRQsPM')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '6328135369')

# State file untuk tracking perubahan
STATE_FILE = 'stock_state.json'

# Produk yang dipantau
PRODUCTS = [
    {
        'shop_id': '581472460',
        'item_id': '28841260015',
        'url': 'https://shopee.co.id/Suno-Ai-Pro-Plan-Privaate-1-Bulan-i.581472460.28841260015'
    }
]

def load_state():
    """Load state terakhir dari file"""
    if Path(STATE_FILE).exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    """Simpan state ke file"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_product_info(shop_id, item_id):
    """Ambil informasi produk dari Shopee API"""
    url = f"https://shopee.co.id/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://shopee.co.id/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('error') or not data.get('data'):
            print(f"❌ Error dari API: {data.get('error_msg', 'Unknown error')}")
            return None
            
        item = data['data']
        
        return {
            'name': item.get('name', 'Unknown'),
            'stock': item.get('stock', 0),
            'price': item.get('price', 0) / 100000,  # Convert to Rupiah
            'sold': item.get('sold', 0),
            'shop_name': item.get('shop_name', 'Unknown Shop'),
            'item_status': item.get('item_status', 'unknown')
        }
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def send_telegram_message(message):
    """Kirim notifikasi ke Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("✅ Telegram notification sent successfully")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False

def format_notification(product_info, product_config, status_changed=False):
    """Format pesan notifikasi"""
    stock_status = "✅ TERSEDIA" if product_info['stock'] > 0 else "❌ HABIS"
    status_emoji = "🔔" if status_changed else "ℹ️"
    
    message = f"""{status_emoji} <b>NOTIFIKASI STOK SHOPEE</b>

📦 <b>Produk:</b> {product_info['name']}
🏪 <b>Toko:</b> {product_info['shop_name']}
📊 <b>Status:</b> {stock_status}
📦 <b>Stok:</b> {product_info['stock']} unit
💰 <b>Harga:</b> Rp {product_info['price']:,.0f}
🛒 <b>Terjual:</b> {product_info['sold']} item

🔗 <a href="{product_config['url']}">Lihat Produk</a>

⏰ <b>Waktu:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB
"""
    
    if status_changed:
        message += "\n⚡ <b>STATUS BERUBAH!</b> Cek sekarang!"
    
    return message

def monitor_products():
    """Monitor semua produk"""
    print(f"🔍 Starting monitoring at {datetime.now()}")
    
    state = load_state()
    
    for product in PRODUCTS:
        shop_id = product['shop_id']
        item_id = product['item_id']
        
        print(f"\n📊 Checking product: {item_id}")
        
        product_info = get_product_info(shop_id, item_id)
        
        if not product_info:
            print("⚠️ Failed to get product info, skipping...")
            continue
        
        print(f"   Name: {product_info['name']}")
        print(f"   Stock: {product_info['stock']}")
        print(f"   Price: Rp {product_info['price']:,.0f}")
        
        # Cek apakah ada perubahan status
        product_key = f"{shop_id}_{item_id}"
        status_changed = False
        
        if product_key in state:
            old_stock = state[product_key].get('stock', 0)
            old_available = old_stock > 0
            new_available = product_info['stock'] > 0
            
            if old_available != new_available:
                status_changed = True
                print("   🔔 STATUS CHANGED!")
        else:
            # Pertama kali monitor, kirim notifikasi
            status_changed = True
            print("   🆕 First time monitoring this product")
        
        # Update state
        state[product_key] = {
            'stock': product_info['stock'],
            'last_check': datetime.now().isoformat(),
            'name': product_info['name']
        }
        
        # Kirim notifikasi jika ada perubahan
        if status_changed:
            message = format_notification(product_info, product, status_changed=True)
            send_telegram_message(message)
        else:
            print("   ℹ️ No status change, no notification sent")
    
    # Simpan state
    save_state(state)
    print(f"\n✅ Monitoring completed at {datetime.now()}")

if __name__ == "__main__":
    monitor_products()
