#!/usr/bin/env python3
"""
Shopee Stock Monitor Bot
Monitors Shopee product stock and sends Telegram notifications when stock status changes.
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Optional, Any
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '')
STATE_FILE = 'stock_state.json'

# Product to monitor
PRODUCTS = [
    {
        "shop_id": "581472460",
        "item_id": "28841260015",
        "url": "https://shopee.co.id/Suno-Ai-Pro-Plan-Privaate-1-Bulan-i.581472460.28841260015"
    }
]

# Shopee API configuration
SHOPEE_API_URL = "https://shopee.co.id/api/v4/item/get"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Referer': 'https://shopee.co.id/'
}


def load_state() -> Dict[str, Any]:
    """Load previous state from JSON file."""
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
                logger.info(f"Loaded state from {STATE_FILE}")
                return state
        else:
            logger.info(f"No existing state file found, starting fresh")
            return {}
    except Exception as e:
        logger.error(f"Error loading state: {e}")
        return {}


def save_state(state: Dict[str, Any]) -> None:
    """Save current state to JSON file."""
    try:
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        logger.info(f"State saved to {STATE_FILE}")
    except Exception as e:
        logger.error(f"Error saving state: {e}")


def fetch_product_data(shop_id: str, item_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch product data from Shopee API.
    
    Args:
        shop_id: Shopee shop ID
        item_id: Shopee item ID
    
    Returns:
        Dictionary containing product data or None if error occurs
    """
    try:
        params = {
            'itemid': item_id,
            'shopid': shop_id
        }
        
        logger.info(f"Fetching data for item {item_id} from shop {shop_id}")
        response = requests.get(
            SHOPEE_API_URL,
            params=params,
            headers=HEADERS,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        
        if 'data' not in data or not data['data']:
            logger.error(f"Invalid response from Shopee API: {data}")
            return None
        
        item_data = data['data']
        
        # Extract relevant information
        product_info = {
            'name': item_data.get('name', 'Unknown Product'),
            'stock': item_data.get('stock', 0),
            'price': item_data.get('price', 0) / 100000,  # Convert to actual price
            'sold': item_data.get('sold', 0),
            'shop_name': item_data.get('shop_name', 'Unknown Shop'),
            'item_status': item_data.get('item_status', 'unknown'),
            'is_available': item_data.get('stock', 0) > 0 and item_data.get('item_status') != 'deleted'
        }
        
        logger.info(f"Product data fetched successfully: {product_info['name']}")
        return product_info
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout while fetching product data")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error while fetching product data: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error while fetching product data: {e}")
        return None


def format_notification(product_info: Dict[str, Any], product_url: str, status_changed: bool = True) -> str:
    """
    Format notification message for Telegram.
    
    Args:
        product_info: Dictionary containing product information
        product_url: URL of the product
        status_changed: Whether the status has changed
    
    Returns:
        Formatted message string
    """
    status_emoji = "✅ TERSEDIA" if product_info['is_available'] else "❌ HABIS"
    
    # Get current time in WIB (UTC+7)
    from datetime import timezone, timedelta
    wib = timezone(timedelta(hours=7))
    current_time = datetime.now(wib).strftime("%Y-%m-%d %H:%M:%S")
    
    message = f"""🔔 NOTIFIKASI STOK SHOPEE

📦 Produk: {product_info['name']}
🏪 Toko: {product_info['shop_name']}
📊 Status: {status_emoji}
📦 Stok: {product_info['stock']} unit
💰 Harga: Rp {product_info['price']:,.0f}
🛒 Terjual: {product_info['sold']} item

🔗 <a href="{product_url}">Link ke produk</a>

⏰ Waktu: {current_time} WIB"""

    if status_changed:
        message += "\n\n⚡ STATUS BERUBAH! Cek sekarang!"
    
    return message


def send_telegram_notification(message: str) -> bool:
    """
    Send notification to Telegram.
    
    Args:
        message: Message to send
    
    Returns:
        True if successful, False otherwise
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials not configured, skipping notification")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML',
            'disable_web_page_preview': False
        }
        
        logger.info("Sending Telegram notification...")
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info("Telegram notification sent successfully")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending Telegram notification: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending Telegram notification: {e}")
        return False


def check_stock_changes(product_info: Dict[str, Any], previous_state: Optional[Dict[str, Any]]) -> bool:
    """
    Check if stock status has changed.
    
    Args:
        product_info: Current product information
        previous_state: Previous product state
    
    Returns:
        True if status changed, False otherwise
    """
    if previous_state is None:
        logger.info("No previous state, treating as first check")
        return True
    
    previous_available = previous_state.get('is_available', None)
    current_available = product_info['is_available']
    
    if previous_available is None:
        return True
    
    if previous_available != current_available:
        logger.info(f"Stock status changed: {previous_available} -> {current_available}")
        return True
    
    logger.info("Stock status unchanged")
    return False


def monitor_products() -> None:
    """Main monitoring function."""
    logger.info("=" * 50)
    logger.info("Starting Shopee Stock Monitor")
    logger.info("=" * 50)
    
    # Load previous state
    state = load_state()
    
    # Track if any changes were made
    changes_made = False
    
    for product in PRODUCTS:
        shop_id = product['shop_id']
        item_id = product['item_id']
        product_url = product['url']
        product_key = f"{shop_id}_{item_id}"
        
        logger.info(f"\nChecking product: {product_url}")
        
        # Fetch current product data
        product_info = fetch_product_data(shop_id, item_id)
        
        if product_info is None:
            logger.error(f"Failed to fetch data for product {product_key}")
            continue
        
        # Get previous state for this product
        previous_state = state.get(product_key)
        
        # Check if status changed
        status_changed = check_stock_changes(product_info, previous_state)
        
        # Send notification if status changed
        if status_changed:
            message = format_notification(product_info, product_url, status_changed=True)
            send_telegram_notification(message)
            changes_made = True
        
        # Update state
        state[product_key] = {
            'name': product_info['name'],
            'is_available': product_info['is_available'],
            'stock': product_info['stock'],
            'price': product_info['price'],
            'sold': product_info['sold'],
            'last_check': datetime.utcnow().isoformat()
        }
    
    # Save updated state
    save_state(state)
    
    logger.info("=" * 50)
    logger.info("Monitoring completed")
    logger.info("=" * 50)


if __name__ == '__main__':
    try:
        monitor_products()
    except KeyboardInterrupt:
        logger.info("\nMonitoring stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise
