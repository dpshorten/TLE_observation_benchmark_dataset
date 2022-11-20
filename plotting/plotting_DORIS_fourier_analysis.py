import matplotlib.pyplot as plt
import matplotlib.dates
import yaml
import pickle as pkl
from skyfield.api import load as skyfield_load
import numpy as np
import pandas as pd

from params import TLE_Lifetime_Analysis_Parameters
from util import convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements

START_YEAR = [
    2019,
    2019,
    2011,
    2015,
    2018,
    2019,
    2019,
    2021,
    2017,
]

NAMES = [
    "CryoSat-2",
    "Haiyang-2A",
    "Jason-1",
    "Jason-2",
    "Jason-3",
    "Sentinel-3A",
    "Sentinel-3B",
    "Sentinel-6A",
    "SARAL",
]

ORBIT_PERIODS = [
    99.16,
    104.45,
    112.56,
    112.0,
    112.42,
    100.99,
    100.93,
    112.4,
    100.54,
]

ORBITAL_ELEMENTS = [
    "semi-major axis",
    "eccentricity",
    "inclination",
]

ORBITAL_ELEMENTS_FOR_OUTPUT_FIG_NAMES = [
    "sma",
    "eccentricity",
    "inclination",
]

VMINS = [
    5,
    -10,
    -10
]
DAYS = 10

params = TLE_Lifetime_Analysis_Parameters()

def get_power_spectrum_for_orbital_element(element):
    power_spectrums = []
    freqs = []
    for i in range(len(NAMES)):

        f = open(params.manoeuver_files_directory + "manoeuvres_" + NAMES[i] + ".yaml", "r")
        series_manoeuvre_time_stamps = pd.Series(yaml.safe_load(f)["manoeuvre_timestamps"])
        list_of_skyfield_earthSatellites = skyfield_load.tle_file(params.TLE_files_directory + NAMES[i] + ".tle")
        df_TLE_Keplerian_elements = convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements(list_of_skyfield_earthSatellites)

        df_Sp3_orbit = pd.read_csv(params.DORIS_files_directory + "DORIS-beacons_" + NAMES[i] + ".csv",
                                   index_col="timestamp", parse_dates=["timestamp"])
        df_Sp3_orbit = df_Sp3_orbit[~df_Sp3_orbit.index.duplicated()]

        start_obs_date = pd.Timestamp(year=START_YEAR[i], month=1, day=1)
        endStamp = (start_obs_date + pd.Timedelta(days=DAYS))

        df_inspection_interval_Sp3 = df_Sp3_orbit.loc[start_obs_date:endStamp, :]
        df_inspection_interval_Sp3 = df_inspection_interval_Sp3.reset_index()
        df_inspection_interval_Sp3 = df_inspection_interval_Sp3.set_index("timestamp")

        fft_of_element = np.fft.fft(df_inspection_interval_Sp3[element].values - np.mean(df_inspection_interval_Sp3[element].values))
        fft_freq = np.fft.fftfreq(len(df_inspection_interval_Sp3[element]))
        cutoff = int(round(len(fft_freq) / 2))
        power_spectrums.append(np.log(np.abs(fft_of_element[:(cutoff - 1)]) ** 2))
        power_spectrums.append(np.log(np.abs(fft_of_element[:(cutoff - 1)]) ** 2))
        freqs.append(fft_freq[:cutoff] * ORBIT_PERIODS[i])
        freqs.append(fft_freq[:cutoff] * ORBIT_PERIODS[i])
    return power_spectrums, freqs

def plot_power_spectrum_of_elemnt(power_spectrums, frequencies, element_index):

    font = {'size': 16}
    matplotlib.rc('font', **font)

    fig = plt.figure(figsize=(15, 4))
    y_mesh_points = []
    y_mesh_points.append(0)
    for i in range(1, len(NAMES)):
        y_mesh_points.append(i)
        y_mesh_points.append(i)
    y_mesh_points.append(len(NAMES))

    plt.pcolormesh(frequencies, y_mesh_points, power_spectrums[0:(-1)], cmap=matplotlib.colormaps["viridis"],
                   vmin = VMINS[element_index], shading='flat')
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('log amplitude', rotation=270, labelpad=15)
    plt.xlim([0, 10])
    plt.xlabel("Frequency (cycles per orbit)")
    fig.axes[0].set_yticks(np.arange(0, len(NAMES)) + 0.5)
    fig.axes[0].set_yticklabels(NAMES)
    plt.tight_layout()
    #plt.show()
    plt.savefig(params.figs_output_directory + "fourier_" + ORBITAL_ELEMENTS_FOR_OUTPUT_FIG_NAMES[element_index] + ".png")
    plt.clf()


for i in range(len(ORBITAL_ELEMENTS)):
    power_spectrums, frequencies = get_power_spectrum_for_orbital_element(ORBITAL_ELEMENTS[i])
    plot_power_spectrum_of_elemnt(power_spectrums, frequencies, i)