# 🧙‍♂️ CartWizard

智慧購物車折扣拆帳與加購推薦系統，支援前後端分離架構：
- 前端（純 HTML/JS/CSS）：可部署在 GitHub Pages
- 後端（FastAPI）：需在本地啟動，處理折扣演算與推薦邏輯

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

## 🚀 快速開始

### ✅ 第一步：安裝依賴
```bash
pip install -r requirements.txt
```

### ▶️ 第二步：啟動 FastAPI 本地伺服器
```bash
cd backend
uvicorn main:app --reload
```

### 🌐 第三步：開啟前端頁面（可放 GitHub Pages）
將 `frontend/` 目錄推上 GitHub 分支 `gh-pages`，網址為：
```
https://你的帳號.github.io/CartWizard/index.html
```

---

## 📁 專案資料夾結構

<details>
<summary>點我展開</summary>

<br>

```text
CartWizard/
├── frontend/                 # 🔸 部署於 GitHub Pages 的畫面
│   ├── index.html            # 拆帳頁（第 1 頁）
│   ├── cart_summary.js       # 對應 API 的邏輯（第 1 頁）
│   ├── style.css             # 共用樣式
│   └── ...                   # 後續將加入 02、03 頁
│
├── backend/                  # 🔹 本地執行的 FastAPI 後端
│   └── main.py               # 提供 /api/cart_summary 等端點
│
├── data/                     # 原始資料與訓練資料
│   ├── raw/products.json     # 商品資料庫
│   ├── raw/discounts.json    # 折扣規則
│   └── carts/                # 測試用購物車 JSON
│
├── src/                      # 核心邏輯與模型
│   └── core/solver.py        # 拆帳演算法
│
├── requirements.txt          # Python 相依套件
└── README.md                 # 本說明文件
```

</details>

---

## 🛠 TODO

- [x] 建立 Shopee 風格的 Streamlit UI
- [x] 折扣總額視覺化圖表（matplotlib）
- [ ] 匯出成推薦服務 API
- [ ] 支援使用者行為回饋強化 AI 模型
- [ ] 多版本折扣規則解析模組化
- [ ] 預測折扣總金額（回歸任務）
- [ ] 預測使用折扣組合（多標籤分類任務）
- [ ] 加購推薦模型（分類任務）
- [ ] 模型訓練可視化（誤差分佈、預測比較圖）


- [x] 拆帳系統與推薦演算法模組化
- [x] Streamlit 多分頁整合 + 模擬推薦
- [x] 顯示推薦信心值 + Top-3 商品
- [x] 支援推薦結果儲存成訓練資料
- [ ] 推薦熱度統計視覺化（bar chart）
- [ ] 使用者接受率追蹤與模型回訓
- [ ] 模型效能報告與混淆矩陣圖表

---

## 🔧 API 說明

### `/api/cart_summary`
- **方法**：POST
- **參數**：上傳購物車 JSON 檔案
- **回傳**：每張發票對應的商品、折扣、總價（含商品名稱對照）

---

## 📌 注意事項
- 前端部署後，功能需依賴你本地開啟的 Python API 才能正常執行
- 可在未來將 API 移至雲端平台（如 Railway、Render）以供公開使用

---

## 📜 版本記錄
- v0.1 初版功能完成：前後端分離架構、拆帳明細頁面完成


## 📜 License

本專案授權方式為 **MIT License**。  
可自由使用、修改與商業化，惟需保留原作者署名。

---

> 作者：林冠傑（Kuan-Chieh Lin）  
> 專案名稱：**CartWizard**  
> A smart discount-splitting & upsell recommender system for modern ecommerce.