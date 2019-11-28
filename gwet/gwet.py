# Uporabljene Python knjižnice
import numpy as np
from gwet.et_ref import fao_pm
from gwet.infiltration import inf

import gwet.dual_crop

def wbalance(lista, precip, soil, kcb = None):

    rhmin = lista["rhmin"].to_numpy()
    wind = lista["wind"].to_numpy()
    precip = precip.copy().to_numpy()

    h = 0.8  # Height of crop
    ze = 0.1  # Top surface soil depth
    zr = 0.8  # Root depth
    p = 0.55  # Check for grasslands

    qpk = soil[0]
    qwp = soil[1]
    qs = soil[2]
    qpk10 = soil[3]
    qwp10 = soil[4]


    et0 = fao_pm(lista)  # ET0 calculation

    kc_ini = 1
    kcb_mid = 1
    kc_end = 1
    if kcb is None:
        kcb = np.full(len(wind), 1.1)  # Kcb-crop coefficient

    # ------------------------------------------------------------------------
    # Dual crop coefficient
    kcmax = gwet.dual_crop.kc_max(wind, rhmin, h, kcb)
    kcmin = 0.15

    fc = gwet.dual_crop.fc(kcb, kcmax, kcmin, h)

    fw = 1  # From table

    few = np.minimum(1-fc, fw)

    dr_old = 1000 * (qpk - qwp) * zr * 0.7
    de_old = 1000 * (qpk10 - qwp10) * ze * 0.7
    print(dr_old)
    dr_data = []
    de_data = []
    eta_data = []
    dp_data = []
    ks_data = []
    inf_data = []
    dr_old_data = []
    ke_data = []
    for i in range(len(precip)):  # Start of the Balance
        # --------------------------------------------------------------------
        #  Surface water balance
        tew = 1000 * (qpk10 - 0.5 * qwp10) * ze
        rew = tew * p

        inf_d = inf(precip[i], de_old, qs, zr)

        kr = gwet.dual_crop.calc_kr (precip[i], de_old, rew, tew)

        ke = np.minimum(kr * (kcmax[i] - kcb[i]), few[i] * kcmax[i])  # CHeck

        evaporation = ke * et0[i]
        transpiration = 0  # From FAO - if shallow rooted crops then change
        dpe = inf_d - de_old

        etcof = evaporation / few[i]

        de = de_old - inf_d + etcof + transpiration + dpe

        de = np.maximum(de, tew)
        de = np.minimum(de, 0)
        de_old = de
        # --------------------------------------------------------------------
        #  Soil profile water balance
        taw = 1000*(qpk - qwp) * zr
        raw = taw * p
        if precip[i] > 0:
            ks = 1
        else:
            if dr_old >= taw:
                ks = 0
            elif raw < dr_old < taw:
                ks = (taw-dr_old)/(taw-raw)
            else:
                ks = 1  # Check this

        eta = et0[i] * (kcb[i]*ks + ke)

        dp = np.maximum(inf_d - eta - dr_old, 0)

        dr = min(dr_old - inf_d + eta + dp, 1000 * qwp * zr)

        dr_data.append(float(dr))
        de_data.append(float(de))
        eta_data.append(float(eta))
        dp_data.append(float(dp))
        ks_data.append(float(ks))
        inf_data.append(float(inf_d))
        dr_old_data.append(float(dr_old))
        ke_data.append(float(ke))
        dr_old = dr

    return dr_data, de_data, eta_data, dp_data, ks_data, \
           inf_data, dr_old_data, ke_data

def urban_balance(lista, precip, soil):

    rhmin = lista["rhmin"].to_numpy()
    wind = lista["wind"].to_numpy()
    precip = precip.copy().to_numpy()

    h = 0.8  # Height of crop
    ze = 0.1  # Top surface soil depth
    zr = 0.8  # Root depth
    p = 0.55  # Check for grasslands

    qpk = soil[0]
    qwp = soil[1]
    qs = soil[2]
    qpk10 = soil[3]
    qwp10 = soil[4]


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

    dr_old = 1000 * (qpk - qwp*1.1) * zr
    de_old = 1000 * (qpk10 - qwp10*1.1) * ze
    print(dr_old)
    dr_data = []
    de_data = []
    eta_data = []
    dp_data = []
    ks_data = []
    inf_data = []
    dr_old_data = []
    ke_data = []
    for i in range(len(precip)):  # Start of the Balance
        # --------------------------------------------------------------------
        #  Surface water balance
        tew = 1000 * (qpk10 - 0.5 * qwp10) * ze
        rew = tew * p

        inf_urb = precip[i] * 0.8
        dpd = precip[i] * 0.1
        inf_d = inf(inf_urb, de_old, qs, zr)

        kr = gwet.dual_crop.calc_kr(precip[i], de_old, rew, tew)

        ke = np.minimum(kr * (kcmax[i] - kcb[i]), few[i] * kcmax[i])  # CHeck

        evaporation = ke * et0[i]
        transpiration = 0  # From FAO - if shallow rooted crops then change
        dpe = inf_d - de_old

        etcof = evaporation / few[i]

        de = de_old - inf_d + etcof + transpiration + dpe

        de = np.maximum(de, tew)
        de = np.minimum(de, 0)
        de_old = de
        # --------------------------------------------------------------------
        #  Soil profile water balance
        taw = 1000*(qpk - qwp) * zr
        raw = taw * p
        if precip[i] > 0:
            ks = 1
        else:
            if dr_old > raw:
                ks = (taw-dr_old)/(taw-raw)
            else:
                ks = 1  # Check this

        eta = et0[i] * (kcb[i]*ks + ke)

        dp = np.maximum(inf_d - eta - dr_old + dpd, 0)

        dr = min(dr_old - inf_d + eta + dp, 1000 * qwp * zr)

        dr_data.append(float(dr))
        de_data.append(float(de))
        eta_data.append(float(eta))
        dp_data.append(float(dp))
        ks_data.append(float(ks))
        inf_data.append(float(inf_d))
        dr_old_data.append(float(dr_old))
        ke_data.append(float(ke))
        dr_old = dr

    return dr_data, de_data, eta_data, dp_data, ks_data, \
           inf_data, dr_old_data, ke_data