import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from skyfield.api import load as skyfield_load
import astropy.constants
import pandas as pd
from util import convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements
from params import TLE_Lifetime_Analysis_Parameters

params = TLE_Lifetime_Analysis_Parameters()

TLE_FILE_NAME = "Jason-2.tle"
DORIS_FILE_NAME = "DORIS-beacons_Jason-2.csv"
DATE_RANGE_SHADE = ("2013-02-25 12:00:00", "2013-02-27 00:00:00")

NUM_PLOT_TYPES=2
# For the below parameters, the first one is for the zoomed out plot without the DORIS data, the second one is for the
# zoomed in one with this data.
DATE_RANGES = [
    ("2013-02-01", "2013-05-01"),
    ("2013-02-24 00:00:00", "2013-02-28 00:00:00"),
]
XLIMS = [
    ("2013-02-01", "2013-05-01"),
    ("2013-02-25 12:00:00", "2013-02-27 00:00:00"),
]
PLOT_DORIS = [False, True]
XTICK_HOUR_INTERVALS = [240, 12]
DATE_FORMATS = ['%Y-%m-%d', '%Y-%m-%d %H']
OUTPUT_FIGURE_NAMES = ["Jason2-mean_and_osculating.pdf",
                       "Jason2-mean_and_osculating_and_SP3.pdf"]

list_of_skyfield_earthSatellites = skyfield_load.tle_file(params.TLE_files_directory + TLE_FILE_NAME, reload=False)
df_TLE_keplerian_elements = convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements(list_of_skyfield_earthSatellites)
df_DORIS_orbit = pd.read_csv(params.DORIS_files_directory + DORIS_FILE_NAME, index_col="timestamp", parse_dates=["timestamp"])

mean_SMA_vals = []
orientation = []
for sat in list_of_skyfield_earthSatellites:

    radians_per_second = sat.model.no_kozai / 60
    mean_SMA_vals.append(1e-3 * (
            astropy.constants.GM_earth.value ** (1/3) /
            (radians_per_second) ** (2 / 3)
    )
                         )

df_TLE_keplerian_elements["mean SMA values"] = mean_SMA_vals

for i in range(NUM_PLOT_TYPES):
    series_SMA = df_TLE_keplerian_elements["semi-major axis"][DATE_RANGES[i][0]:DATE_RANGES[i][1]]
    series_mean_SMA = df_TLE_keplerian_elements["mean SMA values"][DATE_RANGES[i][0]:DATE_RANGES[i][1]]
    series_DORIS = df_DORIS_orbit["semi-major axis"][DATE_RANGES[i][0]:DATE_RANGES[i][1]]

    font = {'size' : 18}

    matplotlib.rc('font', **font)
    fig = plt.figure(figsize=(15, 4))
    plt.subplots_adjust(bottom=0.15)

    # plt.title(title)
    plt.plot(
        series_SMA,
        c="b",
        marker="^",
        label="Oscullating element (TLE and SGP4)",
        markersize=5,
        alpha=0.75,
    )
    plt.plot(
        series_mean_SMA,
        c="g",
        marker="s",
        label="Mean element",
        markersize=4,
        alpha=0.75,
    )

    if PLOT_DORIS[i]:
        plt.plot(
            series_DORIS,
            c="r",
            marker=".",
            label="Oscullating element (DORIS beacons)",
            markersize=4,
            alpha=0.75,
        )
    else:
        plt.fill_between(series_SMA.index.values, min(series_SMA), max(series_SMA),
                         where=(series_SMA.index.values < pd.Timestamp(DATE_RANGE_SHADE[1])) &
                               (series_SMA.index.values > pd.Timestamp(DATE_RANGE_SHADE[0])),
                         alpha=0.5,
                         color='r')

    plt.legend(loc="lower left")
    plt.xlim([datetime.datetime.fromisoformat(XLIMS[i][0]),
              datetime.datetime.fromisoformat(XLIMS[i][1])])
    fig.axes[0].xaxis.set_major_locator(mdates.HourLocator(interval=XTICK_HOUR_INTERVALS[i]))
    fig.axes[0].xaxis.set_major_formatter(mdates.DateFormatter(DATE_FORMATS[i]))
    plt.ylabel("Semi-major axis (km)")
    plt.xticks(rotation=20)
    plt.tight_layout()
    #plt.show()
    plt.savefig(params.figs_output_directory + OUTPUT_FIGURE_NAMES[i])