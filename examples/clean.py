FREE_SHIPPING_LIMIT = 500

def item_total(items):
    return sum(item['price'] * item['quantity'] for item in items)

def shipping_cost(subtotal, standard_cost):
    if subtotal >= FREE_SHIPPING_LIMIT:
        return 0
    return standard_cost

def checkout(items, tax_rate, shipping):
    subtotal = item_total(items)
    return round(subtotal + subtotal * tax_rate + shipping_cost(subtotal, shipping), 2)
