import os
import json
from glob import glob
from tqdm import tqdm

from core.solver import solve_cart_split

CART_DIR = "data/carts/"
DISCOUNT_PATH = "data/raw/discounts.json"
X_PATH = "data/training/X.jsonl"
Y_PATH = "data/training/Y.jsonl"

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_jsonl(path, data_list):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in data_list:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

def build_dataset():
    # 讀取折扣規則
    discount_rules = load_json(DISCOUNT_PATH)

    # 取得購物車清單（auto_開頭）
    cart_files = sorted(glob(os.path.join(CART_DIR, "auto_*.json")))

    X_data = []
    Y_data = []

    for path in tqdm(cart_files, desc="🔄 建構資料集中"):
        cart = load_json(path)
        cart_id = cart["cart_id"]
        items = cart["items"]

        # X：原始購物車內容
        X_data.append({
            "cart_id": cart_id,
            "items": items
        })

        # Y：拆帳後的結果
        result_set = solve_cart_split(items, discount_rules)

        # 多張發票合併資訊
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

    # 輸出訓練資料集
    save_jsonl(X_PATH, X_data)
    save_jsonl(Y_PATH, Y_data)
    print(f"✅ 輸出完成：共 {len(X_data)} 筆 → X: {X_PATH}，Y: {Y_PATH}")

if __name__ == "__main__":
    build_dataset()