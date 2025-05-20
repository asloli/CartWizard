def apply_discount(cart_items, discount):
    """
    根據購物車內容與折扣規則，回傳折扣金額。
    cart_items: list of dict, 每個 dict 包含 id, price, category
    discount: dict, 折扣規則
    return: int, 折扣金額（若不符合，則為 0）
    """
    d_type = discount['type']

    if d_type == '滿額折扣':
        total = sum(item['price'] for item in cart_items)
        if total >= discount['threshold']:
            return discount['discount']
    
    elif d_type == '滿件折扣':
        count = sum(1 for item in cart_items if item['category'] == discount['category'])
        if count >= discount['count']:
            return discount['discount']
    
    elif d_type == '分類折扣':
        discount_total = 0
        for item in cart_items:
            if item['category'] == discount['category']:
                discount_total += item['price'] * (1 - discount['percent'])
        return int(discount_total)
    
    elif d_type == '單品折扣':
        discount_total = 0
        for item in cart_items:
            if item['id'] == discount['product_id']:
                discount_total += item['price'] * (1 - discount['percent'])
        return int(discount_total)

    elif d_type == '組合折扣':
        required_items = set(discount['items'])
        cart_ids = set(item['id'] for item in cart_items)
        if required_items.issubset(cart_ids):
            total_price = sum(item['price'] for item in cart_items if item['id'] in required_items)
            if 'percent' in discount:
                return int(total_price * (1 - discount['percent']))
            elif 'discount' in discount:
                return discount['discount']
    
    return 0