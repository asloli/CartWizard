import json
import pandas as pd
import lightgbm as lgb
from collections import Counter

# 模型與標籤對應路徑
MODEL_PATH = "data/training/addon_model.txt"
LABEL_MAP_PATH = "data/training/label2id.json"
CATEGORY_LIST = ['衣服', '食品', '日用品', '3C']

def extract_features(cart, discount_rules):
    items = cart["items"]
    prices = [i["price"] for i in items]
    categories = [i["category"] for i in items]
    addon = cart.get("addon", {"price": 0})

    feature = {
        "item_count": len(items),
        "total_price": sum(prices),
        "avg_price": sum(prices) / len(prices) if items else 0,
        "max_price": max(prices),
        "min_price": min(prices),
        "addon_price": addon.get("price", 0),
        "saved_by_addon": cart.get("saved_by_addon", 0),
        "triggered_discounts": cart.get("triggered_discounts", 0),
    }

    cat_count = Counter(categories)
    for cat in CATEGORY_LIST:
        feature[f"cat_{cat}"] = cat_count.get(cat, 0)

    # 距離最近滿額門檻
    full_thresholds = [d["threshold"] for d in discount_rules if d["type"] == "滿額折扣"]
    if full_thresholds:
        feature["distance_to_full_discount"] = min(
            [max(0, th - feature["total_price"]) for th in full_thresholds]
        )
    else:
        feature["distance_to_full_discount"] = 0

    return feature

def predict_addon(cart_path, discount_path):
    with open(cart_path, "r", encoding="utf-8") as f:
        cart = json.load(f)
    with open(discount_path, "r", encoding="utf-8") as f:
        discount_rules = json.load(f)
    with open(LABEL_MAP_PATH, "r", encoding="utf-8") as f:
        label2id = json.load(f)
    id2label = {v: k for k, v in label2id.items()}

    model = lgb.Booster(model_file=MODEL_PATH)
    feat = extract_features(cart, discount_rules)
    X = pd.DataFrame([feat])
    pred_id = int(model.predict(X).argmax())
    pred_label = id2label.get(pred_id, None)

    print(f"\n🛒 此購物車推薦加購商品為：{pred_label or 'None'}")

if __name__ == "__main__":
    predict_addon("data/carts/cart_001.json", "data/raw/discounts.json")