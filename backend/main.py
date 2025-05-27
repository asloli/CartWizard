from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import uvicorn
import datetime
import os

from src.core.solver import solve_cart_split
from src.ai.predict_addon import recommend_addon
from src.ai.train_addon_model import extract_features
from lightgbm import Booster

app = FastAPI()

# CORS 設定：允許前端 (包含 GitHub Pages) 存取
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://asloli.github.io"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 載入商品與折扣規則
def _load_data():
    with open("data/raw/products.json", encoding="utf-8") as f:
        products = json.load(f)
    with open("data/raw/discounts.json", encoding="utf-8") as f:
        discounts = json.load(f)
    return products, discounts

product_list, discount_rules = _load_data()
product_name_map = {p["id"]: p["name"] for p in product_list}
product_dict     = {p["id"]: p for p in product_list}

# 載入加購模型
model = Booster(model_file="data/training/addon_model.txt")

@app.post("/api/cart_summary")
async def cart_summary(file: UploadFile = File(...)):
    content = await file.read()
    cart_data = json.loads(content)

    result = solve_cart_split(cart_data.get("items", []), discount_rules)
    for part in result:
        for item in part.get("items", []):
            item["name"] = product_name_map.get(item["id"], item["id"])
    return result

@app.post("/api/recommend_addon")
async def recommend_addon_api(file: UploadFile = File(...)):
    content = await file.read()
    cart_data = json.loads(content)

    addon_id = recommend_addon(cart_data)
    items = cart_data.get("items", [])

    before = solve_cart_split(items, discount_rules)
    for part in before:
        for item in part.get("items", []):
            item["name"] = product_name_map.get(item["id"], item["id"])

    items_after = list(items)
    if addon_id:
        items_after.append(product_dict[addon_id])
    after = solve_cart_split(items_after, discount_rules)
    for part in after:
        for item in part.get("items", []):
            item["name"] = product_name_map.get(item["id"], item["id"])

    return {"addon_id": addon_id, "before": before, "after": after}

@app.post("/api/simulate_addon")
async def simulate_addon(request: Request):
    try:
        payload = await request.json()
        items = payload.get("items", [])

        # 只保留還沒在購物車裡的商品
        existing = {i.get("id") for i in items}
        all_ids = [p["id"] for p in product_list if p["id"] not in existing]

        candidates = []
        for pid in all_ids:
            try:
                # per‐item feature extract + predict，各自捕捉例外
                feature = extract_features({"items": items}, pid)
                score = model.predict([feature])[0]
                candidates.append((pid, score))
            except Exception:
                # 這個 pid 如果失敗就跳過
                continue

        # 排序、取前五、並補 name
        candidates.sort(key=lambda x: x[1], reverse=True)
        top5 = candidates[:5]
        recommendations = [
            {"id": pid, "name": product_name_map.get(pid), "score": round(score, 3)}
            for pid, score in top5
        ]

        return {"recommendations": recommendations}

    except Exception as e:
        # 如果整個流程意外失敗，也回傳空列表，不讓前端拿不到 recommendations
        return JSONResponse(status_code=200, content={
            "recommendations": [],
            "error": str(e)
        })
    
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
    filepath = f"data/user_simulated/sim_{ts}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({"items": items, "summary": summary}, f, ensure_ascii=False, indent=2)

    return {"status": "OK", "file": filepath}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)