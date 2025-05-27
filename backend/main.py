from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import json
import uvicorn
import datetime
import os

from src.core.solver import solve_cart_split
from src.ai.predict_addon import recommend_addon
from src.ai.train_addon_model import extract_features
from lightgbm import Booster

# 建立 FastAPI 實例
app = FastAPI()

# CORS 設定：允許所有來源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 將前端靜態檔案也掛載到同一個服務（同源解決 CORS）
# 假設所有 .html/.js/.css 都放在與本檔同層的 "static" 資料夾
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# 載入商品與折扣規則
with open("data/raw/products.json", encoding="utf-8") as f:
    product_list = json.load(f)
    product_name_map = {p["id"]: p["name"] for p in product_list}
    product_dict = {p["id"]: p for p in product_list}

with open("data/raw/discounts.json", encoding="utf-8") as f:
    discount_rules = json.load(f)

# 載入加購模型
model = Booster(model_file="data/training/addon_model.txt")


@app.post("/api/cart_summary")
async def cart_summary(file: UploadFile = File(...)):
    content = await file.read()
    cart_data = json.loads(content)

    result = solve_cart_split(cart_data.get("items", []), discount_rules)
    # 將商品名稱補回去
    for part in result:
        for item in part.get("items", []):
            item["name"] = product_name_map.get(item["id"], item["id"])
    return result


@app.post("/api/recommend_addon")
async def recommend_addon_api(file: UploadFile = File(...)):
    content = await file.read()
    cart_data = json.loads(content)

    # AI 推薦加購 ID
    addon_id = recommend_addon(cart_data)

    # 拆帳（前後）
    items = cart_data.get("items", [])
    result_before = solve_cart_split(items, discount_rules)
    for part in result_before:
        for item in part.get("items", []):
            item["name"] = product_name_map.get(item["id"], item["id"])

    items_after = items.copy()
    if addon_id:
        items_after.append(product_dict[addon_id])
    result_after = solve_cart_split(items_after, discount_rules)
    for part in result_after:
        for item in part.get("items", []):
            item["name"] = product_name_map.get(item["id"], item["id"])

    return {"addon_id": addon_id, "before": result_before, "after": result_after}


@app.post("/api/simulate_addon")
async def simulate_addon(request: Request):
    try:
        payload = await request.json()
        items = payload.get("items", [])

        # 準備候選商品
        all_ids = [p["id"] for p in product_list if p["id"] not in [i.get("id") for i in items]]
        candidates = []
        for pid in all_ids:
            feature = extract_features({"items": items}, pid)
            score = model.predict([feature])[0]
            candidates.append((pid, score))

        candidates.sort(key=lambda x: x[1], reverse=True)
        top = candidates[:5]
        enriched = [
            {"id": pid, "name": product_name_map.get(pid), "score": round(score, 3)}
            for pid, score in top
        ]
        return {"recommendations": enriched}

    except Exception as e:
        # 捕捉所有例外，並回傳 JSON 錯誤訊息
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/products")
async def get_products():
    return product_list


@app.get("/api/discounts")
async def get_discounts():
    return discount_rules


@app.post("/api/save_simulation")
async def save_simulation(request: Request):
    payload = await request.json()
    items = payload.get("items", [])

    summary = solve_cart_split(items, discount_rules)
    for part in summary:
        for item in part.get("items", []):
            item["name"] = product_name_map.get(item["id"], item["id"])

    os.makedirs("data/user_simulated", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    fn = f"data/user_simulated/sim_{ts}.json"
    with open(fn, "w", encoding="utf-8") as f:
        json.dump({"items": items, "summary": summary}, f, ensure_ascii=False, indent=2)

    return {"status": "OK", "file": fn}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
