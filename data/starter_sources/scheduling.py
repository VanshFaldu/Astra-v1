# Label 0: Focused interval comparison.
def overlaps(a,b):
    return a.start < b.end and b.start < a.end


# Label 0: Single sorting operation with a descriptive key.
def chronological(events):
    return sorted(events,key=lambda event:event.start)


# Label 0: A clear guard separates invalid input from the result.
def duration(event):
    if event.end < event.start:
        raise ValueError("Invalid interval")
    return event.end-event.start


# Label 0: One query delegates storage concerns.
def upcoming(store, now):
    return store.events_after(now)


# Label 1: Scheduling combines reservation, payment, reminders and presentation.
def book(event, calendar, billing, email, sms, ui):
    calendar.reserve(event)
    billing.charge(event)
    email.confirm(event)
    sms.remind(event)
    ui.refresh(event)
    return event


# Label 1: Availability decision is obscured by nested staff, room and slot dependencies.
def slot(staff, rooms):
    for person in staff:
        if person.available:
            for room in rooms:
                if room.open:
                    for time in room.slots:
                        if time.free:
                            if time in person.slots:
                                return time
    return None


# Label 1: Separate positional scheduling options are difficult to match with intent.
def create(title,start,end,zone,owner,room,repeat,notify):
    event={"title":title,"start":start,"end":end,"zone":zone}
    event["owner"]=owner
    event["room"]=room
    event["repeat"]=repeat
    event["notify"]=notify
    return event


# Label 1: Rescheduling combines nested validation with several conditional side effects.
def reschedule(event, policy):
    if event.active:
        if policy.allowed:
            if event.owner.available:
                if event.room.open:
                    if event.start in policy.slots:
                        event.start=policy.next_slot()
                        if event.paid:
                            policy.refund(event)
                        if event.notify:
                            policy.notify(event)
                        return event
    return None
