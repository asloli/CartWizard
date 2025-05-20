import json
import os
import random

PRODUCTS_PATH = 'data/raw/products.json'
OUTPUT_DIR = 'data/carts/'
NUM_CARTS = 100
CART_SIZE = (3, 6)  # 每筆購物車商品數（最小, 最大）

def load_products(path=PRODUCTS_PATH):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_cart(products, cart_id, cart_size_range=CART_SIZE):
    cart_size = random.randint(*cart_size_range)
    cart_items = random.sample(products, k=cart_size)
    return {
        'cart_id': f'C{cart_id:03d}',
        'items': cart_items
    }

def save_cart(cart, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cart, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    products = load_products()
    for i in range(1, NUM_CARTS + 1):
        cart = generate_cart(products, i)
        save_cart(cart, f"{OUTPUT_DIR}/cart_{i:03d}.json")
    print(f"✅ 已產生 {NUM_CARTS} 筆購物車資料，儲存於 {OUTPUT_DIR}")