"""Reproduce the assistant-authored educational starter model; no external data."""
import csv
import io
import json
from pathlib import Path
from analyzer import analyze, FEATURES
from ml import fit_csv, save_model

ROOT = Path(__file__).parent
# Labels are design judgments attached to source examples, not outputs from rules.
# Each entry is (label, rationale, source). Groups are authored modules, not real repositories.
CORPUS = {
 'orders': [
 (0,'Focused subtotal computation with a descriptive interface.', 'def subtotal(items):\n    return sum(item.price * item.quantity for item in items)'),
 (0,'Guard clause keeps eligibility decision explicit.', 'def eligible(order):\n    if not order.items:\n        return False\n    return order.customer.active'),
 (0,'Single-purpose formatting operation.', 'def receipt_id(order):\n    return f"ORDER-{order.id}"'),
 (0,'Related calculations are delegated to named operations.', 'def total(order, policy):\n    base = subtotal(order.items)\n    tax = policy.tax_for(base)\n    shipping = policy.shipping_for(order)\n    return base + tax + shipping'),
 (1,'Order acceptance is buried in interdependent nested conditions.', 'def accept(order):\n    if order.customer:\n        if order.customer.active:\n            if order.items:\n                for item in order.items:\n                    if item.available:\n                        if item.quantity > 0:\n                            return True\n    return False'),
 (1,'Checkout mixes storage, payment, notification and presentation responsibilities.', 'def checkout(order, db, gateway, mail, logger, renderer):\n    db.save(order)\n    gateway.charge(order)\n    mail.send(order)\n    logger.record(order)\n    renderer.show(order)\n    return order.id'),
 (1,'Several opaque positional switches obscure checkout behavior.', 'def price(a,b,c,d,e,f,g):\n    x = a * b\n    if c:\n        x -= d\n    if e:\n        x += f\n    return x * g'),
 (1,'Iteration, validation and pricing are tangled in the same nested traversal.', 'def update(orders):\n    result=[]\n    for order in orders:\n        if order.active:\n            for item in order.items:\n                if item.available:\n                    if order.customer.member:\n                        if item.discount:\n                            result.append(item.price-item.discount)\n                        else:\n                            result.append(item.price)\n    return result')],
 'accounts': [
 (0,'Simple normalized identifier transformation.', 'def normalize_email(email):\n    return email.strip().casefold()'),
 (0,'Explicit preconditions followed by one authorization decision.', 'def can_login(user):\n    if user is None:\n        return False\n    if user.locked:\n        return False\n    return user.active'),
 (0,'Lookup wrapper has a small cohesive purpose.', 'def find_user(store, email):\n    key = normalize_email(email)\n    return store.find(key)'),
 (0,'Two meaningful domain inputs encode a single permission query.', 'def has_role(user, role):\n    return role in user.roles'),
 (1,'Authorization decisions are hidden under repeated account and role nesting.', 'def authorize(users, request):\n    for user in users:\n        if user.active:\n            if not user.locked:\n                for role in user.roles:\n                    if role.enabled:\n                        if request.action in role.actions:\n                            if request.resource in role.resources:\n                                return True\n    return False'),
 (1,'Registration changes persistence, billing, mail and audit systems in one operation.', 'def register(user, store, billing, mail, audit, cache):\n    store.insert(user)\n    billing.create(user)\n    mail.welcome(user)\n    audit.write(user)\n    cache.invalidate(user)\n    return user'),
 (1,'Unexplained boolean arguments make account changes difficult to reason about.', 'def change(user,a,b,c,d,e,f):\n    if a:\n        user.active=b\n    if c:\n        user.locked=d\n    if e:\n        user.admin=f\n    return user'),
 (1,'Many unrelated account policies and nested fallback rules share one implementation.', 'def policy(user, request):\n    if user.active:\n        if user.admin:\n            if request.internal:\n                return True\n            elif request.signed:\n                return True\n        elif user.member:\n            if request.read:\n                if not user.locked:\n                    return True\n            elif request.write:\n                if user.verified:\n                    if request.signed:\n                        return True\n    return False')],
 'inventory': [
 (0,'Stock adjustment is focused and named.', 'def remaining(stock, reserved):\n    return max(stock-reserved, 0)'),
 (0,'Single selection task expressed directly.', 'def available(products):\n    return [p for p in products if p.stock > 0]'),
 (0,'Domain object keeps related input fields together.', 'def needs_reorder(product):\n    return product.stock < product.reorder_level'),
 (0,'One explicit search with a clear fallback.', 'def locate(products, sku):\n    for product in products:\n        if product.sku == sku:\n            return product\n    return None'),
 (1,'Warehouse allocation couples deeply nested locations and stock conditions.', 'def allocate(warehouses, order):\n    for warehouse in warehouses:\n        if warehouse.open:\n            for aisle in warehouse.aisles:\n                if aisle.enabled:\n                    for product in aisle.products:\n                        if product.sku == order.sku:\n                            if product.stock >= order.quantity:\n                                return product\n    return None'),
 (1,'Inventory update also triggers finance, notification and reporting.', 'def receive(product, quantity, store, ledger, mail, report):\n    product.stock += quantity\n    store.save(product)\n    ledger.record(product)\n    mail.send(product)\n    report.refresh(product)\n    return product.stock'),
 (1,'A wide positional interface lacks cohesive input objects.', 'def reorder(sku,stock,reserved,minimum,maximum,supplier,priority,region):\n    quantity=maximum-stock+reserved\n    if stock < minimum:\n        return supplier.submit(sku,quantity,priority,region)\n    return None'),
 (1,'Stock processing tangles three traversals and condition-dependent mutation.', 'def reconcile(warehouses):\n    for warehouse in warehouses:\n        for shelf in warehouse.shelves:\n            if shelf.active:\n                for item in shelf.items:\n                    if item.expired:\n                        if item.reserved:\n                            item.flagged=True\n                        else:\n                            item.stock=0\n                    elif item.damaged:\n                        item.flagged=True\n    return warehouses')],
 'telemetry': [
 (0,'A single numeric aggregation.', 'def average(values):\n    if not values:\n        return None\n    return sum(values)/len(values)'),
 (0,'A focused filter with a meaningful threshold parameter.', 'def above_limit(samples, limit):\n    return [sample for sample in samples if sample > limit]'),
 (0,'Explicit missing-value normalization.', 'def normalize(value, fallback):\n    return fallback if value is None else value'),
 (0,'Formatting delegates serialization instead of mixing responsibilities.', 'def encode_event(event, encoder):\n    return encoder.encode(event)'),
 (1,'Parsing, persistence, alerting and visual output are mixed together.', 'def process(event, parser, store, alerts, dashboard, logger):\n    data=parser.parse(event)\n    store.save(data)\n    alerts.check(data)\n    dashboard.refresh(data)\n    logger.record(data)\n    return data'),
 (1,'Alert rules require traversing several nested state combinations.', 'def alert(devices):\n    for device in devices:\n        if device.online:\n            for sensor in device.sensors:\n                if sensor.active:\n                    for reading in sensor.readings:\n                        if reading.valid:\n                            if reading.value > sensor.limit:\n                                return True\n    return False'),
 (1,'Unclear positional mode flags make an event API error-prone.', 'def transform(x,a,b,c,d,e,f,g):\n    if a:\n        x=x*b\n    if c:\n        x=x+d\n    if e:\n        x=x/f\n    return x+g'),
 (1,'Many measurement branches mix validation, fallback and unit conversions.', 'def reading(sensor):\n    if sensor.active:\n        if sensor.valid:\n            if sensor.unit == "c":\n                if sensor.offset:\n                    return sensor.value+sensor.offset\n                return sensor.value\n            elif sensor.unit == "f":\n                if sensor.calibrated:\n                    return sensor.convert()\n            elif sensor.unit == "k":\n                if sensor.reference:\n                    return sensor.compare()\n        elif sensor.fallback:\n            return sensor.fallback.value\n    return None')],
 'scheduling': [
 (0,'Focused interval comparison.', 'def overlaps(a,b):\n    return a.start < b.end and b.start < a.end'),
 (0,'Single sorting operation with a descriptive key.', 'def chronological(events):\n    return sorted(events,key=lambda event:event.start)'),
 (0,'A clear guard separates invalid input from the result.', 'def duration(event):\n    if event.end < event.start:\n        raise ValueError("Invalid interval")\n    return event.end-event.start'),
 (0,'One query delegates storage concerns.', 'def upcoming(store, now):\n    return store.events_after(now)'),
 (1,'Scheduling combines reservation, payment, reminders and presentation.', 'def book(event, calendar, billing, email, sms, ui):\n    calendar.reserve(event)\n    billing.charge(event)\n    email.confirm(event)\n    sms.remind(event)\n    ui.refresh(event)\n    return event'),
 (1,'Availability decision is obscured by nested staff, room and slot dependencies.', 'def slot(staff, rooms):\n    for person in staff:\n        if person.available:\n            for room in rooms:\n                if room.open:\n                    for time in room.slots:\n                        if time.free:\n                            if time in person.slots:\n                                return time\n    return None'),
 (1,'Separate positional scheduling options are difficult to match with intent.', 'def create(title,start,end,zone,owner,room,repeat,notify):\n    event={"title":title,"start":start,"end":end,"zone":zone}\n    event["owner"]=owner\n    event["room"]=room\n    event["repeat"]=repeat\n    event["notify"]=notify\n    return event'),
 (1,'Rescheduling combines nested validation with several conditional side effects.', 'def reschedule(event, policy):\n    if event.active:\n        if policy.allowed:\n            if event.owner.available:\n                if event.room.open:\n                    if event.start in policy.slots:\n                        event.start=policy.next_slot()\n                        if event.paid:\n                            policy.refund(event)\n                        if event.notify:\n                            policy.notify(event)\n                        return event\n    return None')]
}

