import matplotlib.pyplot as plt
import yaml
from skyfield.api import load as skyfield_load
import matplotlib
import datetime
import numpy as np
import pandas as pd
from params import TLE_Lifetime_Analysis_Parameters
from util import convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements
from util import eci_2_ric


PROPAGATION_DISTANCES = [1, 5]

DATE_RANGE = ("2013-01-01 00:00:00", "2015-01-01 00:00:00")
MANOEUVRES_FILE_NAME = "manoeuvres_Jason-2.yaml"
TLE_FILE_NAME = "Jason-2.tle"

DIFF_NAMES = ["mean_to_mean_SMA_diff",
              "mean_to_mean_ecc_diff",
              "mean_to_mean_inc_diff",
              "osculating_to_osculating_r_diff",
              "osculating_to_osculating_i_diff",
              "osculating_to_osculating_c_diff",
              "osculating_to_osculating_a_diff",
              "osculating_to_osculating_e_diff",
              "osculating_to_osculating_i_diff",
              ]

Y_LABELS = [
    "Difference in semi-major axes (km)",
    "Difference in eccentricity",
    "Difference in inclination (degrees)",
    "Radial position difference (km)",
    "In-track position difference (km)",
    "Cross-track position difference (km)",
    "Difference in semi-major axes (km)",
    "Difference in eccentricity",
    "Difference in inclination (degrees)",
]

Y_LIMS = [
    [
        (-0.017, 0.016),
        (-4e-4, 4e-4),
        (-3e-3, 5e-3),
        (),
        (),
        (),
        (-0.017, 0.016),
        (-4e-4, 4e-4),
        (-3e-3, 5e-3),
    ],
    [
        (-0.025, 0.025),
        (-4e-4, 4e-4),
        (-3e-3, 5e-3),
        (),
        (),
        (),
        (-0.025, 0.025),
        (-4e-4, 4e-4),
        (-3e-3, 5e-3),
    ]
]

params = TLE_Lifetime_Analysis_Parameters()
f = open(params.manoeuver_files_directory + MANOEUVRES_FILE_NAME, "r")
series_manoeuvre_time_stamps = pd.Series(yaml.safe_load(f)["manoeuvre_timestamps"])

def calc_residuals_for_propagation_distance(propagation_distance):
    list_of_skyfield_earth_satellites = skyfield_load.tle_file(params.TLE_files_directory + TLE_FILE_NAME, reload=False)
    df_TLE_keplerian_elements_and_diffs = convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements(list_of_skyfield_earth_satellites)
    df_TLE_propagated_keplerian_elements = convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements(
        list_of_skyfield_earth_satellites, date_offset=propagation_distance)
    mean_x_vals = np.zeros((len(list_of_skyfield_earth_satellites), 3))
    mean_RIC_vals = np.zeros((len(list_of_skyfield_earth_satellites), 3))
    mean_keplerian_elements = np.zeros((len(list_of_skyfield_earth_satellites), 3))
    for i in range(len(list_of_skyfield_earth_satellites)):
        sat = list_of_skyfield_earth_satellites[i]
        mean_keplerian_elements[i, 0] = sat.model.radiusearthkm * sat.model.a
        mean_keplerian_elements[i, 1] = sat.model.em
        mean_keplerian_elements[i, 2] = sat.model.im
        sat.at(sat.epoch)
        mean_x_vals[i, :] = sat._position_and_velocity_TEME_km(sat.epoch)[0]
        mean_RIC_vals[i, :] = \
        eci_2_ric(sat._position_and_velocity_TEME_km(sat.epoch)[0], sat._position_and_velocity_TEME_km(sat.epoch)[1])[0]

    mean_keplerian_elements_prop = np.zeros((len(list_of_skyfield_earth_satellites), 3))
    # reload the satellites to undo the .at() call above
    list_of_skyfield_earth_satellites = skyfield_load.tle_file(params.TLE_files_directory + TLE_FILE_NAME, reload=False)
    for i in range(len(list_of_skyfield_earth_satellites) - propagation_distance):
        sat = list_of_skyfield_earth_satellites[i]
        sat.at(list_of_skyfield_earth_satellites[i + propagation_distance].epoch)
        mean_keplerian_elements_prop[i + propagation_distance, 0] = sat.model.radiusearthkm * sat.model.am
        mean_keplerian_elements_prop[i + propagation_distance, 1] = sat.model.em
        mean_keplerian_elements_prop[i + propagation_distance, 2] = sat.model.im

    osculating_to_osculating_RIC_diff = np.zeros((len(list_of_skyfield_earth_satellites), 3))
    osculating_to_osculating_kep_diff = np.zeros((len(list_of_skyfield_earth_satellites), 3))

    mean_to_mean_keplerian_diff = np.zeros((len(list_of_skyfield_earth_satellites), 3))
    mean_to_mean_keplerian_diff[propagation_distance:, :] = mean_keplerian_elements_prop[propagation_distance:, :] - mean_keplerian_elements[propagation_distance:, :]

    for i in range(len(df_TLE_keplerian_elements_and_diffs) - propagation_distance):
        osculating_to_osculating_RIC_diff[i + propagation_distance, 0] = df_TLE_propagated_keplerian_elements["U"].iloc[i] - \
                                                                         df_TLE_keplerian_elements_and_diffs["U"][i + propagation_distance]
        osculating_to_osculating_RIC_diff[i + propagation_distance, 1] = df_TLE_propagated_keplerian_elements["V"].iloc[i] - \
                                                                         df_TLE_keplerian_elements_and_diffs["V"][i + propagation_distance]
        osculating_to_osculating_RIC_diff[i + propagation_distance, 2] = df_TLE_propagated_keplerian_elements["W"].iloc[i] - \
                                                                         df_TLE_keplerian_elements_and_diffs["W"][i + propagation_distance]
        osculating_to_osculating_kep_diff[i + propagation_distance, 0] = df_TLE_propagated_keplerian_elements["semi-major axis"].iloc[i] - \
                                                                         df_TLE_keplerian_elements_and_diffs["semi-major axis"][i + propagation_distance]
        osculating_to_osculating_kep_diff[i + propagation_distance, 1] = df_TLE_propagated_keplerian_elements["eccentricity"].iloc[i] - \
                                                                         df_TLE_keplerian_elements_and_diffs["eccentricity"][i + propagation_distance]
        osculating_to_osculating_kep_diff[i + propagation_distance, 2] = df_TLE_propagated_keplerian_elements["inclination"].iloc[i] - \
                                                                         df_TLE_keplerian_elements_and_diffs["inclination"][i + propagation_distance]

    df_TLE_keplerian_elements_and_diffs[DIFF_NAMES[0]] = mean_to_mean_keplerian_diff[:, 0]
    df_TLE_keplerian_elements_and_diffs[DIFF_NAMES[1]] = mean_to_mean_keplerian_diff[:, 1]
    df_TLE_keplerian_elements_and_diffs[DIFF_NAMES[2]] = mean_to_mean_keplerian_diff[:, 2]
    df_TLE_keplerian_elements_and_diffs[DIFF_NAMES[3]] = osculating_to_osculating_RIC_diff[:, 0]
    df_TLE_keplerian_elements_and_diffs[DIFF_NAMES[4]] = osculating_to_osculating_RIC_diff[:, 1]
    df_TLE_keplerian_elements_and_diffs[DIFF_NAMES[5]] = osculating_to_osculating_RIC_diff[:, 2]
    df_TLE_keplerian_elements_and_diffs[DIFF_NAMES[6]] = osculating_to_osculating_kep_diff[:, 0]
    df_TLE_keplerian_elements_and_diffs[DIFF_NAMES[7]] = osculating_to_osculating_kep_diff[:, 1]
    df_TLE_keplerian_elements_and_diffs[DIFF_NAMES[8]] = osculating_to_osculating_kep_diff[:, 2]

    return df_TLE_keplerian_elements_and_diffs

