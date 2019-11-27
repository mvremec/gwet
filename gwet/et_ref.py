import numpy as np
import pandas as pd


def fao_pm(lista):
    """
        Funkcija izracuna referencno evapotranspiracija po metodi Penman-Monteith.

        Vhodni podatki:
            lista: razpredelnica s stolpci:
                T_min - minimalna dnevna temperatura [°C]
                T_max - maksimalna dnevna temperatura [°C]
                vlaz_min - minimalna dnevna relativna vlaznost [-]
                vlaz_max - maksimalna dnevna relativna vlaznost [-]
                veter - povprecna dnevna hitrost vetra [m/s]
                sev - vrednost dnevnega prejetega soncno sevanje [MJ m^-2 dan^-1],


         Funkcije vrne dnevne vrednosti referencne evapotranspiracije za podano obdobje
                """
    # Naredi kopijo uporabljenih vhodnih podatkov. S tem se zavarujemo, da ne pride do sprememb v izvorni datoteki vhodnih podatkov.
    lista_copy = lista.copy()
    tmin = lista["tmin"].to_numpy()
    tmax = lista["tmax"].to_numpy()
    rhmin = lista["rhmin"].to_numpy()
    rhmax = lista["rhmax"].to_numpy()
    wind = lista["wind"].to_numpy()
    rad = lista["solar"].to_numpy()

    # Uporabljene konstante
    psi = 0.066  # Psihometrična konstanta (tabela x x) - nadmorska visina 198 0.066 [/]
    sk = 0.082  # Sonceva konstanta []
    # ------------------------------------------------
    # Izracun dolgovalovnega sevanja
    # Vrednost Steffan Boltzmanove konstante
    stef = 4.903 * 10 ** -9
    # Izračun povprečne Temperature
    T_pov = (tmin + tmin) / 2
    # Izračun krivulje zasičenega parnega tlaka (kzp)
    kzp = 4098 * (0.6108 * np.exp ((17.27 * T_pov) / (T_pov + 237.3))) / \
          (T_pov + 237.3) ** 2
    # Izracun zasicenega parnega tlaka pri maks dnevni (esmax)
    psmax = 0.6108 * np.exp (17.27 * tmax / (tmax + 237.3))
    # Izracun zasicenega parnega tlaka pri min dnevni  (pzmin)
    psmin = 0.6108 * np.exp (17.27 * tmin / (tmin + 237.3))
    # Izracun dejanskega parnega tlaka (ea)
    pa = ((rhmax * psmin / 100) + (rhmin * psmax / 100)) / 2
    # Izracun srednje vrednosti zasičenega parnega tlaka (pzs)
    ps = (psmax + psmin) / 2
    # Korekcija vetra glede na višino merjenja
    veter = wind * 4.87 / np.log (67.8 * 1 - 5.42)
    # ---------------------------------------------------------
    # Izracun neto sevanja na površini rastline (Rn)
    # Dolocitev dneva v letu
    J = pd.to_numeric (lista_copy.index.strftime ('%j'))
    # Izračun relativne inverzne razdalja (dr)
    dr = 1 + 0.33 * np.cos (2 * np.pi / 365 * J)
    # Izračun sončnega odklona SO
    so = 0.409 * np.sin (2 * np.pi / 365 * J - 1.39)
    # Izracun zemljepisne sirine pri 16.039875
    zs = np.pi / 180 * 16.039875
    # Določitev kota soncnega zahoda sz
    sz = np.arccos (-np.tan (so) * np.tan (zs))
    # Ekstrateresticnega sevanje (Ra)
    Ra = 24 * 60 / np.pi * 0.082 * dr * (
            sz * np.sin(zs) * np.sin(so) + np.cos (zs) *
            np.cos(so) * np.sin (sz))
    # Izracun radiacija jasnega neba (rso), nadmorska visina 198
    Rso = (0.75 + (2 * 10 ** -5) * 198) * Ra
    # Izracun kratkovalovnega sevanja Rs - reflekcisjki koeficient/albedo je za referenčno travnato površino enak 0.23
    Rns = (1 - 0.23) * rad
    # Izracun neto sevanja na površini rastline (Rnl)
    Rnl = np.absolute((stef * ((tmax + 273.2) ** 4 +
                               (tmin + 273.2) ** 4) / 2 *
                       (0.34 - 0.14 * (pa ** 0.5)) *
                       (1.35 * (rad / Rso) - 0.35)))

    # Izračun neto sevanja
    Rn1 = Rns - Rnl
    Rn = np.maximum (Rn1, 0.001)

    # izracun evapotranspiracije
    et0 = (0.408 * kzp * Rn +
           (psi * 900 / (T_pov + 273.2) * veter * (ps - pa))) / \
          (kzp + psi * (1 + 0.34 * veter))

    e = pd.DataFrame(data={"et0": et0}, index=lista_copy.index)
    e = e.to_numpy()
    return e
