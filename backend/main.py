# backend/main.py

from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import uvicorn

from src.core.solver import solve_cart_split
from src.ai.predict_addon import recommend_addon
from src.ai.train_addon_model import extract_features
from lightgbm import Booster
import datetime
import os

app = FastAPI()

# 允許所有來源跨域（不使用 credentials 以搭配 "*"）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    result = solve_cart_split(cart_data["items"], discount_rules)
    for part in result:
        for item in part["items"]:
            item["name"] = product_name_map.get(item["id"], item["id"])
    return result


@app.post("/api/recommend_addon")
async def recommend_addon_api(file: UploadFile = File(...)):
    content = await file.read()
    cart_data = json.loads(content)

    # AI 推薦加購 ID
    addon_id = recommend_addon(cart_data)

    # 加購前拆帳
    items = cart_data.get("items", [])
    result_before = solve_cart_split(items, discount_rules)
    for part in result_before:
        for item in part["items"]:
            item["name"] = product_name_map.get(item["id"], item["id"])

    # 加購後拆帳：只傳 list，不傳整個 dict
    items_after = items.copy()
    if addon_id:
        items_after.append(product_dict[addon_id])

    result_after = solve_cart_split(items_after, discount_rules)
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

    all_ids = [p["id"] for p in product_list if p["id"] not in [i["id"] for i in items]]
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

@app.get("/api/products")
async def get_products():
    """
    回傳完整的商品列表，供前端篩選與顯示用
    """
    return product_list

@app.get("/api/discounts")
async def get_discounts():
    """
    回傳折扣規則清單，供前端依 type 或 category 篩選
    """
    return discount_rules

@app.post("/api/save_simulation")
async def save_simulation(request: Request):
    """
    接收 { items: [...] }，做一次拆帳後把結果存成 JSON 檔到 data/user_simulated/
    """
    payload = await request.json()
    items = payload.get("items", [])
    # 先做拆帳
    summary = solve_cart_split(items, discount_rules)
    for part in summary:
        for item in part["items"]:
            item["name"] = product_name_map.get(item["id"], item["id"])

    # 確保目錄存在
    os.makedirs("data/user_simulated", exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    fn = f"data/user_simulated/sim_{ts}.json"
    with open(fn, "w", encoding="utf-8") as f:
        json.dump({"items": items, "summary": summary}, f, ensure_ascii=False, indent=2)

    return {"status": "OK", "file": fn}

if __name__ == "__main__":
    # 如果你在 backend/ 目錄下執行 python main.py，就請使用 "main:app"
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
