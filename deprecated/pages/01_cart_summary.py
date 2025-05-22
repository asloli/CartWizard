import streamlit as st
import json
from src.core.solver import solve_cart_split

# 載入產品資料
with open("data/raw/products.json", encoding="utf-8") as f:
    product_list = json.load(f)
    product_name_map = {p["id"]: p["name"] for p in product_list}

with open("assets/style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📑 拆帳明細")
st.markdown("請上傳購物車 JSON 檔案，查看折扣拆帳與發票結果")

uploaded_file = st.file_uploader("📤 上傳購物車 JSON 檔案", type="json")

def render_invoice_card(title, items, discounts, final_price, product_name_map):
    st.markdown(f"<div class='invoice-card'><h4>{title}</h4>", unsafe_allow_html=True)
    for item in items:
        name = product_name_map.get(item["id"], item["id"])
        st.markdown(f"<div class='item-line'>🛒 {name} × 1 = ${item['price']}</div>", unsafe_allow_html=True)
    if discounts:
        st.markdown("折扣：", unsafe_allow_html=True)
        for d in discounts:
            class_name = f"discount-badge discount-{d['type']}"
            st.markdown(
                f"<span class='{class_name}'>[{d['id']}] {d['type']}：- ${d['amount']}</span>",
                unsafe_allow_html=True)
    else:
        st.markdown("折扣：<span style='color:#999;'>(無)</span>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin-top:4px;font-weight:bold;'>💰 小計：${final_price}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

if uploaded_file:
    cart_data = json.load(uploaded_file)
    base_items = cart_data["items"]
    discounts = json.load(open("data/raw/discounts.json", encoding="utf-8"))
    result = solve_cart_split(base_items, discounts)

    st.subheader("🧾 發票明細")
    total_original, total_final, total_discount = 0, 0, 0

    for i, order in enumerate(result, start=1):
        items = order["items"]
        result_data = order["result"]
        used_discounts = result_data.get("used_discounts", [])
        original_total = sum(item["price"] for item in items)
        final_price = result_data["final_price"]
        discount_total = result_data["total_discount"]

        render_invoice_card(f"🧾 發票 {chr(64 + i)}", items, used_discounts, final_price, product_name_map)
        total_original += original_total
        total_final += final_price
        total_discount += discount_total

    st.subheader("🧮 結帳總覽")
    st.markdown(f"- 💵 原始總金額：**${total_original}**")
    st.markdown(f"- 🎁 折扣總金額：**- ${total_discount}**")
    st.markdown(f"- 💰 最終付款金額：**${total_final}**")
