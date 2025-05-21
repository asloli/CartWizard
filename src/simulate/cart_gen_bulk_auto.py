import os
import json
import random
from tqdm import tqdm

PRODUCT_PATH = "data/raw/products.json"
DISCOUNT_PATH = "data/raw/discounts.json"
OUTPUT_DIR = "data/carts/"
COUNT = 1000

# 載入商品與折扣資料
with open(PRODUCT_PATH, encoding="utf-8") as f:
    products = json.load(f)
with open(DISCOUNT_PATH, encoding="utf-8") as f:
    discounts = json.load(f)

# 建立商品ID→商品資訊對照表
product_dict = {p["id"]: p for p in products}

# 根據折扣內容建立「容易觸發折扣」商品池
boost_items = set()
for d in discounts:
    if d["type"] in ["滿件折扣", "組合折扣", "獨立折扣"] and "items" in d:
        boost_items.update(d["items"])

# 建立輸出資料夾
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 找出目前已存在的最大編號
existing = [int(f.split("auto_")[1].split(".json")[0]) for f in os.listdir(OUTPUT_DIR) if f.startswith("auto_")]
start_index = max(existing) + 1 if existing else 1

for i in tqdm(range(start_index, start_index + COUNT), desc="📦 產生購物車樣本"):
    cart_items = []
    used_ids = set()

    # 先放入 3~6 個 boost item 提高折扣觸發機率
    boost_list = list(boost_items)
    random.shuffle(boost_list)
    for pid in boost_list[:random.randint(3, 6)]:
        if pid in product_dict and pid not in used_ids:
            p = product_dict[pid]
            cart_items.append({"id": pid, "price": p["price"], "category": p["category"]})
            used_ids.add(pid)

    # 再加入隨機商品補足 15~25 件
    all_ids = list(product_dict.keys())
    while len(cart_items) < random.randint(15, 25):
        pid = random.choice(all_ids)
        if pid not in used_ids:
            p = product_dict[pid]
            cart_items.append({"id": pid, "price": p["price"], "category": p["category"]})
            used_ids.add(pid)

    cart_data = {
        "cart_id": f"auto_{i:04}",
        "items": cart_items
    }

    with open(os.path.join(OUTPUT_DIR, f"auto_{i:04}.json"), "w", encoding="utf-8") as f:
        json.dump(cart_data, f, ensure_ascii=False, indent=2)

print(f"✅ 已產生 {COUNT} 筆購物車資料，從 auto_{start_index:04} 開始")
