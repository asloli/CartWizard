import json
import os
import random

OUTPUT_DIR = "data/carts/"
PRODUCTS_PATH = "data/raw/products.json"
os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_CARTS = 1000
TARGET_MIN = 1700
TARGET_MAX = 1999

with open(PRODUCTS_PATH, "r", encoding="utf-8") as f:
    products = json.load(f)

def generate_targeted_cart():
    cart = []
    total = 0
    attempts = 0
    while total < TARGET_MIN and attempts < 1000:
        p = random.choice(products)
        if total + p["price"] > TARGET_MAX:
            attempts += 1
            continue
        cart.append(p)
        total += p["price"]
    return cart if TARGET_MIN <= total <= TARGET_MAX else None

count = 0
for i in range(NUM_CARTS * 2):
    cart = generate_targeted_cart()
    if not cart:
        continue
    cart_data = {
        "cart_id": f"TARGETED_{count+1:04}",
        "items": cart
    }
    filename = os.path.join(OUTPUT_DIR, f"targeted_{count+1:04}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cart_data, f, ensure_ascii=False, indent=2)
    count += 1
    if count >= NUM_CARTS:
        break

print(f"✅ 成功產生 {count} 筆 targeted 購物車測資")
