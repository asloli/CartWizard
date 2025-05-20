import os
import json
from glob import glob
from tqdm import tqdm

from core.solver import solve_cart_split

CART_DIR = "data/carts/"
PRODUCTS_PATH = "data/raw/products.json"
DISCOUNT_PATH = "data/raw/discounts.json"

X_OUT = "data/training/X_addon.jsonl"
Y_OUT = "data/training/Y_addon.jsonl"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_jsonl(path, data_list):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in data_list:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def simulate_addon(cart_items, all_products, discount_rules):
    # 原始商品 ID
    original_ids = set(i['id'] for i in cart_items)
    best_price = float('inf')
    best_item = None

    # 原始不加任何商品
    base_result = solve_cart_split(cart_items, discount_rules)
    base_price = sum(r["result"]["final_price"] for r in base_result)

    # 模擬每一件還沒買的商品加進來
    for p in all_products:
        if p['id'] in original_ids:
            continue
        test_cart = cart_items + [p]
        result = solve_cart_split(test_cart, discount_rules)
        total = sum(r["result"]["final_price"] for r in result)
        if total < best_price:
            best_price = total
            best_item = p['id']

    # 若沒有任何加購更省 → 回傳 None
    if base_price <= best_price:
        return None
    return best_item

def main():
    discount_rules = load_json(DISCOUNT_PATH)
    all_products = load_json(PRODUCTS_PATH)
    cart_files = sorted(glob(os.path.join(CART_DIR, "auto_*.json")))

    X_data = []
    Y_data = []

    for path in tqdm(cart_files, desc="🧠 模擬加購資料集中"):
        cart = load_json(path)
        cart_id = cart["cart_id"]
        items = cart["items"]

        addon = simulate_addon(items, all_products, discount_rules)

        X_data.append({
            "cart_id": cart_id,
            "items": items
        })
        Y_data.append({
            "cart_id": cart_id,
            "recommended_addon": addon  # 可為 None
        })

    save_jsonl(X_OUT, X_data)
    save_jsonl(Y_OUT, Y_data)
    print(f"\n✅ 加購推薦資料已儲存：\n  - {X_OUT}\n  - {Y_OUT}")

if __name__ == "__main__":
    main()
