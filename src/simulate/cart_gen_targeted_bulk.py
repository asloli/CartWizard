import os
import json
import random
from tqdm import tqdm

PRODUCT_PATH = "data/raw/products.json"
DISCOUNT_PATH = "data/raw/discounts.json"
OUTPUT_DIR = "data/carts/targeted/"
COUNT = 500

# 載入資料
with open(PRODUCT_PATH, encoding="utf-8") as f:
    products = json.load(f)
with open(DISCOUNT_PATH, encoding="utf-8") as f:
    discounts = json.load(f)

product_dict = {p["id"]: p for p in products}
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 找出目前已存在的最大編號
existing = [int(f.split("targeted_")[1].split(".json")[0]) for f in os.listdir(OUTPUT_DIR) if f.startswith("targeted_")]
start_index = max(existing) + 1 if existing else 1

def pick_items_near_threshold():
    result = []
    for d in discounts:
        if d["type"] == "滿額折扣":
            eligible = [p for p in products if p["category"] == d["category"]]
            random.shuffle(eligible)
            total = 0
            picked = []
            for p in eligible:
                if total + p["price"] >= d["threshold"]:
                    continue
                picked.append(p)
                total += p["price"]
                if d["threshold"] - total < 300:
                    return picked
        elif d["type"] == "滿件折扣" and "items" in d and d["count"] > 1:
            if len(d["items"]) < d["count"]:
                continue
            sampled = random.sample(d["items"], d["count"] - 1)
            return [product_dict[i] for i in sampled if i in product_dict]
    return []

for i in tqdm(range(start_index, start_index + COUNT), desc="🎯 產生差一件觸發折扣樣本"):
    base = pick_items_near_threshold()
    if not base:
        continue
    used_ids = set()
    items = []
    for p in base:
        items.append({"id": p["id"], "price": p["price"], "category": p["category"]})
        used_ids.add(p["id"])

    while len(items) < random.randint(10, 20):
        p = random.choice(products)
        if p["id"] not in used_ids:
            items.append({"id": p["id"], "price": p["price"], "category": p["category"]})
            used_ids.add(p["id"])

    cart_data = {
        "cart_id": f"targeted_{i:04}",
        "items": items
    }

    with open(os.path.join(OUTPUT_DIR, f"targeted_{i:04}.json"), "w", encoding="utf-8") as f:
        json.dump(cart_data, f, ensure_ascii=False, indent=2)

print(f"✅ 已產生 {COUNT} 筆 targeted 購物車資料，從 targeted_{start_index:04} 開始")