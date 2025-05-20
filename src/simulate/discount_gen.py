import json
import os
import random

OUTPUT_PATH = "data/raw/discounts.json"

CATEGORIES = ['衣服', '食品', '3C', '日用品']
BRANDS = ['A店', 'B鋪', 'C百貨', 'D商行']
DISCOUNT_ID = 1

def next_id():
    global DISCOUNT_ID
    result = f"D{DISCOUNT_ID:03d}"
    DISCOUNT_ID += 1
    return result

def random_bool(p=0.3):
    return random.random() < p

def generate_discounts():
    discounts = []

    # 滿額折扣 group = amount
    for _ in range(3):
        discounts.append({
            "id": next_id(),
            "type": "滿額折扣",
            "threshold": random.randint(800, 3000),
            "discount": random.choice([100, 200, 300]),
            "exclusive": False,
            "stackable": True,
            "group": "amount"
        })

    # 滿件折扣 group = count
    for _ in range(3):
        discounts.append({
            "id": next_id(),
            "type": "滿件折扣",
            "category": random.choice(CATEGORIES),
            "count": random.randint(2, 5),
            "discount": random.choice([50, 100]),
            "exclusive": False,
            "stackable": True,
            "group": "count"
        })

    # 分類折扣（品類券）
    for _ in range(2):
        discounts.append({
            "id": next_id(),
            "type": "分類折扣",
            "category": random.choice(CATEGORIES),
            "percent": random.choice([0.85, 0.9]),
            "exclusive": False,
            "stackable": True
        })

    # 單品折扣（多為不可疊加）
    for pid in random.sample([f"P{i+1:03d}" for i in range(50)], 4):
        discounts.append({
            "id": next_id(),
            "type": "單品折扣",
            "product_id": pid,
            "percent": random.choice([0.7, 0.8, 0.85]),
            "exclusive": random_bool(0.2),
            "stackable": False
        })

    # 組合折扣（exclusive 固定為 True）
    for _ in range(3):
        items = random.sample([f"P{i+1:03d}" for i in range(50)], k=2)
        discounts.append({
            "id": next_id(),
            "type": "組合折扣",
            "items": items,
            "discount": random.choice([150, 200, 300]),
            "exclusive": True,
            "stackable": False
        })

    # 品牌券（只能某品牌商品使用）
    for _ in range(2):
        discounts.append({
            "id": next_id(),
            "type": "品牌折扣",
            "brand": random.choice(BRANDS),
            "percent": random.choice([0.85, 0.9]),
            "exclusive": False,
            "stackable": True
        })

    # 限時折扣（不能疊加）
    discounts.append({
        "id": next_id(),
        "type": "限時折扣",
        "percent": 0.9,
        "exclusive": True,
        "stackable": False,
        "note": "週末限定"
    })

    return discounts

def save_discounts(discounts, path=OUTPUT_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(discounts, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    discounts = generate_discounts()
    save_discounts(discounts)
    print(f"✅ 折扣規則（現實導向）已儲存至 {OUTPUT_PATH}")