from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
import uvicorn

from src.core.solver import solve_cart_split
from src.ai.predict_addon import recommend_addon
from src.ai.train_addon_model import extract_features
from lightgbm import Booster

app = FastAPI()

# 允許所有來源的跨域請求（不使用 credentials，以便 * 可以生效）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "null"], # 可改為你的 GitHub Pages 網址
    allow_credentials=False, 
    allow_methods=["*"],
    allow_headers=["*"],
)

# 載入資料與模型
with open("data/raw/products.json", encoding="utf-8") as f:
    product_list = json.load(f)
    product_name_map = {p["id"]: p["name"] for p in product_list}
    product_dict = {p["id"]: p for p in product_list}

with open("data/raw/discounts.json", encoding="utf-8") as f:
    discount_rules = json.load(f)

model = Booster(model_file="data/training/addon_model.txt")

@app.post("/api/cart_summary")
async def cart_summary(file: UploadFile = File(...)):
    content = await file.read()
    cart_data = json.loads(content)
    result = solve_cart_split(cart_data["items"], discount_rules)
    for part in result:
        for item in part["items"]:
            item["name"] = product_name_map.get(item["id"], item["id"])
    return result

@app.post("/api/recommend_addon")
async def recommend_addon_api(file: UploadFile = File(...)):
    content = await file.read()
    cart_data = json.loads(content)

    # AI 推薦加購邏輯
    addon_id = recommend_addon(cart_data)

    items = cart_data.get("items", [])
    result_before = solve_cart_split(items, discount_rules)
    for part in result_before:
        for item in part["items"]:
            item["name"] = product_name_map.get(item["id"], item["id"])

    if addon_id:
        cart_data["items"].append(product_dict[addon_id])
    result_after = solve_cart_split(cart_data, discount_rules)
    for part in result_after:
        for item in part["items"]:
            item["name"] = product_name_map.get(item["id"], item["id"])

    return {
        "addon_id": addon_id,
        "before": result_before,
        "after": result_after
    }

@app.post("/api/simulate_addon")
async def simulate_addon(request: Request):
    payload = await request.json()
    items = payload.get("items", [])
    cart_data = {"items": items}

    all_ids = [p["id"] for p in product_list if p["id"] not in [i["id"] for i in items]]
    candidates = []
    for pid in all_ids:
        feature = extract_features(cart_data, pid)
        score = model.predict([feature])[0]
        candidates.append((pid, score))

    candidates.sort(key=lambda x: x[1], reverse=True)
    top = candidates[:5]
    enriched = [{"id": pid, "name": product_name_map.get(pid), "score": round(score, 3)} for pid, score in top]
    return {"recommendations": enriched}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)