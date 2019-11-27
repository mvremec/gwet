# Uporabljene Python knjižnice
import os
import time

import pandas as pd
from simpledbf import Dbf5
import numpy as np
from gwet.et_ref import fao_pm

import gwet.pet

def balance(lista, precip):
    lista_copy = lista.copy()
    tmin = lista["tmin"].to_numpy()
    tmax = lista["tmax"].to_numpy()
    rhmin = lista["rhmin"].to_numpy()
    rhmax = lista["rhmax"].to_numpy()
    wind = lista["wind"].to_numpy()
    solar = lista["solar"].to_numpy()
    precip = precip.copy().to_numpy()

    h = 0.8  # Height of crop
    ze = 0.1  # Top surface soil depth
    zr = 0.4  #  Root depth
    p = 0.5  #  Check for grasslands
    # ET0 calculation
    et0 = fao_pm(lista)

    kc_ini = 1
    kcb_mid = 1
    kc_end = 1


    kcb = np.full(len(wind), 1)
    kcmin = np.full(len(wind), 0.15)

    kcmax = gwet.pet.kc_max(wind, rhmin, h, kcb)
    fc = gwet.pet.fc(kcb, kcmax, kcmin, h)

    fw = 1  # From table

    few = np.minimum(1-fc, fw)

    ro  = precip * 0.1  #  Surface runoff

    etc = kcb * et0  #  potential evapotranspiration
    for i in range(len(precip)):  # Start of the Balance
        # --------------------------------------------------------------------
        #  Surface water balance
        des_ old = des
        tew = 1000 * (sfc - 0.5 * swp) * ze
        rew = tew/2
        if des_old > rew:
            kr = (tew-des_old)/(tew-rew)
        else:
            kr = 1  # Check this

        if precip[i] > 0:  # Calculate kr
            ke = np.minimum(kr(kcmax[i]-kcb[i]), (1-fc)*kcmax)  # CHeck this
        else:
            kr = np.minimum(kr(kcmax[i]-kcb[i]), few*kcmax)  # CHeck this

        des = des_old - (precip[i] - ro[i]) - et[i]
        des = np.maximum(des, tew)
        des = np.minimum(des, 0)

        # --------------------------------------------------------------------
        #  Soil profile water balance
        taw = 1000*(sfc-swp)*zr
        raw = taw * p
        if de_old > raw:
            ks = (taw-de_old)/(taw-raw)
        else:
            ks = 1  # Check this

        eta = et0[i] * (kcb[i]*ks + ke)

        dpe = np.maximum(d_old - (precip[i]-ro[i]) - eta - de_old, 0)

        de = de_old - (precip[i]-ro[i]) + eta + dpe
        de = np.maximum(de, taw)
        de = np.minimum(de, 0)

    ke = []
    for


    return et0, kcmax, fc