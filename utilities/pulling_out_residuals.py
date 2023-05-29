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

TLE_FILE_NAME = "Haiyang-2A.tle"
MANOEUVRE_FILE_NAME = "manoeuvres_Haiyang-2A.yaml"

DATE_RANGE = ("2019-02-01", "2019-04-01")

XTICK_HOUR_INTERVAL = 5000
DATE_FORMAT = '%Y-%m-%d'

MEAN_ELEMENT_NAMES = [
    "average eccentricity",
    "average inclination",
    "average right ascension of ascending node",
    "average argument of perigee",
    "average mean anomaly",
    "average mean motion",
]

list_of_skyfield_earthSatellites = skyfield_load.tle_file(params.TLE_files_directory + TLE_FILE_NAME, reload=False)
df_TLE_keplerian_elements = convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements(list_of_skyfield_earthSatellites)
df_propagated_TLE_keplerian_elements = convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements(
    list_of_skyfield_earthSatellites,
    date_offset=1
)

manoeuvre_timestamps = yaml.safe_load(open(params.TLE_files_directory + MANOEUVRE_FILE_NAME))["manoeuvre_timestamps"]

mean_SMA_vals = []
orientation = []

diffs = pd.DataFrame()
diffs_dummy = pd.DataFrame()
for element_name in MEAN_ELEMENT_NAMES:
    diffs[element_name] = (
            df_propagated_TLE_keplerian_elements[element_name]
            - df_TLE_keplerian_elements[element_name].iloc[1:]
    )
    diffs_dummy[element_name] = df_TLE_keplerian_elements[element_name].iloc[1:]
    diffs_dummy[element_name] = (
        df_TLE_keplerian_elements[element_name].iloc[:-1].values
        - df_TLE_keplerian_elements[element_name].iloc[1:].values
    )

font = {'size' : 18}

matplotlib.rc('font', **font)
fig = plt.figure(figsize=(15, 4))
plt.subplots_adjust(bottom=0.15)

index = 5
# plt.title(title)
plt.plot(
#    np.arange(len(series_SMA)),
    diffs[MEAN_ELEMENT_NAMES[index]],
    c="b",
    marker="s",
    label="Mean motion",
    markersize=4,
    alpha=0.75,
)

# plt.plot(
# #    np.arange(len(series_SMA)),
#     diffs_dummy[MEAN_ELEMENT_NAMES[index]],
#     c="r",
#     marker="s",
#     label="Mean motion",
#     markersize=4,
#     alpha=0.75,
# )

plt.scatter(
    manoeuvre_timestamps,
    np.mean(diffs[MEAN_ELEMENT_NAMES[index]]) * np.ones(len(manoeuvre_timestamps)),
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

diffs.to_csv("diffs_Haiyang-2A.csv")
#plt.savefig(params.figs_output_directory + OUTPUT_FIGURE_NAMES[i])