def main():
    folder=ROOT/'data'/'starter_sources'; folder.mkdir(parents=True,exist_ok=True)
    rows=[]
    for group,examples in CORPUS.items():
        source='\n\n'.join(f'# Label {label}: {rationale}\n{code}\n' for label,rationale,code in examples)
        (folder/f'{group}.py').write_text(source,encoding='utf-8')
        functions=analyze(source)['functions']
        for (label,rationale,_),metrics in zip(examples,functions):
            rows.append({'repository':f'authored-module:{group}','function':metrics['name'],'line':metrics['line'],**{k:metrics[k] for k in FEATURES},'label':label,'review_rationale':rationale,'source_file':f'data/starter_sources/{group}.py','label_author':'AI assistant','dataset_kind':'assistant-authored educational example'})
    output=io.StringIO(); writer=csv.DictWriter(output,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    content=output.getvalue();(ROOT/'data'/'starter_training.csv').write_text(content,encoding='utf-8')
    model=fit_csv(content)
    model['dataset_kind']='assistant-authored educational examples; not independently human-reviewed or a public benchmark'
    model['provenance']={'samples':len(rows),'groups':len(CORPUS),'group_kind':'authored domain modules, not real repositories','label_author':'AI assistant','source':'data/starter_sources','csv':'data/starter_training.csv','limitations':'Same author and related structural patterns across domains. Holdout scores are demonstration results, not real-world performance evidence.'}
    save_model(model)
    (ROOT/'data'/'starter_evaluation.json').write_text(json.dumps(model['evaluation'],indent=2),encoding='utf-8')
    print(json.dumps(model['evaluation'],indent=2))
if __name__=='__main__': main()
