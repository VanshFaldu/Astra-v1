# Label 0: A single numeric aggregation.
def average(values):
    if not values:
        return None
    return sum(values)/len(values)


# Label 0: A focused filter with a meaningful threshold parameter.
def above_limit(samples, limit):
    return [sample for sample in samples if sample > limit]


# Label 0: Explicit missing-value normalization.
def normalize(value, fallback):
    return fallback if value is None else value


# Label 0: Formatting delegates serialization instead of mixing responsibilities.
def encode_event(event, encoder):
    return encoder.encode(event)


# Label 1: Parsing, persistence, alerting and visual output are mixed together.
def process(event, parser, store, alerts, dashboard, logger):
    data=parser.parse(event)
    store.save(data)
    alerts.check(data)
    dashboard.refresh(data)
    logger.record(data)
    return data


# Label 1: Alert rules require traversing several nested state combinations.
def alert(devices):
    for device in devices:
        if device.online:
            for sensor in device.sensors:
                if sensor.active:
                    for reading in sensor.readings:
                        if reading.valid:
                            if reading.value > sensor.limit:
                                return True
    return False


# Label 1: Unclear positional mode flags make an event API error-prone.
def transform(x,a,b,c,d,e,f,g):
    if a:
        x=x*b
    if c:
        x=x+d
    if e:
        x=x/f
    return x+g


# Label 1: Many measurement branches mix validation, fallback and unit conversions.
def reading(sensor):
    if sensor.active:
        if sensor.valid:
            if sensor.unit == "c":
                if sensor.offset:
                    return sensor.value+sensor.offset
                return sensor.value
            elif sensor.unit == "f":
                if sensor.calibrated:
                    return sensor.convert()
            elif sensor.unit == "k":
                if sensor.reference:
                    return sensor.compare()
        elif sensor.fallback:
            return sensor.fallback.value
    return None
