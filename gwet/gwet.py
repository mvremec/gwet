# Uporabljene Python knjižnice
import pandas as pd
import numpy as np
from gwet.et_ref import fao_pm
from gwet.infiltration import inf

import gwet.dual_crop


def wbalance(meteo,precip,soil,landuse):
    """FAO water balance approach following the dual crop coefficient approach
    with the usage of the water stress coefficient.

    Parameters
    ----------
    meteo: pandas.DataFrame
        Pandas DataFrame containing the parameters needed for the reference
        evapotranspiration calculation (ET0).
    precip: np.array of floats
        Time series of daily precipitation [mm].
    soil: np.array of floats
        Array of soil properties.
    landuse: pandas.DataFrame
        Pandas Dataframe containing time series data of the basal crop
        coefficent(kcb), depth(zr) and crop height(h).

    """
    rhmin = meteo["rhmin"].to_numpy()
    wind = meteo["wind"].to_numpy()
    precip = precip.copy().to_numpy()

    ze = 0.1  # Top surface soil depth
    p = 0.55  # Check for grasslands

    h = landuse["h"]
    zr = landuse["zr"]
    kcb = landuse["kcb"]

    qpk = soil[0]
    qwp = soil[1]
    qs = soil[2]
    qpk10 = soil[3]
    qwp10 = soil[4]

    et0 = fao_pm(meteo)  # ET0 calculation

    if kcb is None:
        kcb = np.full(len(wind), 1.1)  # Kcb-crop coefficient

    # ------------------------------------------------------------------------
    # Dual crop coefficient
    kcmax = gwet.dual_crop.kc_max(wind, rhmin, h, kcb)
    kcmin = 0.15

    fc = gwet.dual_crop.fc(kcb, kcmax, kcmin, h)

    fw = 1  # From table

    few = np.minimum(1-fc, fw)

    dr_old = 1000 * (qpk - qwp) * zr[0] * 0.7
    de_old = 1000 * (qpk10 - qwp10) * ze * 0.7

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

        inf_d = inf(precip[i], de_old, qs, zr[i])

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
        taw = 1000*(qpk - qwp) * zr[i]
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

        dr = min(dr_old - inf_d + eta + dp, 1000 * qwp * zr[i])

        dr_data.append(float(dr))
        de_data.append(float(de))
        eta_data.append(float(eta))
        dp_data.append(float(dp))
        ks_data.append(float(ks))
        inf_data.append(float(inf_d))
        dr_old_data.append(float(dr_old))
        ke_data.append(float(ke))
        dr_old = dr

    return eta_data, dp_data, ks_data, inf_data, dr_old_data, ke_data

def urban_balance(meteo,precip,soil,landuse):
    """FAO water balance approach following the dual crop coefficient approach
    with the usage of the water stress coefficient for urban areas.

    Parameters
    ----------
    meteo: pandas.DataFrame
        Pandas DataFrame containing the parameters needed for the reference
        evapotranspiration calculation (ET0).
    precip: np.array of floats
        Time series of daily precipitation [mm].
    soil: np.array of floats
        Array of soil properties.
    landuse: pandas.DataFrame
        Pandas Dataframe containing time series data of the basal crop
        coefficent(kcb), depth(zr) and crop height(h).

    """
    rhmin = meteo["rhmin"].to_numpy()
    wind = meteo["wind"].to_numpy()
    precip = precip.copy().to_numpy()

    ze = 0.1  # Top surface soil depth
    p = 0.55  # Check for grasslands

    h = landuse["h"]
    zr = landuse["zr"]
    kcb = landuse["kcb"]

    qpk = soil[0]
    qwp = soil[1]
    qs = soil[2]
    qpk10 = soil[3]
    qwp10 = soil[4]

    et0 = fao_pm(meteo)  # ET0 calculation

    if kcb is None:
        kcb = np.full(len(wind), 1.1)  # Kcb-crop coefficient

    # ------------------------------------------------------------------------
    # Dual crop coefficient
    kcmax = gwet.dual_crop.kc_max(wind, rhmin, h, kcb)
    kcmin = 0.15

    fc = gwet.dual_crop.fc(kcb, kcmax, kcmin, h)

    fw = 1  # From table

    few = np.minimum(1-fc, fw)

    dr_old = 1000 * (qpk - qwp) * zr[0] * 0.7
    de_old = 1000 * (qpk10 - qwp10) * ze * 0.7

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

        p_urb = precip[i] * 0.8
        dpd = precip[i] * 0.1
        inf_d = inf(p_urb, de_old, qs, zr[i])

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
        taw = 1000*(qpk - qwp) * zr[i]
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

        dr = min(dr_old - inf_d + eta + dp, 1000 * qwp * zr[i])

        dr_data.append(float(dr))
        de_data.append(float(de))
        eta_data.append(float(eta))
        dp_data.append(float(dp))
        ks_data.append(float(ks))
        inf_data.append(float(inf_d))
        dr_old_data.append(float(dr_old))
        ke_data.append(float(ke))
        dr_old = dr

    return eta_data, dp_data, ks_data, inf_data, dr_old_data, ke_data


def hydrotop(hydrotops, precip, meteo, land_use, soil_prop):
    """Method to calculate the actual evapotranspiration and groundwater
    recharge for each row of the input pandas.DataFrame hydrotops.

    Parameters
    ----------
    hydrotops: pandas.DataFrame
        Pandas DataFrame of the shapefile database.
    precip: np.array of floats
        Time series of daily precipitation [mm].
    meteo: pandas.DataFrame
        Pandas DataFrame containing the meteorological parameters.
    land_use: Dictionary of pandas.DataFrames
        Disctionary containing pandas.DataFrames with time series of the basal
        crop coefficent(kcb), depth(zr) and crop height(h) for each landuse ID.
    soil_prop: pandas.DataFrame
        Pandas Dataframe containing data of the soil hydraulic properties for
        each soil ID.

    """
    actual_et = {}
    recharge = {}
    for index, row in hydrotops.iterrows():
        landuse_data = land_use[str(row[0])] 
        soil_data = soil_prop.loc[row[1]].to_numpy()
        precip_data = precip[str(row[2])]
        if row[0] <= 8:
            eta_data, dp_data, ks_data, inf_data, dr_old_data, ke_data = \
                wbalance(meteo, precip_data, soil_data, landuse_data)
            recharge[index] = dp_data
            actual_et[index] = eta_data
        elif row[0] == 9:
            eta_data, dp_data, ks_data, inf_data, dr_old_data, ke_data = \
                urban_balance(meteo, precip_data, soil_data, landuse_data)
            recharge[index] = dp_data
            actual_et[index] = eta_data
        elif row[0] == 11:
            recharge[index] = [0.001] * len(precip_data)
            actual_et[index] = [0.001] * len(precip_data)
    recharge_df = pd.DataFrame(data=recharge, index=precip_data.index)
    actual_et_df = pd.DataFrame(data=actual_et, index=precip_data.index)
    return recharge_df, actual_et_df
