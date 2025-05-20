from .discount import apply_discount
from collections import defaultdict

def solve_cart(cart_items, discount_rules):
    original_total = sum(item['price'] for item in cart_items)
    used_discounts = []
    total_discount = 0

    # 檢查 exclusive 折扣（只能獨立使用）
    exclusive_rules = [d for d in discount_rules if d.get("exclusive", False)]
    for rule in exclusive_rules:
        amt = apply_discount(cart_items, rule)
        if amt > 0:
            return {
                "original_total": original_total,
                "total_discount": amt,
                "final_price": original_total - amt,
                "used_discounts": [{**rule, "amount": amt}]
            }

    # 處理 stackable=False 的單一折扣（獨占折扣）
    exclusive_candidate = None
    for rule in discount_rules:
        if not rule.get("stackable", True):
            amt = apply_discount(cart_items, rule)
            if amt > 0 and (exclusive_candidate is None or amt > exclusive_candidate["amount"]):
                exclusive_candidate = {**rule, "amount": amt}

    if exclusive_candidate:
        return {
            "original_total": original_total,
            "total_discount": exclusive_candidate["amount"],
            "final_price": original_total - exclusive_candidate["amount"],
            "used_discounts": [exclusive_candidate]
        }

    # group 折扣（每個 group 取最划算的）
    grouped = defaultdict(list)
    others = []

    for rule in discount_rules:
        if rule.get("stackable", True) and not rule.get("exclusive", False):
            group = rule.get("group")
            if group:
                grouped[group].append(rule)
            else:
                others.append(rule)

    # 選每組 group 的最優折扣
    for group, rules in grouped.items():
        best = max(rules, key=lambda d: apply_discount(cart_items, d))
        amt = apply_discount(cart_items, best)
        if amt > 0:
            used_discounts.append({**best, "amount": amt})
            total_discount += amt

    # 其他可疊加折扣
    for rule in others:
        amt = apply_discount(cart_items, rule)
        if amt > 0:
            used_discounts.append({**rule, "amount": amt})
            total_discount += amt

    return {
        "original_total": original_total,
        "total_discount": total_discount,
        "final_price": max(original_total - total_discount, 0),
        "used_discounts": used_discounts
    }

def solve_cart_split(cart_items, discount_rules):
    used_item_ids = set()
    orders = []

    # 將折扣區分為 exclusive 折扣與一般折扣
    exclusive_discounts = [d for d in discount_rules if d.get('exclusive', False)]
    normal_discounts = [d for d in discount_rules if not d.get('exclusive', False)]

    # 先處理 exclusive 折扣，每個都各自開獨立發票
    for d in exclusive_discounts:
        usable_items = [i for i in cart_items if i['id'] not in used_item_ids]

        if d['type'] == '組合折扣':
            target_ids = set(d['items'])
            matched = [i for i in usable_items if i['id'] in target_ids]
        elif d['type'] == '單品折扣':
            matched = [i for i in usable_items if i['id'] == d['product_id']]
        elif d['type'] == '分類折扣':
            matched = [i for i in usable_items if i['category'] == d['category']]
        elif d['type'] == '品牌折扣':
            matched = [i for i in usable_items if i.get('brand') == d['brand']]
        elif d['type'] == '限時折扣':
            matched = usable_items
        else:
            matched = []

        if not matched:
            continue

        amt = apply_discount(matched, d)
        if amt > 0:
            result = solve_cart(matched, [d])
            orders.append({
                "items": matched,
                "discounts": [d],
                "result": result
            })
            used_item_ids.update(i['id'] for i in matched)

    # 剩餘商品進行主購物車處理
    remaining_items = [i for i in cart_items if i['id'] not in used_item_ids]
    if remaining_items:
        result = solve_cart(remaining_items, normal_discounts)
        orders.append({
            "items": remaining_items,
            "discounts": normal_discounts,
            "result": result
        })

    return orders