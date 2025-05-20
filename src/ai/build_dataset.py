import os
import json
from glob import glob
from tqdm import tqdm
from collections import Counter
from core.solver import solve_cart_split

CART_DIR = "data/carts/"
DISCOUNT_PATH = "data/raw/discounts.json"
X_PATH = "data/training/X.jsonl"
Y_PATH = "data/training/Y.jsonl"
CATEGORY_LIST = ['衣服', '食品', '日用品', '3C']

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_jsonl(path, data_list):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in data_list:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def distance_to_nearest_threshold(total_price, discounts):
    diffs = []
    for d in discounts:
        if d['type'] == '滿額折扣':
            diff = max(0, d['threshold'] - total_price)
            diffs.append(diff)
    return min(diffs) if diffs else 0

def build_dataset():
    discount_rules = load_json(DISCOUNT_PATH)
    cart_files = sorted(glob(os.path.join(CART_DIR, "auto_*.json")))

    X_data = []
    Y_data = []

    for path in tqdm(cart_files, desc="🔄 建構資料集中"):
        cart = load_json(path)
        cart_id = cart["cart_id"]
        items = cart["items"]

        prices = [i["price"] for i in items]
        categories = [i["category"] for i in items]
        total_price = sum(prices)

        # 加入特徵欄位
        x = {
            "cart_id": cart_id,
            "items": items,
            "item_count": len(items),
            "total_price": total_price,
            "avg_price": total_price / len(items) if items else 0,
            "max_price": max(prices),
            "min_price": min(prices),
            "distance_to_full_discount": distance_to_nearest_threshold(total_price, discount_rules)
        }

        cat_count = Counter(categories)
        for cat in CATEGORY_LIST:
            x[f"cat_{cat}"] = cat_count.get(cat, 0)

        X_data.append(x)

        # Y：拆帳結果
        result_set = solve_cart_split(items, discount_rules)
        total_final = sum(r["result"]["final_price"] for r in result_set)
        total_discount = sum(r["result"]["total_discount"] for r in result_set)
        used_discounts = []
        for r in result_set:
            used_discounts += [d["id"] for d in r["result"]["used_discounts"]]

        Y_data.append({
            "cart_id": cart_id,
            "final_price": total_final,
            "total_discount": total_discount,
            "used_discounts": sorted(set(used_discounts))
        })

    save_jsonl(X_PATH, X_data)
    save_jsonl(Y_PATH, Y_data)
    print(f"✅ 輸出完成：共 {len(X_data)} 筆 → X: {X_PATH}，Y: {Y_PATH}")

if __name__ == "__main__":
    build_dataset()