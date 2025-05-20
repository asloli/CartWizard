import json
import os
import pandas as pd
import lightgbm as lgb
from collections import Counter
from sklearn.metrics import accuracy_score, classification_report

X_PATH = "data/training/X_addon.jsonl"
Y_PATH = "data/training/Y_addon.jsonl"
CATEGORY_LIST = ['衣服', '食品', '日用品', '3C']

def load_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

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
    }

    cat_count = Counter(categories)
    for cat in CATEGORY_LIST:
        feature[f"cat_{cat}"] = cat_count.get(cat, 0)

    return feature

def build_label_encoder(y_raw):
    labels = set(y['recommended_addon'] for y in y_raw)
    labels = sorted(x for x in labels if x is not None)
    label2id = {l: i for i, l in enumerate(labels)}
    label2id[None] = len(label2id)  # 最後一位是 None
    id2label = {v: k for k, v in label2id.items()}
    return label2id, id2label

def main():
    X_raw = load_jsonl(X_PATH)
    Y_raw = load_jsonl(Y_PATH)

    # 轉換為特徵表與標籤
    X = pd.DataFrame([extract_features(x) for x in X_raw])

    label2id, id2label = build_label_encoder(Y_raw)
    y = pd.Series([label2id[y['recommended_addon']] for y in Y_raw])

    print(f"📘 共 {len(label2id)} 類別（含 None）：")
    for k, v in label2id.items():
        print(f"  {v:>2} → {k or 'None'}")

    # 切分資料
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # 訓練 LightGBM 多類別分類模型
    model = lgb.LGBMClassifier(objective='multiclass', num_class=len(label2id))
    model.fit(X_train, y_train)

    # 預測
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n✅ 預測準確率：{acc:.3%}")

    print("\n🎯 前 10 筆預測結果：")
    for i in range(10):
        pred_id = y_pred[i]
        true_id = y_test.iloc[i]
        pred_label = id2label[pred_id]
        true_label = id2label[true_id]
        correct = "✅" if pred_id == true_id else "❌"
        print(f"  {correct} 預測: {pred_label or 'None':>5} ｜ 實際: {true_label or 'None':>5}")

    print("\n📊 分類報告：")
    print(classification_report(y_test, y_pred, target_names=[id2label[i] or 'None' for i in sorted(id2label.keys())]))

if __name__ == "__main__":
    main()