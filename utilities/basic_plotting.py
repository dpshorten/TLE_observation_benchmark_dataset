import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from skyfield.api import load as skyfield_load
import astropy.constants
import pandas as pd
from util import convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements
from params import TLE_Lifetime_Analysis_Parameters
import numpy as np
import yaml

params = TLE_Lifetime_Analysis_Parameters()

TLE_FILE_NAME = "Sentinel-3A.tle"
MANOEUVRE_FILE_NAME = "manoeuvres_Sentinel-3A.yaml"

DATE_RANGE = ("2010-02-01", "2016-04-01")


XLIMS = ("2016-01-01", "2017-01-01")

XTICK_HOUR_INTERVAL = 5000
DATE_FORMAT = '%Y-%m-%d'


list_of_skyfield_earthSatellites = skyfield_load.tle_file(params.TLE_files_directory + TLE_FILE_NAME, reload=False)
df_TLE_keplerian_elements = convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements(list_of_skyfield_earthSatellites)

manoeuvre_timestamps = yaml.safe_load(open(params.TLE_files_directory + MANOEUVRE_FILE_NAME))["manoeuvre_timestamps"]


#series_SMA = df_TLE_keplerian_elements["semi-major axis"][DATE_RANGE[0]:DATE_RANGE[1]]
series_mean_SMA = df_TLE_keplerian_elements["average mean motion"][DATE_RANGE[0]:DATE_RANGE[1]]

manoeuvre_timestamps = [timestamp for timestamp in manoeuvre_timestamps if pd.Timestamp(DATE_RANGE[0]) < timestamp <
                        pd.Timestamp(DATE_RANGE[1])]

font = {'size' : 18}

matplotlib.rc('font', **font)
fig = plt.figure(figsize=(15, 4))
plt.subplots_adjust(bottom=0.15)

# plt.title(title)
plt.plot(
#    np.arange(len(series_SMA)),
    series_mean_SMA,
    c="b",
    marker="s",
    label="Mean motion",
    markersize=4,
    alpha=0.75,
)

plt.scatter(
    manoeuvre_timestamps,
    np.mean(series_mean_SMA) * np.ones(len(manoeuvre_timestamps)),
    marker = "x",
    c = "g",
    s = 100,
    label = "Manoeuvres"
)


plt.legend(loc="lower left")
#plt.xlim([datetime.datetime.fromisoformat(XLIMS[0]),
 #         datetime.datetime.fromisoformat(XLIMS[1])])
#fig.axes[0].xaxis.set_major_locator(mdates.HourLocator(interval=XTICK_HOUR_INTERVAL))
#fig.axes[0].xaxis.set_major_formatter(mdates.DateFormatter(DATE_FORMAT))
plt.ylabel("Mean motion (rad/s)")
plt.xticks(rotation=20)
plt.tight_layout()
plt.show()
#plt.savefig(params.figs_output_directory + OUTPUT_FIGURE_NAMES[i])