import numpy as np

def kc_max(wind, rhmin, h, kcb):
    """Calculation of the maximum value of Kc following rain or irrigation.

    Parameters
    ----------
    wind: np.array of floats
        Time series of wind data [m/s].
    rhmin: np.array of floats
        Mean  value  for  daily  minimum  relative  humidity [-].
    h: np.array of floats
        Mean  plant  height [m].
    kcb: np.array of floats
        Daily basal crop coefficient [-].

    """
    kcmax = np.maximum(
        (1.2 + (0.4 * (wind - 2) - 0.004 * rhmin - 45) * (h / 3) ** 0.3),
        kcb + 0.05)
    kcmax=np.maximum(kcmax, 1.05)
    kcmax = np.minimum(kcmax, 1.3)
    return kcmax

def fc(kcb, kcmax, kcmin, h):
    """Calculation of the effective fraction of soil surface covered by
    vegetation.

    Parameters
    ----------
    kcb: np.array of floats
        Daily basal crop coefficient [-].
    kcmax: np.array of floats
        Maximum value of Kc following rain or irrigation [-].
    kcmin: np.array of floats
        Minimum Kc for dry bare soil with no ground cover [-].
    h: np.array of floats
        Mean  plant  height [m].

    """
    fc = ((kcb - kcmin)/(kcmax - kcmin))**(1+0.5 * h)
    fc = np.minimum(fc, 1)
    fc = np.maximum(fc, 0)
    return fc

def calc_kr(precip, de_old, rew, tew):
    """Calculation of the dimensionless  evaporation  reduction  coefficient
    dependent  on  the  soil  water  depletion.

    Parameters
    ----------
    precip: float
        Daily precipitation [mm].
    de_old: lfloat
        Cumulative  depth  of  evaporation  following  complete  wetting  from
        the  exposed and wetted fraction of the topsoil at the end of day i-1
        [mm].
    rew: float
        Cumulative depth of evaporation (depletion) at the end of stage 1 [mm].
    tew: float
        maximum  cumulative  depth  of  evaporation  (depletion)  from  the
        soil surface layer [mm].

    """
    if precip > 0:
        return 1
    else:
        if rew < de_old < tew:
            return (tew-de_old)/(tew-rew)
        elif de_old <= rew:
            return 1
        else:
            return 0