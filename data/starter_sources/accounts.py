# Label 0: Simple normalized identifier transformation.
def normalize_email(email):
    return email.strip().casefold()


# Label 0: Explicit preconditions followed by one authorization decision.
def can_login(user):
    if user is None:
        return False
    if user.locked:
        return False
    return user.active


# Label 0: Lookup wrapper has a small cohesive purpose.
def find_user(store, email):
    key = normalize_email(email)
    return store.find(key)


# Label 0: Two meaningful domain inputs encode a single permission query.
def has_role(user, role):
    return role in user.roles


# Label 1: Authorization decisions are hidden under repeated account and role nesting.
def authorize(users, request):
    for user in users:
        if user.active:
            if not user.locked:
                for role in user.roles:
                    if role.enabled:
                        if request.action in role.actions:
                            if request.resource in role.resources:
                                return True
    return False


# Label 1: Registration changes persistence, billing, mail and audit systems in one operation.
def register(user, store, billing, mail, audit, cache):
    store.insert(user)
    billing.create(user)
    mail.welcome(user)
    audit.write(user)
    cache.invalidate(user)
    return user


# Label 1: Unexplained boolean arguments make account changes difficult to reason about.
def change(user,a,b,c,d,e,f):
    if a:
        user.active=b
    if c:
        user.locked=d
    if e:
        user.admin=f
    return user


# Label 1: Many unrelated account policies and nested fallback rules share one implementation.
def policy(user, request):
    if user.active:
        if user.admin:
            if request.internal:
                return True
            elif request.signed:
                return True
        elif user.member:
            if request.read:
                if not user.locked:
                    return True
            elif request.write:
                if user.verified:
                    if request.signed:
                        return True
    return False
