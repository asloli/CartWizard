# 📜 CHANGELOG

所有版本的功能進度與變更記錄。

---

## [v0.11] - 2025-05-21
### ✨ 新功能
- 🧠 整合 LightGBM 推薦模型到 Streamlit UI
- 🎯 顯示推薦商品信心值（predict_proba）
- 🧾 顯示推薦 Top-3 商品清單與機率
- 🛒 模擬選購頁面可儲存使用者選擇行為（接受 / 拒絕）
- 📊 折扣總額變化圖加入比較視覺化（matplotlib）

### 🗂 架構調整
- 📁 將原始 app.py 分為三個分頁：
  - `01_cart_summary.py`
  - `02_addon_recommend.py`
  - `03_cart_simulation.py`
- 🧭 新增首頁導覽 `app.py`，指引使用者進入分頁操作

### 📄 文件與維護
- ✅ 更新 `README.md` 結構與教學說明
- ✅ 製作 `.gitignore` 忽略資料與模型
- ✅ 生成 `requirements.txt`（streamlit, lightgbm 等）
