import os
import json
from glob import glob
from tqdm import tqdm

from core.solver import solve_cart_split
from core.discount import apply_discount

CART_DIR = "data/carts/"
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
    """計算加購後省下多少錢與新增觸發幾個折扣"""
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
    cart_files = sorted(glob(os.path.join(CART_DIR, "*.json")))

    X_data = []
    Y_data = []

    for path in tqdm(cart_files, desc="🔄 建構推薦加購資料集中"):
        cart = load_json(path)
        cart_id = cart["cart_id"]
        base_items = cart["items"]
        base_ids = set(i["id"] for i in base_items)

        # 拆帳前的結果
        base_result = solve_cart_split(base_items, discount_rules)
        base_final_price = sum(r["result"]["final_price"] for r in base_result)

        for candidate in products:
            pid = candidate["id"]
            if pid in base_ids:
                continue  # 排除已在購物車內的

            saved, triggered = calc_extra_features(base_items, candidate, discount_rules)

            # X：特徵包含購物車、加購商品、可省金額、觸發折扣數
            X_data.append({
                "cart_id": cart_id,
                "items": base_items,
                "addon": candidate,
                "saved_by_addon": saved,
                "triggered_discounts": triggered
            })

            # Y：是否推薦
            is_better = saved > 0  # 有節省就推薦
            Y_data.append({
                "cart_id": cart_id,
                "recommended_addon": pid if is_better else None
            })

    save_jsonl(X_PATH, X_data)
    save_jsonl(Y_PATH, Y_data)
    print(f"✅ 輸出完成：共 {len(X_data)} 筆 → X: {X_PATH}，Y: {Y_PATH}")

if __name__ == "__main__":
    build_dataset()
