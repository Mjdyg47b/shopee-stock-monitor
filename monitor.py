import requests
import json
import os
import time
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
    """Ambil informasi produk dari Shopee API dengan anti-block headers"""
    
    # ✅ GUNAKAN API v2 yang lebih stabil
    url = f"https://shopee.co.id/api/v2/item/get?itemid={item_id}&shopid={shop_id}"
    
    # ✅ Headers lengkap untuk bypass blocking
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://shopee.co.id/',
        'Origin': 'https://shopee.co.id',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
    }
    
    try:
        print(f"   Trying API v2...")
        response = requests.get(url, headers=headers, timeout=15)
        
        # Jika v2 gagal, coba v4 dengan delay
        if response.status_code == 403:
            print(f"   API v2 blocked, trying v4 with delay...")
            time.sleep(2)
            url = f"https://shopee.co.id/api/v4/item/get?itemid={item_id}&shopid={shop_id}"
            response = requests.get(url, headers=headers, timeout=15)
        
        response.raise_for_status()
        data = response.json()
        
        if data.get('error') or not data.get('data'):
            print(f"   ❌ Error dari API: {data.get('error_msg', 'Unknown error')}")
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
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"   ❌ API Blocked (403) - Trying alternative method...")
            # Fallback: gunakan scraping sederhana
            return get_product_info_fallback(shop_id, item_id)
        else:
            print(f"   ❌ HTTP error: {e}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Network error: {e}")
        return None
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return None

def get_product_info_fallback(shop_id, item_id):
    """Fallback method: Scrape dari halaman HTML produk"""
    url = f"https://shopee.co.id/product/{shop_id}/{item_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'id-ID,id;q=0.9',
    }
    
    try:
        print(f"   Trying fallback method (HTML scraping)...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Cari JSON data di dalam HTML
        html = response.text
        
        # Shopee menyimpan data di <script> tag dengan __INITIAL_STATE__
        if '"stock":' in html:
            # Simple parsing untuk stock availability
            # Jika ada kata "Habis" atau "Out of Stock" = stok habis
            if 'Habis' in html or 'Out of Stock' in html or 'out_of_stock' in html:
                stock = 0
            else:
                stock = 1  # Assume available jika tidak ada indikasi habis
            
            return {
                'name': 'Suno Ai Pro Plan (parsed from HTML)',
                'stock': stock,
                'price': 0,  # Tidak bisa parse harga dari HTML dengan mudah
                'sold': 0,
                'shop_name': 'Unknown',
                'item_status': 'active' if stock > 0 else 'sold_out'
            }
        
        print(f"   ❌ Fallback failed: Cannot parse HTML")
        return None
        
    except Exception as e:
        print(f"   ❌ Fallback error: {e}")
        return None

def send_telegram_message(message, disable_notification=False):
    """Kirim notifikasi ke Telegram dengan opsi bunyi"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False,
        'disable_notification': disable_notification
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("   ✅ Telegram notification sent successfully")
        return True
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Failed to send Telegram message: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Response: {e.response.text}")
        return False

def format_notification(product_info, product_config, status_changed=False, now_available=False):
    """Format pesan notifikasi"""
    stock_status = "✅ TERSEDIA" if product_info['stock'] > 0 else "❌ HABIS"
    
    if now_available:
        status_emoji = "🔔🎉"
    elif status_changed:
        status_emoji = "🔔"
    else:
        status_emoji = "ℹ️"
    
    # Format harga
    price_text = f"Rp {product_info['price']:,.0f}" if product_info['price'] > 0 else "N/A"
    sold_text = f"{product_info['sold']}" if product_info['sold'] > 0 else "N/A"
    
    message = f"""{status_emoji} <b>NOTIFIKASI STOK SHOPEE</b>

📦 <b>Produk:</b> {product_info['name']}
🏪 <b>Toko:</b> {product_info['shop_name']}
📊 <b>Status:</b> {stock_status}
📦 <b>Stok:</b> {product_info['stock']} unit
💰 <b>Harga:</b> {price_text}
🛒 <b>Terjual:</b> {sold_text} item

🔗 <a href="{product_config['url']}">Lihat Produk</a>

⏰ <b>Waktu:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB
"""
    
    if now_available:
        message += "\n🎉 <b>PRODUK SEKARANG TERSEDIA!</b> 🎉\n⚡ <b>BURUAN CEK SEKARANG!</b> ⚡"
    elif status_changed:
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
            print("   ⚠️ Failed to get product info, skipping...")
            continue
        
        print(f"   Name: {product_info['name']}")
        print(f"   Stock: {product_info['stock']}")
        print(f"   Price: Rp {product_info['price']:,.0f}")
        
        # Cek apakah ada perubahan status
        product_key = f"{shop_id}_{item_id}"
        status_changed = False
        now_available = False
        
        if product_key in state:
            old_stock = state[product_key].get('stock', 0)
            old_available = old_stock > 0
            new_available = product_info['stock'] > 0
            
            if old_available != new_available:
                status_changed = True
                if not old_available and new_available:
                    now_available = True
                    print("   🎉 PRODUCT NOW AVAILABLE!")
                elif old_available and not new_available:
                    print("   ⚠️ Product now OUT OF STOCK!")
                print("   🔔 STATUS CHANGED!")
        else:
            # Pertama kali monitor
            status_changed = True
            if product_info['stock'] > 0:
                now_available = True
            print("   🆕 First time monitoring this product")
        
        # Update state
        state[product_key] = {
            'stock': product_info['stock'],
            'last_check': datetime.now().isoformat(),
            'name': product_info['name']
        }
        
        # Kirim notifikasi
        if status_changed:
            message = format_notification(
                product_info, 
                product, 
                status_changed=True, 
                now_available=now_available
            )
            disable_sound = not now_available
            send_telegram_message(message, disable_notification=disable_sound)
            
            if now_available:
                print("   🔔 NOTIFICATION SENT WITH SOUND (Product Available!)")
            else:
                print("   🔕 NOTIFICATION SENT WITHOUT SOUND (Product Out of Stock)")
        else:
            print("   ℹ️ No status change, no notification sent")
    
    # Simpan state
    save_state(state)
    print(f"\n✅ Monitoring completed at {datetime.now()}")

if __name__ == "__main__":
    monitor_products()
