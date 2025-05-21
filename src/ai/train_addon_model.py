import json
import os
import pandas as pd
import lightgbm as lgb
from collections import Counter
from sklearn.metrics import accuracy_score, classification_report

X_PATH = "data/training/X_addon.jsonl"
Y_PATH = "data/training/Y_addon.jsonl"
DISCOUNT_PATH = "data/raw/discounts.json"
CATEGORY_LIST = ['衣服', '食品', '日用品', '3C']

def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# 加入滿額折扣距離特徵
discount_rules = load_json(DISCOUNT_PATH)
def distance_to_nearest_threshold(total_price, discounts):
    diffs = []
    for d in discounts:
        if d['type'] == '滿額折扣':
            diff = max(0, d['threshold'] - total_price)
            diffs.append(diff)
    return min(diffs) if diffs else 0

def extract_features(cart_item):
    items = cart_item["items"]
    prices = [i["price"] for i in items]
    categories = [i["category"] for i in items]

    feature = {
        "item_count": len(items),
        "total_price": sum(prices),
        "avg_price": sum(prices) / len(prices) if items else 0,
        "max_price": max(prices),
        "min_price": min(prices),
        "addon_price": cart_item["addon"]["price"],
        "saved_by_addon": cart_item.get("saved_by_addon", 0),
        "triggered_discounts": cart_item.get("triggered_discounts", 0),
    }

    # 分類數量
    cat_count = Counter(categories)
    for cat in CATEGORY_LIST:
        feature[f"cat_{cat}"] = cat_count.get(cat, 0)

    # 距離滿額門檻
    feature["distance_to_full_discount"] = distance_to_nearest_threshold(
        feature["total_price"], discount_rules
    )

    return feature

def build_label_encoder(y_raw):
    labels = set(y['recommended_addon'] for y in y_raw)
    labels = sorted(x for x in labels if x is not None)
    label2id = {l: i for i, l in enumerate(labels)}
    label2id[None] = len(label2id)
    id2label = {v: k for k, v in label2id.items()}
    return label2id, id2label

def main():
    X_raw = load_jsonl(X_PATH)
    Y_raw = load_jsonl(Y_PATH)

    X = pd.DataFrame([extract_features(x) for x in X_raw])
    label2id, id2label = build_label_encoder(Y_raw)

    # 🔽 儲存 label2id 對照表供推論使用
    with open("data/training/label2id.json", "w", encoding="utf-8") as f:
        json.dump(label2id, f, ensure_ascii=False, indent=2)

    y = pd.Series([label2id[y["recommended_addon"]] for y in Y_raw])

    # 🔁 加入 sample_weight：推薦成功為 1，拒絕為 0.2 權重
    sample_weight = [1.0 if y["recommended_addon"] else 0.2 for y in Y_raw]

    print(f"📘 共 {len(label2id)} 類別（含 None）：")
    for k, v in label2id.items():
        print(f"  {v:>2} → {k or 'None'}")

    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]
    w_train = sample_weight[:split]
    w_test = sample_weight[split:]

    model = lgb.LGBMClassifier(objective="multiclass", num_class=len(label2id))
    model.fit(X_train, y_train, sample_weight=w_train)
    model.booster_.save_model("data/training/addon_model.txt")

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n✅ 預測準確率：{acc:.3%}")

    print("\n📊 分類報告：")
    labels_in_test = sorted(set(y_test))
    print(classification_report(
        
        y_test, y_pred,
        labels=labels_in_test,
        target_names = [id2label[i] if id2label[i] is not None else "None" for i in labels_in_test],
        zero_division=0
    ))

if __name__ == "__main__":
    main()
