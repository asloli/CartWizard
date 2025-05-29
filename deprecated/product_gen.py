import json
import random
import os

PRODUCT_CATEGORIES = ['衣服', '食品', '3C', '日用品']
PRODUCT_COUNT = 100
OUTPUT_PATH = 'data/raw/products.json'

def generate_products(n=PRODUCT_COUNT):
    products = []
    for i in range(n):
        product = {
            'id': f'P{i+1:03d}',
            'name': f'商品{i+1}',
            'category': random.choice(PRODUCT_CATEGORIES),
            'price': random.randint(50, 2000)
        }
        products.append(product)
    return products

def save_products(products, path=OUTPUT_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    products = generate_products()
    save_products(products)
    print(f"✅ 商品庫已儲存至 {OUTPUT_PATH}")