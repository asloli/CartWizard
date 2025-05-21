import json
import pandas as pd
import lightgbm as lgb
from src.ai.train_addon_model import extract_features

MODEL_PATH = "data/training/addon_model.txt"
LABEL2ID_PATH = "data/training/label2id.json"
PRODUCTS_PATH = "data/raw/products.json"

# 載入模型與類別編碼
def load_model():
    model = lgb.Booster(model_file=MODEL_PATH)
    with open(LABEL2ID_PATH, encoding="utf-8") as f:
        label2id = json.load(f)
    id2label = {v: k for k, v in label2id.items()}
    return model, id2label

# 單次預測：傳入購物車資料，回傳推薦商品 ID 或 None
def recommend_addon(cart_data):
    model, id2label = load_model()
    with open(PRODUCTS_PATH, encoding="utf-8") as f:
        products = json.load(f)

    base_items = cart_data["items"]
    base_ids = set(i["id"] for i in base_items)

    candidates = []
    for p in products:
        if p["id"] in base_ids:
            continue
        sample = {
            "items": base_items,
            "addon": p
        }
        feature = extract_features(sample)
        candidates.append((p["id"], feature))

    if not candidates:
        return None

    df = pd.DataFrame([f for _, f in candidates])
    preds = model.predict(df)
    top_idx = preds.argmax()
    top_label = int(preds[top_idx].argmax()) if preds.ndim == 2 else preds.argmax()
    predicted_addon = id2label.get(top_label)

    return predicted_addon if predicted_addon not in [None, "None"] else None
