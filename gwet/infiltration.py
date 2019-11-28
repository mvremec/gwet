def inf(precip, de, qs, zr):
    """Calculation of infiltration.

    Parameters
    ----------
    precip: float
        Daily precipitation [mm].
    de: float
        Root zone depletion at the end of day [mm].
    qs: float
        Water content at saturation[-].
    zr: float
        Root depth [m].

    Examples:
        meteo = pd.DataFrame({"tmin":8, "tmax": 25.7, "rhmin": 34, "rhmax": 96,
                            "solar":25.7, "wind": 0.257}, index = [1])

    """
    qs_profile = 1000 * qs * zr
    if (de + precip) > qs_profile:
        return qs_profile - de
    else:
        return precip