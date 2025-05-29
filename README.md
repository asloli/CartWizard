
# 🛒 CartWizard

CartWizard 是一套智慧購物車系統，結合即時折扣拆帳和 AI 加購推薦功能，幫助消費者在購物時獲得最划算的折扣組合。

---

## 📦 目錄結構

```
CartWizard/
├── backend/                # FastAPI 後端服務
│   ├── main.py             # API 路由與核心處理
│   └── src/                # 核心演算法與 AI 模型
│       ├── core/solver.py
│       ├── ai/predict_addon.py
│       └── ai/train_addon_model.py
├── data/                   # 測試資料與模型
│   ├── raw/                # 原始商品與折扣規則
│   ├── training/           # AI 訓練檔與模型
│   ├── carts/              # 模擬產生的購物車資料
│   └── user_simulated/     # 使用者模擬結果
├── frontend/               # 前端頁面
│   ├── index.html
│   ├── 02_addon.html
│   ├── 03_simulation.html
│   ├── style.css
│   └── cart_simulation.js
└── README.md
```

---

## 🚀 功能總覽

✅ **商品與折扣規則即時載入**  
✅ **商品分類與折扣篩選**  
✅ **最划算折扣組合拆帳**  
✅ **AI 加購推薦（Top 3）**  
✅ **推薦結果以卡片式 UI 呈現**  
✅ **模擬結果保存至檔案**

---

## 🧪 模擬加購推薦

在 `03_simulation.html` 頁面中，使用者可以：
1. 選擇想購買的商品，系統會自動即時拆帳並計算折扣。
2. 前端會自動呼叫後端 `/simulate_addon` API，取得 AI 加購推薦結果。
3. 預覽 **Top 3 加購選項**，包含：
   - 單價與推薦分數
   - 加購後總價與節省金額
   - 使用到的折扣 ID

推薦結果已優化為卡片式樣式，使用者更易閱讀。

---

## 🌐 API 文件

### `/api/products`  
取得商品清單（JSON 格式）。

### `/api/discounts`  
取得折扣規則清單（JSON 格式）。

### `/api/cart_summary`  
**方法**：POST  
**上傳**：購物車（`FormData` 格式，`file` 欄位放 `cart.json`）  
**回傳**：折扣拆帳結果，含多張發票與每張發票的折扣明細。

### `/api/simulate_addon`  
**方法**：POST  
**傳入**：`{ "items": [...] }`（JSON 格式）  
**回傳**：`recommendations`（Top 3 加購推薦結果），包含加購後價格、節省金額、使用到的折扣等。

### `/api/save_simulation`  
**方法**：POST  
**傳入**：`{ "items": [...] }`（JSON 格式）  
**回傳**：`{"file": "data/user_simulated/sim_*.json"}`（已儲存檔案路徑）。

---

## ⚙️ 執行方式

### 1️⃣ 安裝依賴
```bash
pip install -r requirements.txt
```

### 2️⃣ 啟動後端 API
```bash
uvicorn backend.main:app --reload
```

### 3️⃣ 瀏覽前端
直接開啟 `https://asloli.github.io/CartWizard/index.html`，即可測試即時加購模擬與折扣推薦。

---

## 🔧 AI 模型訓練流程
1. 使用 `data/carts/` 中的真實或模擬購物車資料，生成訓練資料集（包含「加購前」與「加購後」的折扣拆帳結果）。
2. `train_addon_model.py` 會呼叫 `extract_features`，自動抽取購物車特徵（如商品種類分布、平均價格等）。
3. 使用 LightGBM 訓練分類模型，產出最適合加購推薦的模型 `addon_model.txt。`
4. 訓練後的模型可直接被 `/simulate_addon` API 使用，實現即時加購推薦。

---

## 💡 延伸想法

- 💻 **UI 美化**：前端已使用卡片式樣式，後續可再美化 hover/動畫效果。
- 🤖 **AI 模型優化**：目前使用 LightGBM，可替換更強的模型或持續擴充訓練資料。未來可從 03_simulation.html 產出的真實模擬加購資料中，萃取使用者偏好與實際的「加購意願」資料，強化 AI 推薦權重，讓 AI 更精準地推薦出能真正讓使用者願意多選購的加購商品。
- 🌍 **部署**：可使用 Docker / GitHub Pages 部署，快速體驗前後端整合。

---

## 📝 版本記錄
- `v0.3-alpha`：加入 AI 加購推薦、卡片式結果呈現、bug fix。

---

## 📜 License

本專案授權方式為 **MIT License**。  
可自由使用、修改與商業化，惟需保留原作者署名。

---

> 作者：林冠傑（Kuan-Chieh Lin）  
> 專案名稱：**CartWizard**  
> A smart discount-splitting & upsell recommender system for modern ecommerce.