import numpy as np

def kc_max(wind, rhmin, h, kcb):
    kcmax = np.maximum(
        (1.2 + (0.4 * (wind - 2) - 0.004 * rhmin - 45) * (h / 3) ** 0.3),
        kcb + 0.05)
    kcmax=np.maximum(kcmax,1.05)
    kcmax = np.minimum(kcmax, 1.3)
    return kcmax

def fc(kcb, kcmax, kcmin, h):
    fc = ((kcb-kcmin)/(kcmax-kcmin))**(1+0.5*h)
    fc = np.minimum(fc, 1)
    fc = np.maximum(fc, 0)
    return fc