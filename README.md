# CartWizard 🧙‍♂️  
智慧購物車折扣拆帳與加購推薦系統

---

## 🧠 功能簡介
- 自動計算最省錢的折扣拆帳組合
- 模擬加購行為，推薦「加一件更划算」商品
- 可生成訓練資料供 AI 模型學習推薦
- 適合作為演算法優化與推薦系統展示專案
- 🔮 AI 模型推薦最划算的「加購商品」（支援 `None` 回傳）
- ✅ 訓練樣本強化與推薦準確率追蹤
- 🧾 發票視覺化呈現、Shopee 風格卡片 UI
- 📊 折扣金額條狀圖，直觀比較加購前後省多少
- 🛍️ 模擬加購推薦後的消費者行為話術

---

## 🚀 使用方式
1. 生成商品庫與折扣規則（`src/simulate/`）
2. 建立模擬購物車（`src/simulate/cart_gen.py`）
3. 使用演算法拆帳（`src/core/solver.py`）
4. 模擬推薦加購（`src/core/addon_recommender.py`）
5. 匯出訓練資料 → AI 模型訓練（`src/ai/`）
6. 訓練推薦模型：`src/ai/train_addon_model.py`
7. 推論推薦加購：`src/ai/predict_addon.py`，預測推薦商品 ID

### ✅ 介面操作

1. 執行主程式：
   ```bash
   streamlit run app.py
   ```

2. 在網頁中上傳購物車檔案（JSON 格式），格式範例如下：
   ```json
   {
     "cart_id": "demo001",
     "items": [
       { "id": "P001", "price": 1514, "category": "衣服" },
       { "id": "P003", "price": 751, "category": "衣服" }
     ]
   }
   ```

3. 點選分頁：
   - 📑 拆帳明細：顯示原始最划算折扣拆帳發票
   - 🛍️ 推薦加購：顯示推薦加購商品，與原始訂單進行視覺化對比

---

## 📁 專案資料夾結構

<details>
<summary>點我展開</summary>

<br>

```text
CartWizard/
├── app.py                    # Streamlit 主介面程式（Shopee UI）
├── assets/
│   └── style.css             # Shopee 風格樣式表
├── data/                      # ✅ 測試資料與輸出資料
│   ├── carts/                 # 兩千多筆購物車模擬樣本（JSON）
│   ├── results/               # 拆帳結果資料
│   ├── raw/                   # 原始商品庫、折扣規則（JSON/CSV）
│   │   ├── discounts.json
│   │   └── products.json
│   ├── training/              # AI 訓練資料（含模型）
│   ├── carts/                 # 模擬生成的購物車資料
│   └── training/              # AI 訓練資料（X, Y）
│   │   ├── addon_model.txt    # 加購推薦模型
│   │   ├── label2id.json      # 類別對應字典（推薦用）
│   │   ├── X.jsonl            # 拆帳訓練 X
│   │   ├── Y.jsonl            # 拆帳訓練 Y
│   │   ├── X_addon.jsonl      # 加購推薦 X
│   │   └── Y_addon.jsonl      # 加購推薦 Y
│   └── results/               # 拆帳結果輸出（可選）
│ 
├── src/                  # ✅ 所有 Python 程式碼
│   ├── core/             # 核心邏輯：拆帳演算法、加購模擬
│   │   ├── cart.py
│   │   ├── discount.py
│   │   └── solver.py
│   ├── simulate/              # 商品 / 折扣 / 購物車資料模擬器
│   │   ├── product_gen.py
│   │   ├── discount_gen.py
│   │   ├── cart_gen.py
│   │   ├── cart_gen_large.py
│   │   ├── cart_gen_bulk_auto.py
│   │   └── cart_gen_targeted_bulk.py
│   ├── ai/                    # AI 訓練與推論程式
│   │   ├── build_dataset.py
│   │   ├── build_addon_dataset.py
│   │   ├── train_model.py
│   │   ├── train_addon_model.py
│   │   └── predict_addon.py
│   ├── utils/                 # 工具模組（如 io 處理）
│   │   └── io_utils.py（如有）
│   └── test_run_solver.py     # 演算法測試用腳本
│
├── notebooks/                 # 分析與視覺化 Notebook
│   └── addon_analysis.ipynb
│
├── tests/                     # 單元測試（未來可擴充）
│   └── test_solver.py（如有）
├── README.md             # ✅ 專案說明
├── requirements.txt      # 安裝所需套件
├── .gitignore            # 忽略項目
└── LICENSE               # 授權（可選 MIT 或 CC0）
```

</details>

---

## 🛠 TODO

- [x] 建立 Shopee 風格的 Streamlit UI
- [x] 折扣總額視覺化圖表（matplotlib）
- [ ] 模擬完整購物流程（多輪選購＋推薦行為記錄）
- [ ] 使用者操作行為 log 記錄器
- [ ] 訓練推薦模型（click, saved, action 強化）
- [ ] 加入商品圖片、hover 說明、推薦話術標語
- [ ] 對接 FastAPI 提供推薦結果為 API
- [ ] 模型誤差與折扣增益視覺化對照

---

## 📜 License

本專案授權方式為 **MIT License**。  
可自由使用、修改與商業化，惟需保留原作者署名。

---

> 作者：林冠傑（Kuan-Chieh Lin）  
> 專案名稱：**CartWizard**  
> A smart discount-splitting & upsell recommender system for modern ecommerce.