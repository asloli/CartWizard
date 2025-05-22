import streamlit as st
import json
import os
import numpy as np
import pandas as pd
from lightgbm import Booster
from src.core.solver import solve_cart_split
from src.ai.train_addon_model import extract_features

st.set_page_config(page_title="🛒 購物模擬推薦", layout="wide")

with open("data/raw/products.json", encoding="utf-8") as f:
    product_list = json.load(f)
    product_dict = {p["id"]: p for p in product_list}
    product_name_map = {p["id"]: p["name"] for p in product_list}

with open("data/raw/discounts.json", encoding="utf-8") as f:
    discount_list = json.load(f)

model = Booster(model_file="data/training/addon_model.txt")

#🧱 UI：商品卡片 + 數量選擇器
st.title("🛒 自由選購商品並模擬加購推薦")

all_categories = sorted(set(p["category"] for p in product_list))
selected_categories = st.multiselect("分類篩選", all_categories, default=all_categories)

for p in product_list:
    if f"qty_{p['id']}" not in st.session_state:
        st.session_state[f"qty_{p['id']}"] = 0

filtered = [p for p in product_list if p["category"] in selected_categories]
cols_per_row = 4
for i in range(0, len(filtered), cols_per_row):
    row = st.columns(cols_per_row)
    for j, p in enumerate(filtered[i:i+cols_per_row]):
        with row[j]:
            st.markdown(f"#### {p['name']}")
            st.markdown(f"💰 ${p['price']}　📦 {p['category']}")
            st.number_input("數量", key=f"qty_{p['id']}", min_value=0, step=1, label_visibility="collapsed")

#✅ 計算總價 + 推薦模擬
selected_items = []
total_qty = 0
total_price = 0
for pid in product_dict:
    qty = st.session_state.get(f"qty_{pid}", 0)
    if qty > 0:
        p = product_dict[pid]
        selected_items += [{
            "id": p["id"],
            "price": p["price"],
            "category": p["category"]
        }] * qty
        total_qty += qty
        total_price += p["price"] * qty

st.divider()

if selected_items:
    st.subheader("✅ 已選商品與模擬結果")
    cart_data = {"cart_id": "ui_simulated", "items": selected_items}
    result = solve_cart_split(selected_items, discount_list)

    for i, order in enumerate(result, start=1):
        with st.expander(f"🧾 發票 {chr(64 + i)}", expanded=True):
            for item in order["items"]:
                st.markdown(f"- {product_name_map[item['id']]} (${item['price']})")
            if order["result"]["used_discounts"]:
                st.markdown("折扣：")
                for d in order["result"]["used_discounts"]:
                    st.markdown(f"`[{d['id']}] {d['type']} -${d['amount']}`")
            st.markdown(f"💰 小計：**${order['result']['final_price']}**")

#Top 3 推薦顯示 + 儲存
    base_ids = set(i["id"] for i in selected_items)
    candidates = [p for p in product_list if p["id"] not in base_ids]
    df_pred = pd.DataFrame([
        extract_features({"items": selected_items, "addon": p})
        for p in candidates
    ])
    probas = model.predict(df_pred)
    top_scores = np.max(probas, axis=1)
    top_indices = np.argsort(top_scores)[::-1][:3]
    top_results = [(candidates[i]["id"], top_scores[i]) for i in top_indices]
    recommended_id, confidence = top_results[0]

    st.subheader("🎯 模型推薦加購結果")
    st.caption(f"🧠 推薦：**{product_name_map[recommended_id]}**　({confidence*100:.1f}%)")
    for rank, (pid, prob) in enumerate(top_results, start=1):
        name = product_name_map.get(pid, pid)
        st.markdown(f"{rank}. {name} ({prob*100:.1f}%)")

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

#📦 底部結帳區塊（總數量 + 金額 + 儲存）
st.markdown(f"""
<div class="fixed-footer">
  <div class="summary">
    商品數：{total_qty}　總金額：${total_price}
  </div>
  <form action="#" method="post">
    <button>🛒 結帳</button>
  </form>
</div>
""", unsafe_allow_html=True)
