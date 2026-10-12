# Label 0: Focused subtotal computation with a descriptive interface.
def subtotal(items):
    return sum(item.price * item.quantity for item in items)


# Label 0: Guard clause keeps eligibility decision explicit.
def eligible(order):
    if not order.items:
        return False
    return order.customer.active


# Label 0: Single-purpose formatting operation.
def receipt_id(order):
    return f"ORDER-{order.id}"


# Label 0: Related calculations are delegated to named operations.
def total(order, policy):
    base = subtotal(order.items)
    tax = policy.tax_for(base)
    shipping = policy.shipping_for(order)
    return base + tax + shipping


# Label 1: Order acceptance is buried in interdependent nested conditions.
def accept(order):
    if order.customer:
        if order.customer.active:
            if order.items:
                for item in order.items:
                    if item.available:
                        if item.quantity > 0:
                            return True
    return False


# Label 1: Checkout mixes storage, payment, notification and presentation responsibilities.
def checkout(order, db, gateway, mail, logger, renderer):
    db.save(order)
    gateway.charge(order)
    mail.send(order)
    logger.record(order)
    renderer.show(order)
    return order.id


# Label 1: Several opaque positional switches obscure checkout behavior.
def price(a,b,c,d,e,f,g):
    x = a * b
    if c:
        x -= d
    if e:
        x += f
    return x * g


# Label 1: Iteration, validation and pricing are tangled in the same nested traversal.
def update(orders):
    result=[]
    for order in orders:
        if order.active:
            for item in order.items:
                if item.available:
                    if order.customer.member:
                        if item.discount:
                            result.append(item.price-item.discount)
                        else:
                            result.append(item.price)
    return result
