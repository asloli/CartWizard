from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd

import json
import uvicorn
import datetime
import os

from src.core.solver import solve_cart_split
from src.ai.predict_addon import recommend_addon
from src.ai.train_addon_model import extract_features
from lightgbm import Booster

app = FastAPI()

# CORS：允許所有來源並處理 OPTIONS 預檢
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "https://asloli.github.io"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
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
    items_after = items.copy()
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
        payload       = await request.json()
        items         = payload.get("items", [])

        # 拆帳前總價
        before_orders = solve_cart_split(items, discount_rules)
        before_price  = sum(o["result"]["final_price"] for o in before_orders)

        # 準備候選商品ID
        existing_ids = {i["id"] for i in items}
        all_ids      = [p["id"] for p in product_list if p["id"] not in existing_ids]

        # 計算分數
        scored = []
        for pid in all_ids:
            try:
                sample  = {"items": items, "addon": product_dict[pid]}
                feature = extract_features(sample)

                input_df = pd.DataFrame([feature])
                score    = model.predict(input_df)[0]

                # ✨ 因為 score 是 array，取最大值或合適的機率值
                max_score = float(score.max())  # 或者 np.max(score)
                scored.append((pid, max_score))
            except Exception as e:
                print(f"❌ error for {pid}: {e}")
                continue


        print("✅ all_ids 候選數量:", len(all_ids))
        print("✅ scored:", scored)

        # 取前三名
        scored.sort(key=lambda x: x[1], reverse=True)
        top3 = scored[:3]

        recs = []
        for pid, score in top3:
            # 模擬加購後拆帳
            items_after  = items + [product_dict[pid]]
            after_orders = solve_cart_split(items_after, discount_rules)
            after_price  = sum(o["result"]["final_price"] for o in after_orders)
            saved        = before_price - after_price
            # 收集使用到的折扣 ID
            used_ds      = [
                d["id"]
                for o in after_orders
                for d in o["result"]["used_discounts"]
            ]

            recs.append({
                "id": pid,
                "name": product_name_map[pid],
                "score": round(score, 3),
                "addon_price": product_dict[pid]["price"],
                "after_price": after_price,
                "saved": saved,
                "used_discounts": used_ds
            })

        return JSONResponse(content={"recommendations": recs})

    except Exception as e:
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
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
