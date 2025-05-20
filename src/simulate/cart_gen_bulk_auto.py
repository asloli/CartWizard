import json
import os
import random

PRODUCTS_PATH = 'data/raw/products.json'
OUTPUT_DIR = 'data/carts/'
NUM_CARTS = 1000
ITEM_COUNT_RANGE = (15, 25)

def load_products(path=PRODUCTS_PATH):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_cart(cart_id, products, min_items=15, max_items=25):
    n = random.randint(min_items, max_items)
    items = random.sample(products, k=n)
    return {
        'cart_id': cart_id,
        'items': items
    }

def save_cart(cart, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cart, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    products = load_products()
    for i in range(1, NUM_CARTS + 1):
        cid = f"AUTO{i:03d}"
        cart = generate_cart(cid, products, *ITEM_COUNT_RANGE)
        path = os.path.join(OUTPUT_DIR, f"auto_{i:03d}.json")
        save_cart(cart, path)
        if i % 50 == 0 or i == NUM_CARTS:
            print(f"✅ 已產出 {i} / {NUM_CARTS} 筆")
