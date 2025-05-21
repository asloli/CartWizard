# 完整版 apply_discount 支援新版折扣格式

def apply_discount(cart_items, discount):
    if discount["type"] == "滿額折扣":
        if "category" not in discount:
            return 0
        total = sum(item["price"] for item in cart_items if item["category"] == discount["category"])
        return discount["amount"] if total >= discount["threshold"] else 0

    elif discount["type"] == "滿件折扣":
        if "items" not in discount or "count" not in discount:
            return 0
        match_count = sum(1 for item in cart_items if item["id"] in discount["items"])
        return discount["amount"] if match_count >= discount["count"] else 0

    elif discount["type"] == "組合折扣":
        if "items" not in discount:
            return 0
        ids_in_cart = set(item["id"] for item in cart_items)
        return discount["amount"] if all(req in ids_in_cart for req in discount["items"]) else 0

    elif discount["type"] == "獨立折扣":
        if "items" not in discount:
            return 0
        for item in cart_items:
            if item["id"] in discount["items"]:
                return discount["amount"]
        return 0

    return 0
