# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 16:19:34 2019

@author: Matevz
"""
import geopandas
import numpy as np
import pandas as pd

from gwet.gwet import hydrotop

hydrotops = pd.DataFrame(data = (["precip1", 1, 406],["precip2", 2, 408]),
                        columns = ["precip_id", "luse_id", "soil_id"])
meteo1 = pd.read_csv("examples/meteo.csv", index_col = "date",
                     parse_dates=True)
precip1 = pd.read_csv("examples/precip1.csv", index_col="date", sep=";", 
                      parse_dates=True)
precip2 = pd.read_csv("examples/precip2.csv", index_col="date", sep=";", 
                      parse_dates=True)
precip = {"precip1": precip1, "precip2": precip2}

landuse1 = pd.DataFrame({"h": np.full(len(precip1), 0.6),
                         "zr": np.full(len(precip1), 0.8),
                         "kcb": np.full(len(precip1.index), 1.1)})
landuse2 = landuse1 * 1.1
landuse3 = landuse1 * 0.9

landuse = {"1": landuse1, "2": landuse2, "3": landuse3}

columns = ["qpk", "qwp", "qs", "qpk10", "qwp10"]
soils = pd.DataFrame(data = ([0.27, 0.13, 0.32, 0.36, 0.17],
                    [0.30, 0.15, 0.36, 0.38, 0.17],
                    [0.20, 0.10, 0.25, 0.35, 0.17],
                    [0.29, 0.14, 0.37, 0.37, 0.17],
                    [0.44, 0.24, 0.50, 0.39, 0.13],
                    [0.19, 0.07, 0.26, 0.32, 0.11]),
                    columns = columns, 
                    index = [401, 402, 404, 406, 408, 1356])

dp, eta = hydrotop(hydrotops, precip, meteo1, landuse, soils)





meteo1 = pd.DataFrame({"tmin":8, "tmax": 25.7, "rhmin": 34, "rhmax": 96,
                       "solar":25.7, "wind": 0.257}, index = [1])
#meteo2 = pd.read_csv("examples/meteo.txt",
#                    delimiter = "\t",index_col = 0, parse_dates=True)

#meteo2["solar"][meteo2["solar"]<0] = 0
#meteosum = meteo2.resample("d").sum()
#meteomax = meteo2.resample("d").max()
#meteomin = meteo2.resample("d").min()
#meteoav = meteo2.resample("d").mean()
#meteo_solar = (meteo2["solar"] * 60 * 60).resample("d").sum()/10**6
#meteo_solar.plot()
#
#meteo = pd.DataFrame({"tmin": meteomin["T"], "tmax": meteomax["T"], 
#                      "rhmin": meteomin["rh"], "rhmax": meteomax["rh"],
#                      "solar": meteo_solar, "wind": meteoav["wind"]})