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

---

## 🚀 使用方式
1. 生成商品庫與折扣規則（`src/simulate/`）
2. 建立模擬購物車（`src/simulate/cart_gen.py`）
3. 使用演算法拆帳（`src/core/solver.py`）
4. 模擬推薦加購（`src/core/addon_recommender.py`）
5. 匯出訓練資料 → AI 模型訓練（`src/ai/`）
6. 訓練推薦模型：`src/ai/train_addon_model.py`
7. 推論推薦加購：`src/ai/predict_addon.py`，預測推薦商品 ID

---

## 📁 專案資料夾結構

<details>
<summary>點我展開</summary>

<br>

```text
CartWizard/
├── data/                      # ✅ 測試資料與輸出資料
│   ├── carts/                 # 兩千多筆購物車模擬樣本（JSON）
│   ├── raw/                   # 原始商品庫、折扣規則（JSON/CSV）
│   │   ├── discounts.json
│   │   └── products.json
│   ├── training/              # AI 訓練資料（含模型）
│   ├── carts/                 # 模擬生成的購物車資料
│   ├── results/               # 拆帳結果資料
│   └── training/              # AI 訓練資料（X, Y）
│   │   ├── addon_model.txt    # 加購推薦模型
│   │   ├── label2id.json      # 類別對應字典（推薦用）
│   │   ├── X.jsonl            # 拆帳訓練 X
│   │   ├── Y.jsonl            # 拆帳訓練 Y
│   │   ├── X_addon.jsonl      # 加購推薦 X
│   │   └── Y_addon.jsonl      # 加購推薦 Y
│   └── results/               # 拆帳結果輸出（可選）
│ 
├── notebooks/                 # 分析與視覺化 Notebook
│   └── addon_analysis.ipynb
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
- [ ] GUI or Web介面
- [ ] 匯出成推薦服務 API
- [ ] 支援使用者行為回饋強化 AI 模型
- [ ] 多版本折扣規則解析模組化
- [ ] 預測折扣總金額（回歸任務）
- [ ] 預測使用折扣組合（多標籤分類任務）
- [ ] 加購推薦模型（分類任務）
- [ ] 模型訓練可視化（誤差分佈、預測比較圖）

---

## 📜 License

本專案授權方式為 **MIT License**。  
可自由使用、修改與商業化，惟需保留原作者署名。

---

> 作者：林冠傑（Kuan-Chieh Lin）  
> 專案名稱：**CartWizard**  
> A smart discount-splitting & upsell recommender system for modern ecommerce.