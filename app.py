import streamlit as st

st.set_page_config(page_title="CartWizard", layout="centered")

st.title("🧙‍♂️ CartWizard 智慧購物系統")
st.markdown("""
歡迎使用 CartWizard！請透過上方選單切換頁面功能：

- 📑 **拆帳明細（上傳）**：上傳購物車，查看套用折扣後的明細與發票拆帳結果
- 🛍️ **推薦加購（上傳）**：上傳購物車，讓模型推薦最划算的加購商品
- 🛒 **購物模擬**：自由選擇商品模擬購物，加購推薦即時顯示，可儲存資料供模型訓練

👉 點選左側選單，開始使用！
""")