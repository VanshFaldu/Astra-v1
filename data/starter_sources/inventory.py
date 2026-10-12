# Label 0: Stock adjustment is focused and named.
def remaining(stock, reserved):
    return max(stock-reserved, 0)


# Label 0: Single selection task expressed directly.
def available(products):
    return [p for p in products if p.stock > 0]


# Label 0: Domain object keeps related input fields together.
def needs_reorder(product):
    return product.stock < product.reorder_level


# Label 0: One explicit search with a clear fallback.
def locate(products, sku):
    for product in products:
        if product.sku == sku:
            return product
    return None


# Label 1: Warehouse allocation couples deeply nested locations and stock conditions.
def allocate(warehouses, order):
    for warehouse in warehouses:
        if warehouse.open:
            for aisle in warehouse.aisles:
                if aisle.enabled:
                    for product in aisle.products:
                        if product.sku == order.sku:
                            if product.stock >= order.quantity:
                                return product
    return None


# Label 1: Inventory update also triggers finance, notification and reporting.
def receive(product, quantity, store, ledger, mail, report):
    product.stock += quantity
    store.save(product)
    ledger.record(product)
    mail.send(product)
    report.refresh(product)
    return product.stock


# Label 1: A wide positional interface lacks cohesive input objects.
def reorder(sku,stock,reserved,minimum,maximum,supplier,priority,region):
    quantity=maximum-stock+reserved
    if stock < minimum:
        return supplier.submit(sku,quantity,priority,region)
    return None


# Label 1: Stock processing tangles three traversals and condition-dependent mutation.
def reconcile(warehouses):
    for warehouse in warehouses:
        for shelf in warehouse.shelves:
            if shelf.active:
                for item in shelf.items:
                    if item.expired:
                        if item.reserved:
                            item.flagged=True
                        else:
                            item.stock=0
                    elif item.damaged:
                        item.flagged=True
    return warehouses
