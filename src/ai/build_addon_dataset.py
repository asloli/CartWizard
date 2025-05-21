import os
import json
from glob import glob
from tqdm import tqdm

from src.core.solver import solve_cart_split
from src.core.discount import apply_discount


CART_DIR = "data/carts/"
TARGETED_DIR = "data/carts/targeted/"
SIM_DIR = "data/user_simulated/"
DISCOUNT_PATH = "data/raw/discounts.json"
PRODUCT_PATH = "data/raw/products.json"
X_PATH = "data/training/X_addon.jsonl"
Y_PATH = "data/training/Y_addon.jsonl"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_jsonl(path, data_list):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in data_list:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def calc_extra_features(original_items, addon_item, discount_rules):
    before = solve_cart_split(original_items, discount_rules)
    after = solve_cart_split(original_items + [addon_item], discount_rules)

    before_price = sum(r["result"]["final_price"] for r in before)
    after_price = sum(r["result"]["final_price"] for r in after)
    saved = before_price - after_price

    before_discounts = set(d["id"] for r in before for d in r["result"]["used_discounts"])
    after_discounts = set(d["id"] for r in after for d in r["result"]["used_discounts"])
    triggered = len(after_discounts - before_discounts)

    return saved, triggered

def build_dataset():
    discount_rules = load_json(DISCOUNT_PATH)
    products = load_json(PRODUCT_PATH)
    product_dict = {p["id"]: p for p in products}

    cart_files = sorted(glob(os.path.join(CART_DIR, "*.json")))
    targeted_files = sorted(glob(os.path.join(TARGETED_DIR, "*.json")))
    sim_files = sorted(glob(os.path.join(SIM_DIR, "*.json")))

    X_data = []
    Y_data = []

    all_cart_sources = [
        (cart_files, "🛒 原始購物車資料"),
        (targeted_files, "🎯 Targeted 加購樣本"),
    ]

    for file_list, label in all_cart_sources:
        for path in tqdm(file_list, desc=label):
            cart = load_json(path)
            cart_id = cart["cart_id"]
            base_items = cart["items"]
            base_ids = set(i["id"] for i in base_items)

            base_result = solve_cart_split(base_items, discount_rules)

            for candidate in products:
                pid = candidate["id"]
                if pid in base_ids:
                    continue
                saved, triggered = calc_extra_features(base_items, candidate, discount_rules)
                X_data.append({
                    "cart_id": cart_id,
                    "items": base_items,
                    "addon": candidate,
                    "saved_by_addon": saved,
                    "triggered_discounts": triggered
                })
                is_better = saved > 0
                Y_data.append({
                    "cart_id": cart_id,
                    "recommended_addon": pid if is_better else None
                })

    for path in tqdm(sim_files, desc="📥 整合使用者模擬資料中"):
        sim = load_json(path)
        base_items = sim["base_items"]
        recommended_id = sim["recommended"]
        accepted = sim["accepted"]
        cart_id = sim.get("cart_id", os.path.basename(path).replace(".json", ""))

        if recommended_id not in product_dict:
            continue

        addon = product_dict[recommended_id]
        saved, triggered = calc_extra_features(base_items, addon, discount_rules)

        X_data.append({
            "cart_id": cart_id,
            "items": base_items,
            "addon": addon,
            "saved_by_addon": saved,
            "triggered_discounts": triggered
        })
        Y_data.append({
            "cart_id": cart_id,
            "recommended_addon": recommended_id if accepted else None
        })

    save_jsonl(X_PATH, X_data)
    save_jsonl(Y_PATH, Y_data)
    print(f"✅ 輸出完成：共 {len(X_data)} 筆 → X: {X_PATH}，Y: {Y_PATH}")

if __name__ == "__main__":
    build_dataset()
