# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 16:19:34 2019

@author: Matevz
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

meteo1 = pd.read_csv("examples/Radenci.txt",
                    delimiter = "\t",index_col = 0, parse_dates=True)
meteo2 = pd.read_csv("examples/meteo.txt",
                    delimiter = "\t",index_col = 0, parse_dates=True)

meteo2["solar"][meteo2["solar"]<0] = 0
meteosum = meteo2.resample("d").sum()
meteomax = meteo2.resample("d").max()
meteomin = meteo2.resample("d").min()
meteoav = meteo2.resample("d").mean()
meteo_solar = (meteo2["solar"] * 60 * 60).resample("d").sum()/10**6
meteo_solar.plot()

meteo = pd.DataFrame({"tmin": meteomin["T"], "tmax": meteomax["T"], 
                      "rhmin": meteomin["rh"], "rhmax": meteomax["rh"],
                      "solar": meteo_solar, "wind": meteoav["wind"]})



from gwet.gwet import wbalance
from gwet.et_ref import fao_pm

qpk = 0.266
qwp = 0.1328
qs = 0.3212
qpk10 = 0.36
qwp10 = 0.17

soil = [qpk, qwp, qs, qpk10, qwp10]

et0, kcmax, fc, etc, dr_data, de_data, eta_data, dp_data = wbalance(meteo, precip, qfc, qwp, qaverage)

  


