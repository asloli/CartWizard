# 📜 CHANGELOG

所有版本的功能進度與變更記錄。

---
## [v0.3-alpha] - 2025-05-28
### ✨ 新增
- 新增 AI 加購推薦功能（Top 3 推薦）
- 前端加購推薦結果以卡片樣式顯示，視覺效果更佳
- 後端使用 LightGBM 預測模型，支援多分類加購推薦分數
- 後端 `simulate_addon` API 修正特徵維度問題，穩定輸出結果
- README.md 更新，包含訓練流程與未來優化方向
- 更新 `.gitignore`，排除開發中無需追蹤的資料與編譯檔案
- 更新 `requirements.txt`，補上 numpy、streamlit 等漏裝套件

### 🐛 修正
- 修正 AI 模型輸入維度錯誤（改以 pandas DataFrame 傳入）
- 修正加購推薦輸出多維 array 問題，取最大分數作為推薦依據
- 調整後端 CORS 設定，確保前後端跨網域請求順利

### ⚡️ 優化
- 加入前端 console.log / debug info，方便開發測試
- 使用真實模擬加購資料（`03_simulation.html`），作為未來 AI 加購推薦訓練集
- 未來可考慮強化 UI 卡片 hover 效果、使用 Docker 部署

---

🎯 下一版本規劃：
- 持續擴充加購訓練資料，強化模型推薦精準度
- 引入可視化資料分析，協助模型調整
- 美化前端與移動裝置相容度
