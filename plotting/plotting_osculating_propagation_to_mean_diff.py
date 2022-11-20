import matplotlib.pyplot as plt
from skyfield.api import load as skyfield_load
import matplotlib
import datetime
from params import TLE_Lifetime_Analysis_Parameters
from util import convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements, eci_2_ric
import numpy as np
import astropy.constants

DATE_RANGE = ("2013-02-01", "2013-05-01")
TLE_FILE_NAME = "Jason-2.tle"

OUTPUT_FIGURE_NAMES = ["Jason2-propagation_diff_with_mean.pdf",
                       "Jason2-propagation_diff.pdf"]

params = TLE_Lifetime_Analysis_Parameters()

list_of_skyfield_earthSatellites = skyfield_load.tle_file(params.TLE_files_directory + TLE_FILE_NAME, reload=False)
df_TLE_keplerian_elements_and_diffs = convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements(list_of_skyfield_earthSatellites)
df_TLE_propagated_keplerian_elements = convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements(
        list_of_skyfield_earthSatellites, date_offset=1)

mu = 3.986004418e14
mean_SMA_vals = []
orientation = []
for sat in list_of_skyfield_earthSatellites:

    radiansPerSecond = sat.model.no_kozai / 60
    mean_SMA_vals.append(1e-3 * (
            astropy.constants.GM_earth.value ** (1/3) /
            (radiansPerSecond) ** (2/3)
    )
                         )
mean_SMA_vals = np.array(mean_SMA_vals)

propagated_diff_with_mean = [0]
propagated_diff_with_osculating = [0]
for i in range(len(df_TLE_keplerian_elements_and_diffs) - 1):
    propagated_diff_with_mean.append(df_TLE_propagated_keplerian_elements["semi-major axis"].iloc[i] - mean_SMA_vals[1 + i])
    propagated_diff_with_osculating.append(df_TLE_propagated_keplerian_elements["semi-major axis"].iloc[i] -
                                           df_TLE_keplerian_elements_and_diffs["semi-major axis"].iloc[1 + i])

df_TLE_keplerian_elements_and_diffs["propagated diff with osculating"] = propagated_diff_with_osculating
df_TLE_keplerian_elements_and_diffs["propagated diff with mean"] = propagated_diff_with_mean

series_propagated_diff_with_osculating = df_TLE_keplerian_elements_and_diffs["propagated diff with osculating"][DATE_RANGE[0]:DATE_RANGE[1]]
series_propagated_diff_with_mean = df_TLE_keplerian_elements_and_diffs["propagated diff with mean"][DATE_RANGE[0]:DATE_RANGE[1]]

font = {'size' : 18}

matplotlib.rc('font', **font)

series_to_plot = [series_propagated_diff_with_mean,
                  series_propagated_diff_with_osculating]

for i in range(len(series_to_plot)):

    plt.figure(figsize=(15, 4))
    plt.subplots_adjust(bottom=0.15)

    plt.plot(
        series_to_plot[i],
        c="b",
        marker="s",
        markersize=4,
        alpha=0.75,
    )

    plt.ylabel("Diff. in semi-major axis (km)")
    plt.xticks(rotation=20)
    plt.xlim([datetime.datetime.fromisoformat(DATE_RANGE[0]),
              datetime.datetime.fromisoformat(DATE_RANGE[1])])
    plt.tight_layout()
    #plt.show()
    plt.savefig(params.figs_output_directory + OUTPUT_FIGURE_NAMES[i])

