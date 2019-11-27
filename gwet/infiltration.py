def inf(precip, de, qs):
    if de + precip > qs:
        return qs - de
    else:
        return precip