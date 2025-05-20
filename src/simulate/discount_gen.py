import json
import os

DISCOUNTS = [
    {
        "id": "D001",
        "type": "滿額折扣",
        "threshold": 1000,
        "discount": 100
    },
    {
        "id": "D002",
        "type": "分類折扣",
        "category": "衣服",
        "percent": 0.9
    },
    {
        "id": "D003",
        "type": "滿件折扣",
        "category": "食品",
        "count": 3,
        "discount": 50
    },
    {
        "id": "D004",
        "type": "單品折扣",
        "product_id": "P005",
        "percent": 0.85
    }
]

OUTPUT_PATH = 'data/raw/discounts.json'

def save_discounts(discounts, path=OUTPUT_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(discounts, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    save_discounts(DISCOUNTS)
    print(f"✅ 折扣規則已儲存至 {OUTPUT_PATH}")