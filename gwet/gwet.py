# Uporabljene Python knjižnice
import numpy as np
from gwet.et_ref import fao_pm
from gwet.infiltration import inf

import gwet.dual_crop

def wbalance(lista, precip, qfc, qwp, qs, qfc10, qwp10):

    rhmin = lista["rhmin"].to_numpy()
    wind = lista["wind"].to_numpy()
    precip = precip.copy().to_numpy()

    h = 0.8  # Height of crop
    ze = 0.1  # Top surface soil depth
    zr = 0.4  # Root depth
    p = 0.55  # Check for grasslands

    et0 = fao_pm(lista)  # ET0 calculation

    kc_ini = 1
    kcb_mid = 1
    kc_end = 1

    kcb = np.full(len(wind),1)  # Kcb-crop coefficient

    etc = kcb * et0  # Potential evapotranspiration

    # ------------------------------------------------------------------------
    # Dual crop coefficient
    kcmax = gwet.dual_crop.kc_max(wind, rhmin, h, kcb)
    kcmin = 0.15

    fc = gwet.dual_crop.fc(kcb, kcmax, kcmin, h)

    fw = 1  # From table

    few = np.minimum(1-fc, fw)

    dr_old = 1000 * (qfc + qwp)/2 * zr
    de_old = 1000 * (qfc10 + qwp10)/2 * ze
    dr_data = []
    de_data = []
    eta_data = []
    dp_data = []
    for i in range(len(precip)):  # Start of the Balance
        # --------------------------------------------------------------------
        #  Surface water balance
        tew = 1000 * (qfc10 - 0.5 * qwp10) * ze
        rew = tew * p

        inf_d = inf(precip[i], de_old, qs)

        if precip[i] > 0:
            kr = 1
        else:
            if de_old > rew:
                kr = (tew-de_old)/(tew-rew)
            else:
                kr = 1  # Check this

        ke = np.minimum(kr * (kcmax[i] - kcb[i]), few[i] * kcmax[i])  # CHeck

        evaporation = ke * et0[i]
        transpiration = 0  # From FAO - if shalllow rooted crops then change
        dpe = inf_d - de_old

        de = de_old - inf_d + evaporation / few[i] + transpiration + dpe

        de = np.maximum(de, tew)
        de = np.minimum(de, 0)
        de_old = de
        # --------------------------------------------------------------------
        #  Soil profile water balance
        taw = 1000*(qfc - qwp) * zr
        raw = taw * p
        if precip[i] > 0:
            ks = 1
        else:
            if dr_old > raw:
                ks = (taw-dr_old)/(taw-raw)
            else:
                ks = 1  # Check this

        eta = et0[i] * (kcb[i]*ks + ke)

        dp = np.maximum(dr_old - inf_d - eta - dr_old, 0)

        dr = dr_old - inf_d + eta + dp
        dr = np.maximum(dr, taw)
        dr = np.minimum(dr, 0)
        dr_old = dr

        dr_data.extend(dr)
        de_data.extend(de)
        eta_data.extend(eta)
        dp_data.extend(dp)

    return et0, kcmax, fc, etc, dr_data, de_data, eta_data, dp_data