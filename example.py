# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 16:19:34 2019

@author: Matevz
"""
import numpy as np
import pandas as pd
from gwet.gwet import balance
meteo = pd.read_csv("examples/Radenci.txt",
                    delimiter = "\t",index_col = 0, parse_dates=True)
#et0, kcmax, fc = balance(meteo)


wind = meteo["wind"].copy().to_numpy()

for i in range(len(wind)):
    print(wind[i])