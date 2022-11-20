import pandas as pd
from skyfield.api import load_file, Loader, load
import random
import datetime
import numpy as np
import skyfield.elementslib as skyfieldEle
import matplotlib.pyplot as plt
import matplotlib
from params import TLE_Lifetime_Analysis_Parameters

DORIS_DATA_DIR = "../DORIS_beacon_positions/"
TLE_DATA_DIR = "../processed_files/"

DORIS_FILE_NAMES = [
    "DORIS-beacons_Sentinel-3A.csv",
    "DORIS-beacons_Haiyang-2A.csv",
]

TLE_FILE_NAMES = [
    "Sentinel-3A.tle",
    "Haiyang-2A.tle",
]

SATELLITE_NAMES = [
    "Sentinel-3A",
    "Haiyang-2A",
]

OUTPUT_FIG_FILE_NAMES = [
    "propagation_error_S3A.png",
    "propagation_error_HY2A.png",
]

NUM_SAMPLES = 100
DAYS_TO_SAMPLE = [0, 0.5, 1, 1.5, 2, 2.5, 5, 10, 20]
buffer_from_end = DAYS_TO_SAMPLE * 24 * 60

ts = load.timescale()

diffs_for_sats = np.zeros((len(DORIS_FILE_NAMES), NUM_SAMPLES, len(DAYS_TO_SAMPLE)))
params = TLE_Lifetime_Analysis_Parameters()

for i in range(len(DORIS_FILE_NAMES)):

    print(DORIS_FILE_NAMES[i])

    df_DORIS = pd.read_csv(DORIS_DATA_DIR + DORIS_FILE_NAMES[i], header=0,
                           parse_dates=["timestamp"])
    df_DORIS = df_DORIS.drop_duplicates(subset = ["timestamp"])
    df_DORIS = df_DORIS.set_index("timestamp")

    first_DORIS_date = df_DORIS.index.values[0]
    last_DORIS_date = df_DORIS.index.values[-1]

    loader = Loader(TLE_DATA_DIR)
    tle_skyfield_satellites = loader.tle_file(TLE_FILE_NAMES[i])

    num_valid_samples = 0
    while num_valid_samples < NUM_SAMPLES:
        is_valid_sample = True
        diffs = np.zeros((len(DAYS_TO_SAMPLE),))
        random_epoch_index = random.randint(30, len(tle_skyfield_satellites) - 30)

        skyfield_sat = tle_skyfield_satellites[random_epoch_index]
        datetime_sat_epoch = skyfield_sat.epoch.utc_datetime()
        datetime_sat_epoch = datetime_sat_epoch.replace(tzinfo=None)
        nearest_in_DORIS = df_DORIS.index.get_indexer([datetime_sat_epoch], method='nearest')
        datetime_nearest_in_DORIS = df_DORIS.index[nearest_in_DORIS].to_pydatetime()[0]
        #print(datetime_sat_epoch, datetime_nearest_in_DORIS)
        if (datetime_sat_epoch - datetime_nearest_in_DORIS) > datetime.timedelta(minutes=2):
            print(datetime_sat_epoch, datetime_nearest_in_DORIS, random_epoch_index)
            continue
        #print(df_DORIS.loc[datetime_nearest_in_DORIS]["semi-major axis"])

        for j in range(len(DAYS_TO_SAMPLE)):
            datetime_evaluation = datetime_nearest_in_DORIS + datetime.timedelta(days = DAYS_TO_SAMPLE[j])
            skyfield_satellite_at_current = skyfield_sat.at(ts.utc(datetime_evaluation.year,
                                                                   datetime_evaluation.month,
                                                                   datetime_evaluation.day,
                                                                   datetime_evaluation.hour,
                                                                   datetime_evaluation.minute,))
            skyFieldKeplerianElements = skyfieldEle.osculating_elements_of(skyfield_satellite_at_current)

            try:
                # This will cause an exception if the timestamp we are looking for is not in the DORIS data.
                diff = abs(skyFieldKeplerianElements.semi_major_axis.km - df_DORIS.loc[datetime_evaluation]["semi-major axis"])
            except:
                is_valid_sample = False
                break

            diffs[j] = diff

        if is_valid_sample:
            diffs_for_sats[i, num_valid_samples, :] = diffs
            num_valid_samples += 1

font = {'size' : 20}
matplotlib.rc('font', **font)

for i in range(len(OUTPUT_FIG_FILE_NAMES)):
    fig = plt.figure(figsize=(10, 7))
    plt.boxplot(diffs_for_sats[i, :, :], whis=3, showfliers=False)
    fig.axes[0].set_xticks(list(range(1, len(DAYS_TO_SAMPLE) + 1)))
    fig.axes[0].set_xticklabels(DAYS_TO_SAMPLE)
    plt.ylabel("Abs. diff. in semi-major axis (km)")
    plt.xlabel("days of propagation")
    plt.savefig(params.figs_output_directory + OUTPUT_FIG_FILE_NAMES[i])
    plt.clf()