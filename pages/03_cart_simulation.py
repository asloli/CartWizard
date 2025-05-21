import streamlit as st
import json
import os
import pandas as pd
import numpy as np
from lightgbm import Booster
from src.core.solver import solve_cart_split
from src.ai.train_addon_model import extract_features

st.set_page_config(page_title="🛒 購物模擬", layout="centered")
st.title("🛒 自由選購商品並模擬加購推薦")

# 載入 Booster 模型與標籤對照
model = Booster(model_file="data/training/addon_model.txt")
with open("data/training/label2id.json", encoding="utf-8") as f:
    label2id = json.load(f)
id2label = {v: k for k, v in label2id.items()}

with open("data/raw/products.json", encoding="utf-8") as f:
    product_list = json.load(f)
    product_name_map = {p["id"]: p["name"] for p in product_list}
    product_dict = {p["id"]: p for p in product_list}

with open("data/raw/discounts.json", encoding="utf-8") as f:
    discount_list = json.load(f)

product_discount_map = {}
for p in product_list:
    applicable = [d["type"] for d in discount_list if "items" in d and p["id"] in d["items"]]
    product_discount_map[p["id"]] = ", ".join(set(applicable)) if applicable else "—"

all_categories = sorted(set(p["category"] for p in product_list))
selected_categories = st.multiselect("篩選分類", all_categories, default=all_categories)
all_discount_types = sorted(set(d["type"] for d in discount_list if "type" in d))
selected_discount_types = st.multiselect("只顯示含有折扣的商品類型", all_discount_types, default=[])

filtered_products = []
for p in product_list:
    if p["category"] not in selected_categories:
        continue
    if selected_discount_types:
        types_for_product = [
            d["type"] for d in discount_list if "items" in d and p["id"] in d["items"]
        ]
        if not any(t in selected_discount_types for t in types_for_product):
            continue
    filtered_products.append(p)

product_table = [
    {
        "商品ID": p["id"],
        "商品名稱": p["name"],
        "價格": p["price"],
        "分類": p["category"],
        "數量": 0,
        "折扣類型": product_discount_map[p["id"]]
    }
    for p in filtered_products
]

df = st.data_editor(
    product_table,
    column_config={"數量": st.column_config.NumberColumn(min_value=0, step=1)},
    use_container_width=True,
    num_rows="dynamic",
    key="product_selector"
)

selected_items = []
for row in df:
    if row["數量"] > 0:
        for _ in range(row["數量"]):
            selected_items.append({
                "id": row["商品ID"],
                "price": row["價格"],
                "category": row["分類"]
            })

if selected_items:
    st.markdown("✅ **已選商品清單與模擬結果**")
    cart_data = {"cart_id": "ui_simulated", "items": selected_items}
    result = solve_cart_split(selected_items, discount_list)

    base_ids = set(i["id"] for i in selected_items)
    candidates = [p for p in product_list if p["id"] not in base_ids]
    features = [extract_features({"items": selected_items, "addon": p}) for p in candidates]
    df_pred = pd.DataFrame(features)
    probas = model.predict(df_pred)
    if probas.ndim == 1:
        probas = [[1 - p, p] for p in probas]

    top_indices = pd.Series([max(p) for p in probas]).sort_values(ascending=False).index[:3]
    top_results = [(candidates[i]["id"], max(probas[i])) for i in top_indices]
    top_label_idx = [int(np.argmax(p)) for p in probas]
    predicted_labels = [id2label[i] for i in top_label_idx]
    recommended_id, confidence = top_results[0]

    st.caption(f"🧠 模型推薦完成：{recommended_id} ({confidence*100:.1f}%)")
    for rank, (pid, prob) in enumerate(top_results, start=1):
        name = product_dict.get(pid, {}).get("name", pid)
        st.markdown(f"{rank}. **{name}** ({prob*100:.1f}%)")

    for i, order in enumerate(result, start=1):
        st.subheader(f"🧾 發票 {chr(64 + i)}")
        for item in order["items"]:
            name = product_name_map.get(item["id"], item["id"])
            st.markdown(f"- {name}：${item['price']}")
        st.markdown("**折扣內容：**")
        for d in order["result"]["used_discounts"]:
            st.markdown(f"- {d['type']} [{d['id']}]: -${d['amount']}")
        st.markdown(f"💰 **小計：${order['result']['final_price']}**")

    if recommended_id and recommended_id in product_dict:
        addon_item = product_dict[recommended_id]
        st.subheader("🎯 加購推薦結果")
        st.markdown(f"👉 系統推薦加購：**{addon_item['name']}** (${addon_item['price']})")

        accepted = st.radio("是否接受加購推薦？", ["尚未選擇", "✅ 接受推薦", "❌ 拒絕推薦"], index=0)

        if accepted != "尚未選擇":
            save_data = {
                "cart_id": "sim_" + "_".join([i["id"] for i in selected_items]),
                "base_items": selected_items,
                "recommended": recommended_id,
                "accepted": accepted == "✅ 接受推薦"
            }
            os.makedirs("data/user_simulated", exist_ok=True)
            save_path = f"data/user_simulated/{save_data['cart_id']}.json"
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            st.success(f"✅ 已儲存模擬購物記錄：{save_data['cart_id']}.json")
    else:
        st.info("目前無加購推薦")
