# CartWizard 🧙‍♂️  
智慧購物車折扣拆帳與加購推薦系統

---

## 🧠 功能簡介
- 自動計算最省錢的折扣拆帳組合
- 模擬加購行為，推薦「加一件更划算」商品
- 可生成訓練資料供 AI 模型學習推薦
- 適合作為演算法優化與推薦系統展示專案

---

## 🚀 使用方式
1. 生成商品庫與折扣規則（`src/simulate/`）
2. 建立模擬購物車（`src/simulate/cart_gen.py`）
3. 使用演算法拆帳（`src/core/solver.py`）
4. 模擬推薦加購（`src/core/addon_recommender.py`）
5. 匯出訓練資料 → AI 模型訓練（`src/ai/`）

---

## 📁 專案資料夾結構

<details>
<summary>點我展開</summary>```

CartWizard/
├── data/ // 測試資料與輸出資料
│ ├── raw/ // 原始商品庫、折扣規則（JSON/CSV）
│ ├── carts/ // 模擬生成的購物車資料
│ ├── results/ // 拆帳結果資料
│ └── training/ // AI 訓練資料（X, Y）
│
├── src/ // 所有 Python 程式碼
│ ├── core/ // 核心邏輯：拆帳演算法、加購模擬
│ │ ├── cart.py
│ │ ├── discount.py
│ │ └── solver.py
│ ├── simulate/ // 測資模擬器（購物車、折扣、商品）
│ │ ├── product_gen.py
│ │ ├── cart_gen.py
│ │ └── discount_gen.py
│ ├── ai/ // AI 模型與訓練
│ │ ├── build_dataset.py
│ │ ├── train_model.py
│ │ └── predict.py
│ └── utils/ // 工具模組（JSON/CSV處理、格式轉換）
│ └── io_utils.py
│
├── notebooks/ // 測試、視覺化、分析 Jupyter 筆記本
│ └── analysis.ipynb
│
├── tests/ // 單元測試（pytest 或 unittest）
│ └── test_solver.py
│
├── README.md // 專案說明
├── requirements.txt // 安裝所需套件
├── .gitignore // 忽略項目（建議加入 pycache、*.pyc、/data/results/ 等）
└── LICENSE // 授權（可選 MIT 或 CC0）

```


</details>

---

## 🛠 TODO
- [ ] GUI or Web介面
- [ ] 匯出成推薦服務 API
- [ ] 支援使用者行為回饋強化 AI 模型
- [ ] 多版本折扣規則解析模組化

---

## 📜 License
本專案授權方式：MIT（可自行修改）

---

> 作者：林冠傑 ｜ 專案名稱：CartWizard  
> A smart discount-splitting & upsell recommender system for modern ecommerce.