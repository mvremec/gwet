import numpy as np
import pandas as pd


def fao_pm(meteo):
    """FAO paper 56. Reference evapotranspiration calculation (ET0).

    Parameters
    ----------
    meteo: pandas.DataFrame
        Pandas DataFrame containing the parameters needed for the reference
        evapotranspiration calculation (ET0).

    Examples:
        meteo = pd.DataFrame({"tmin":8, "tmax": 25.7, "rhmin": 34, "rhmax": 96,
                            "solar":25.7, "wind": 0.257}, index = [1])

    """

    # Make a copy of input meteo parameters
    meteo_copy = meteo.copy()
    tmin = meteo["tmin"].to_numpy()
    tmax = meteo["tmax"].to_numpy()
    rhmin = meteo["rhmin"].to_numpy()
    rhmax = meteo["rhmax"].to_numpy()
    wind = meteo["wind"].to_numpy()
    rad = meteo["solar"].to_numpy()

    # Used constants
    psi = 0.066  # Psychrometric con. at 200m elev. [kPa °C-1](p. 32 - FAO-56)
    sc = 0.082  # solar constant [MJ m-2 min-1(p. 46 - FAO-56)
    # ------------------------------------------------
    stef = 4.903 * 10 ** -9  # Stefan-Boltzmann constant [MJ K-4 m-2 day-1]

    tmean = (tmin + tmin) / 2
    # Slope of saturation vapour pressure curve (∆)[kPa °C-1]
    kzp = 4098 * (0.6108 * np.exp((17.27 * tmean) / (tmean + 237.3))) / \
        (tmean + 237.3) ** 2
    # Saturation vapour pressure at daily maximum temperature [kPa]
    psmax = 0.6108 * np.exp (17.27 * tmax / (tmax + 237.3))
    # Saturation vapour pressure at daily minimum temperature [kPa]
    psmin = 0.6108 * np.exp(17.27 * tmin / (tmin + 237.3))
    # Actual vapour pressure (ea)[kPa]
    pa = ((rhmax * psmin / 100) + (rhmin * psmax / 100)) / 2
    # Mean saturation vapour pressure (es)[kPa]
    ps = (psmax + psmin) / 2
    # Correction of the wind based on the height of measurement
    wind = wind * 4.87 / np.log(67.8 * 1 - 5.42)
    # ---------------------------------------------------------
    # Day of the year
    j = pd.to_numeric(meteo_copy.index.strftime('%j'))
    # Inverse relative distance Earth-Sun
    dr = 1 + 0.33 * np.cos(2 * np.pi / 365 * j)
    # Solar declination [rad]
    so = 0.409 * np.sin(2 * np.pi / 365 * j - 1.39)
    # Latitude [rad]
    zs = np.pi / 180 * 16.039875
    # Sunset hour angle [rad]
    sz = np.arccos(-np.tan(so) * np.tan(zs))
    # Extraterrestrial radiation for hourly or shorter periods (Ra)
    ra = 24 * 60 / np.pi * sc * dr * (
            sz * np.sin(zs) * np.sin(so) + np.cos(zs) *
            np.cos(so) * np.sin(sz))
    # Clear-sky solar radiation (Rso) at 200m elevation [MJ m-2 day-1]
    rso = (0.75 + (2 * 10 ** -5) * 198) * ra
    # Net solar or net shortwave radiation (Rns)[MJ m-2 day-1]
    rns = (1 - 0.23) * rad
    # Net longwave radiation (Rnl)[MJ m-2 day-1]
    rnl = np.absolute((stef * ((tmax + 273.2) ** 4 +
                               (tmin + 273.2) ** 4) / 2 *
                       (0.34 - 0.14 * (pa ** 0.5)) *
                       (1.35 * (rad / rso) - 0.35)))

    # Net radiation (Rn)
    rn = rns - rnl
    rn = np.maximum(rn, 0.001)

    # Reference evapotranspiration calculation (ET0)
    et0 = (0.408 * kzp * rn +
           (psi * 900 / (tmean + 273.2) * wind * (ps - pa))) / \
          (kzp + psi * (1 + 0.34 * wind))

    e = pd.DataFrame(data={"et0": et0}, index=meteo_copy.index)
    e = e.to_numpy()
    return e
