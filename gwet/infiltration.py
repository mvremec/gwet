def inf(precip, de, qs, zr):
    qs_profile = 1000 * qs *zr
    if de + precip > qs_profile:
        return qs_profile - de
    else:
        return precip