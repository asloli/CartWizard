import json
import os
import random

PRODUCTS_PATH = 'data/raw/products.json'
OUTPUT_DIR = 'data/carts/'
NUM_CARTS = 5
ITEM_COUNT_RANGE = (15, 25)

# 你的三個極端折扣要匹配的商品組合
EXTREME_DISCOUNTS = {
    "D900": ["P001"],              # 單品三折
    "D901": ["P002", "P003"],      # 組合折1500
    "D902": []                     # 滿額2000，自然就觸發
}

def load_products(path=PRODUCTS_PATH):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def insert_trigger_items(products, d_ids):
    used = []
    for d in d_ids:
        for pid in EXTREME_DISCOUNTS[d]:
            item = next((p for p in products if p['id'] == pid), None)
            if item:
                used.append(item)
    return used

def build_cart(cart_id, all_products):
    num_items = random.randint(*ITEM_COUNT_RANGE)
    
    # 隨機決定要觸發哪些極端折扣（1~3個）
    d_ids = random.sample(list(EXTREME_DISCOUNTS.keys()), k=random.randint(1, 3))

    # 插入對應商品
    base_items = insert_trigger_items(all_products, d_ids)

    # 隨機補齊其餘商品（避免重複）
    used_ids = set(p['id'] for p in base_items)
    others = [p for p in all_products if p['id'] not in used_ids]
    while len(base_items) < num_items and others:
        pick = random.choice(others)
        base_items.append(pick)
        others.remove(pick)

    return {
        "cart_id": cart_id,
        "items": base_items
    }

def save_cart(cart, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cart, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    products = load_products()
    for i in range(1, NUM_CARTS + 1):
        cart = build_cart(f"CEXT{i:03d}", products)
        path = f"{OUTPUT_DIR}/cart_extreme_{i:03d}.json"
        save_cart(cart, path)
        print(f"✅ 已產生：{path}")
