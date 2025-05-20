import json
import os
import lightgbm as lgb
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error
from math import sqrt
from collections import Counter

X_PATH = "data/training/X.jsonl"
Y_PATH = "data/training/Y.jsonl"

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

def plot_results(y_true, y_pred):
    # 散佈圖：預測 vs 實際
    plt.figure(figsize=(6, 6))
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--')
    plt.xlabel("實際價格")
    plt.ylabel("預測價格")
    plt.title("預測 vs 實際價格（越貼近紅線越準）")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 誤差直方圖
    errors = abs(y_true - y_pred)
    plt.figure(figsize=(8, 4))
    plt.hist(errors, bins=30, color='skyblue', edgecolor='black')
    plt.xlabel("預測誤差（元）")
    plt.ylabel("出現次數")
    plt.title("預測誤差分佈")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    X_raw = load_jsonl(X_PATH)
    Y_raw = load_jsonl(Y_PATH)

    X = pd.DataFrame([extract_features(x) for x in X_raw])
    y = pd.Series([y["final_price"] for y in Y_raw])

    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    model = lgb.LGBMRegressor()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    rmse = sqrt(mean_squared_error(y_test, y_pred))
    print(f"\n📊 預測 RMSE（均方根誤差）：{rmse:.2f}")

    print("\n🎯 前 10 筆預測結果：")
    for i in range(10):
        real = y_test.iloc[i]
        pred = y_pred[i]
        diff = abs(real - pred)
        print(f"  - 實際: {real:>6.0f} ｜ 預測: {pred:>6.0f} ｜ 誤差: {diff:>6.0f}")

    plot_results(y_test.values, y_pred)

if __name__ == "__main__":
    main()
