import datetime
import matplotlib
import matplotlib.pyplot as plt
from util import convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements
from skyfield.api import load as skyfield_load
import astropy.constants
import pandas as pd
import numpy as np
from params import TLE_Lifetime_Analysis_Parameters

PLOT_INDEX = 0

TLE_FILE_NAMES = [
    "CryoSat-2.tle",
    "Fengyun-2D.tle",
    "Fengyun-2E.tle",
    "Fengyun-2F.tle",
    "Fengyun-2H.tle",
    "Fengyun-4A.tle",
    "Haiyang-2A.tle",
    "Jason-1.tle",
    "Jason-2.tle",
    "Jason-3.tle",
    "SARAL.tle",
    "Sentinel-3A.tle",
    "Sentinel-3B.tle",
    "Sentinel-6A.tle",
    "TOPEX.tle",
]

NAMES_LIST = [
    "Cryosat2",
    "FY2D",
    "FY2E",
    "FY2F",
    "FY2H",
    "FY4A",
    "HY2A",
    "Jason1",
    "Jason2",
    "Jason3",
    "S3a",
    "S3b",
    "S6a",
    "SARAL",
    "TOPEX",
]

Y_AXIS_LABELS = [
    "diff in semi-major axes (km)",
    "diff in eccentricity",
    "diff in inclination (radians)",
]

OUTPUT_FIGURE_NAMES = [
    "multi_sats-SMA_diffs_mean_and_osculating.pdf",
    "multi_sats-ecc_diffs_mean_and_osculating.pdf",
    "multi_sats-inc_diffs_mean_and_osculating.pdf",
]

params = TLE_Lifetime_Analysis_Parameters()



diffs = [[], [], []]

for j in range(len(TLE_FILE_NAMES)):

    list_of_skyfield_earthSatellites = skyfield_load.tle_file(params.TLE_files_directory + TLE_FILE_NAMES[j], reload=False)
    df_TLE_keplerian_elements = convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements(list_of_skyfield_earthSatellites)

    mean_SMA_vals = []
    mean_eccentricity = []
    mean_inclination = []
    orientation = []
    for sat in list_of_skyfield_earthSatellites:

        radians_per_second = sat.model.no_kozai / 60
        mean_SMA_vals.append(1e-3 * (astropy.constants.GM_earth.value ** (1 / 3) / (radians_per_second) ** (2 / 3)))
        mean_eccentricity.append(sat.model.ecco)
        mean_inclination.append((sat.model.inclo / np.pi) * 180)

    df_TLE_keplerian_elements["mean SMA values"] = mean_SMA_vals
    df_TLE_keplerian_elements["mean eccentricity"] = mean_eccentricity
    df_TLE_keplerian_elements["mean inclination"] = mean_inclination

    diffs[0].append(df_TLE_keplerian_elements["semi-major axis"] - df_TLE_keplerian_elements["mean SMA values"])
    diffs[1].append(df_TLE_keplerian_elements["eccentricity"] - df_TLE_keplerian_elements["mean eccentricity"])
    diffs[2].append(df_TLE_keplerian_elements["inclination"] - df_TLE_keplerian_elements["mean inclination"])

font = {'size'   : 14}
matplotlib.rc('font', **font)

for i in range(len(diffs)):

    fig = plt.figure(figsize=(15, 4))
    plt.subplots_adjust(bottom=0.15)

    # Make the scatter strips
    x = np.zeros(0)
    y = np.zeros(0)
    for j in range(len(diffs[i])):
        x = np.concatenate((x, j * np.ones(len(diffs[i][j])) + np.random.normal(loc=0, scale=7.5e-2, size=len(diffs[i][j]))))
        y = np.concatenate((y, diffs[i][j]))
    plt.scatter(x, y, s=3, alpha=0.3)

    plt.xticks(rotation=30, fontsize=12)
    fig.axes[0].set_xticks(list(range(0, len(NAMES_LIST))))
    fig.axes[0].set_xticklabels(NAMES_LIST)
    fig.axes[0].tick_params(axis='x', which='major', labelsize=18)
    fig.axes[0].tick_params(axis='y', which='major', labelsize=16)

    plt.ylabel(Y_AXIS_LABELS[i], labelpad=None)

    plt.tight_layout()
    #plt.show()
    plt.savefig(params.figs_output_directory + OUTPUT_FIGURE_NAMES[i])
    plt.clf()