import streamlit as st
import json
import matplotlib.pyplot as plt
from src.core.solver import solve_cart_split
from src.ai.predict_addon import recommend_addon

def draw_discount_comparison(before_discount, after_discount):
    plt.rcParams['font.family'] = 'Microsoft JhengHei'
    fig, ax = plt.subplots(figsize=(4, 2))
    bars = ax.bar(["原始", "加購"], [before_discount, after_discount], color=["#FF6666", "#66CC99"])
    ax.set_ylabel("折扣金額")
    ax.set_title("折扣總額變化", fontsize=12)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"${height}", xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 5), textcoords="offset points",
                    ha='center', va='bottom', fontsize=10)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig

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

st.title("🛍️ 推薦加購商品")

with open("data/raw/products.json", encoding="utf-8") as f:
    product_list = json.load(f)
    product_name_map = {p["id"]: p["name"] for p in product_list}
    product_dict = {p["id"]: p for p in product_list}

with open("assets/style.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📤 上傳購物車 JSON 檔案", type="json")

if uploaded_file:
    cart_data = json.load(uploaded_file)
    base_items = cart_data["items"]
    base_ids = set(i["id"] for i in base_items)
    discounts = json.load(open("data/raw/discounts.json", encoding="utf-8"))
    original_result = solve_cart_split(base_items, discounts)

    recommended_id = recommend_addon(cart_data)

    if not recommended_id:
        st.info("目前無加購推薦")
    elif recommended_id not in product_dict:
        st.warning(f"找不到推薦商品 {recommended_id}")
    else:
        addon_item = product_dict[recommended_id]
        new_items = base_items + [addon_item]
        new_result = solve_cart_split(new_items, discounts)
        before_price = sum(r["result"]["final_price"] for r in original_result)
        after_price = sum(r["result"]["final_price"] for r in new_result)
        saved = before_price - after_price
        new_total_original = sum(i["price"] for i in new_items)
        new_total_discount = new_total_original - after_price

        st.markdown(f"✅ 推薦加購商品：**{addon_item['name']}**")
        if saved > 0:
            st.success(f"💡 加購後可節省：**${saved}**")
        elif saved == 0:
            st.markdown(f"✨ 加購 **{addon_item['name']}** 搭配使用更受歡迎")
        else:
            st.markdown(f"🎁 組合購買 **{addon_item['name']}** 是熱門選擇")

        st.markdown("### 📊 折扣總額變化")
        fig = draw_discount_comparison(
            sum(r["result"]["total_discount"] for r in original_result),
            sum(r["result"]["total_discount"] for r in new_result)
        )
        st.pyplot(fig)

        st.markdown("### 🧾 發票內容對比")
        max_len = max(len(original_result), len(new_result))
        for i in range(max_len):
            st.markdown(f"#### 發票 {chr(65 + i)}")
            col1, col2 = st.columns(2)
            with col1:
                if i < len(original_result):
                    render_invoice_card("原始訂單",
                                        original_result[i]["items"],
                                        original_result[i]["result"]["used_discounts"],
                                        original_result[i]["result"]["final_price"],
                                        product_name_map)
                else:
                    st.info("（原始無此發票）")
            with col2:
                if i < len(new_result):
                    render_invoice_card("加購後訂單",
                                        new_result[i]["items"],
                                        new_result[i]["result"]["used_discounts"],
                                        new_result[i]["result"]["final_price"],
                                        product_name_map)
                else:
                    st.info("（加購無此發票）")