def plot_residuals(df_TLE_keplerian_elements, series_manoeuvre_time_stamps, propagation_distance, y_lims):

    font = {'size': 20}
    matplotlib.rc('font', **font)

    for j in range(len(DIFF_NAMES)):

        plt.clf()
        plt.figure(figsize=(15, 6))
        plt.subplots_adjust(bottom=0.15)

        plotted_series = df_TLE_keplerian_elements[DIFF_NAMES[j]]

        plt.plot(
            plotted_series.loc[DATE_RANGE[0]:DATE_RANGE[1]],
            c="b",
            marker=".",
            markersize=3,
            alpha=0.75,
        )

        series_manoeuvre_time_stamps = series_manoeuvre_time_stamps[(series_manoeuvre_time_stamps > DATE_RANGE[0]) &
                                                              (series_manoeuvre_time_stamps < DATE_RANGE[1])]
        # set the y vals at which to plot the manoeuvre timestamps
        np_vals_at_which_to_plot_manoeuvres = np.zeros(series_manoeuvre_time_stamps.shape[0])
        for i in range(len(series_manoeuvre_time_stamps)):
            this_timestamp = series_manoeuvre_time_stamps.iloc[i]
            index_of_closest_SMA_timestamp = np.searchsorted(df_TLE_keplerian_elements.index, this_timestamp, side="left") - 1
            np_vals_at_which_to_plot_manoeuvres[i] = plotted_series.iloc[index_of_closest_SMA_timestamp]
        plt.scatter(series_manoeuvre_time_stamps, np_vals_at_which_to_plot_manoeuvres, marker='x', s=150, c='r', label="manoeuvre",
                    linewidths=2)



        if len(y_lims[j]) > 0:
            plt.ylim(y_lims[j])
        plt.ylabel(Y_LABELS[j])
        plt.xticks(rotation=20)
        ax = plt.gca()
        ax.tick_params(axis='x', which='major', labelsize=26)
        #ax.tick_params(axis='y', which='major', labelsize=23)
        plt.xlim([datetime.datetime.fromisoformat(DATE_RANGE[0]),
                  datetime.datetime.fromisoformat(DATE_RANGE[1])])
        plt.legend()
        plt.tight_layout()
        plt.savefig(params.figs_output_directory + DIFF_NAMES[j] + "_offset" + str(propagation_distance) + ".png")
        #plt.show()

for i in range(len(PROPAGATION_DISTANCES)):
    df_TLE_keplerian_elements_and_diffs = calc_residuals_for_propagation_distance(PROPAGATION_DISTANCES[i])
    plot_residuals(df_TLE_keplerian_elements_and_diffs, series_manoeuvre_time_stamps, PROPAGATION_DISTANCES[i], Y_LIMS[i])