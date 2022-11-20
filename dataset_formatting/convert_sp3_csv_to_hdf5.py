import pandas as pd
import datetime
import h5py

RAW_DATA_DIR = "../DORIS_beacon_positions/"
OUTPUT_DATA_DIR = "../processed_files/"
MAX_NUM_COLS = 100

output_file_names = [
    "DORIS_beacons_Sentinel-3A.h5",
    "DORIS_beacons_Sentinel-3B.h5",
    "DORIS_beacons_Sentinel-6A.h5",
    "DORIS_beacons_Jason-1.h5",
    "DORIS_beacons_Jason-2.h5",
    "DORIS_beacons_Jason-3.h5",
    "DORIS_beacons_SARAL.h5",
    "DORIS_beacons_CryoSat-2.h5",
    "DORIS_beacons_Haiyang-2A.h5",
]

input_file_names = [
    "s3a.csv",
    "s3b.csv",
    "s6a.csv",
    "ja1.csv",
    "ja2.csv",
    "ja3.csv",
    "saral.csv",
    "DORIS-beacons_CryoSat2.csv",
    "h2a.csv",
]

satellite_names = [
    "Sentinel-3A",
    "Sentinel-3B",
    "Sentinel-6A",
    "Jason-1",
    "Jason-2",
    "Jason-3",
    "SARAL",
    "CryoSat-2",
    "Haiyang-2A",
]

keys = [
    "timestamp",
    "semi-major axis",
    "eccentricity",
    "inclination",
    "LoAN",
    "AoP",
    "mean anomaly",
]

for i in range(len(input_file_names)):

    print(input_file_names[i])

    df_sp3 = pd.read_csv(RAW_DATA_DIR + input_file_names[i],
                         header=0,
                         low_memory=False)

    store = pd.HDFStore(OUTPUT_DATA_DIR + output_file_names[i])
    store.put("DORIS_beacon_elements", df_sp3, format='table')