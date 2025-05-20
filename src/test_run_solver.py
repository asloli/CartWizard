import json
import os
from collections import defaultdict
from copy import deepcopy

from core.solver import solve_cart_split, solve_cart
from core.discount import apply_discount

CART_PATH = "data/carts/cart_extreme_005.json"
DISCOUNT_PATH = "data/raw/discounts.json"

def solve_cart(cart_items, discount_rules):
    # 原始 solve_cart（可保留或略為更新）
    original_total = sum(item['price'] for item in cart_items)
    used_discounts = []
    total_discount = 0

    # 按類型分組
    type_map = defaultdict(list)
    for d in discount_rules:
        type_map[d["type"]].append(d)

    # 滿額：只取最划算的
    if "滿額折扣" in type_map:
        best = max(type_map["滿額折扣"], key=lambda d: apply_discount(cart_items, d))
        amt = apply_discount(cart_items, best)
        if amt > 0:
            used_discounts.append({**best, "amount": amt})
            total_discount += amt

    # 滿件：只取最划算的
    if "滿件折扣" in type_map:
        best = max(type_map["滿件折扣"], key=lambda d: apply_discount(cart_items, d))
        amt = apply_discount(cart_items, best)
        if amt > 0:
            used_discounts.append({**best, "amount": amt})
            total_discount += amt

    # 其他折扣：全試（分類折扣、單品折扣）
    for d_type in ["分類折扣", "單品折扣"]:
        for d in type_map[d_type]:
            amt = apply_discount(cart_items, d)
            if amt > 0:
                used_discounts.append({**d, "amount": amt})
                total_discount += amt

    final_price = max(original_total - total_discount, 0)
    return {
        "original_total": original_total,
        "total_discount": total_discount,
        "final_price": final_price,
        "used_discounts": used_discounts
    }


def solve_cart_split(cart_items, discount_rules):
    exclusive_discounts = [d for d in discount_rules if d.get('exclusive', False)]
    normal_discounts = [d for d in discount_rules if not d.get('exclusive', False)]

    used_item_ids = set()
    orders = []

    for d in exclusive_discounts:
        related_ids = set()
        # 判斷這個折扣要哪些商品
        if d['type'] == '組合折扣':
            related_ids = set(d['items'])
        elif d['type'] == '單品折扣':
            related_ids = {d['product_id']}
        elif d['type'] == '分類折扣':
            related_ids = set(i['id'] for i in cart_items if i['category'] == d['category'])
        else:
            continue

        if related_ids.issubset(i['id'] for i in cart_items if i['id'] not in used_item_ids):
            order_items = [i for i in cart_items if i['id'] in related_ids]
            result = solve_cart(order_items, [d])
            if result["total_discount"] > 0:
                orders.append({
                    "items": order_items,
                    "discounts": [d],
                    "result": result
                })
                used_item_ids.update(related_ids)

    # 剩下的商品
    remaining_items = [i for i in cart_items if i['id'] not in used_item_ids]
    if remaining_items:
        result = solve_cart(remaining_items, normal_discounts)
        orders.append({
            "items": remaining_items,
            "discounts": normal_discounts,
            "result": result
        })

    return orders

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def print_split_result(orders):
    all_items = [item for order in orders for item in order["items"]]
    all_ids = sorted(set(item["id"] for item in all_items))

    print("📦 原始購物車：", ", ".join(all_ids))
    print("📑 共需分開發票數量：", len(orders))
    print("============================================")

    total = 0
    for idx, order in enumerate(orders, start=1):
        result = order["result"]
        item_ids = [i['id'] for i in order["items"]]
        discount_list = result["used_discounts"]

        print(f"\n🧾 發票 {chr(64 + idx)}")
        print("📦 商品：", ", ".join(item_ids))
        if discount_list:
            print("💡 折扣：")
            for d in discount_list:
                print(f"  - [{d['id']}] {d['type']}：-{d['amount']} 元")
        else:
            print("💡 折扣：無")
        print(f"💰 小計：{result['final_price']} 元")
        print("-" * 40)

        total += result["final_price"]

    print("\n🧮 💰 最終總金額（多張合計）：", total, "元")

    print("🔍 exclusive 折扣觸發情況：")
    for d in discount_rules:
        if d.get("exclusive", False):
            amt = apply_discount(cart["items"], d)
            print(f"  - {d['id']} 可折 {amt}")

if __name__ == "__main__":
    if not os.path.exists(CART_PATH):
        print(f"❌ 找不到購物車資料：{CART_PATH}")
        exit(1)
    if not os.path.exists(DISCOUNT_PATH):
        print(f"❌ 找不到折扣規則：{DISCOUNT_PATH}")
        exit(1)

    cart = load_json(CART_PATH)
    discount_rules = load_json(DISCOUNT_PATH)

    split_orders = solve_cart_split(cart["items"], discount_rules)
    print_split_result(split_orders)

