import pandas as pd
import datetime
import yaml
from yaml import CDumper as Dumper

RAW_DATA_DIR = "../DORIS_beacon_positions/"
OUTPUT_DATA_DIR = "../processed_files/"
MAX_NUM_COLS = 100

output_file_names = [
    "DORIS_beacons_Sentinel-3A.yaml",
    "DORIS_beacons_Sentinel-3B.yaml",
    "DORIS_beacons_Sentinel-6A.yaml",
    "DORIS_beacons_Jason-1.yaml",
    "DORIS_beacons_Jason-2.yaml",
    "DORIS_beacons_Jason-3.yaml",
    "DORIS_beacons_SARAL.yaml",
    "DORIS_beacons_CryoSat-2.yaml",
    "DORIS_beacons_Haiyang-2A.yaml",
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

for i in range(len(input_file_names)):

    print(input_file_names[i], end=" & ")

    df_sp3 = pd.read_csv(RAW_DATA_DIR + input_file_names[i],
                         header=0,
                         parse_dates = ["timestamp"],
                         low_memory=False)

    print("read")
    f = open(OUTPUT_DATA_DIR + output_file_names[i], 'w')
    yaml.dump({"name" : satellite_names[i]}, f)
    yaml.dump({"timestamps": df_sp3["timestamp"].values.astype('datetime64[us]').tolist()}, f, Dumper=Dumper)
    print("timestamps done")
    yaml.dump({"semi-major axis": df_sp3["semi-major axis"].values.tolist()}, f, Dumper=Dumper)
    print("a done")
    yaml.dump({"eccentricity": df_sp3["eccentricity"].values.tolist()}, f, Dumper=Dumper)
    print("ecc done")
    yaml.dump({"inclination": df_sp3["inclination"].values.tolist()}, f, Dumper=Dumper)
    print("inc done")
    yaml.dump({"LoAN": df_sp3["LoAN"].values.tolist()}, f, Dumper=Dumper)
    print("LoAN done")
    yaml.dump({"AoP": df_sp3["AoP"].values.tolist()}, f, Dumper=Dumper)
    print("AoP done")
    yaml.dump({"mean anomaly": df_sp3["mean anomaly"].values.tolist()}, f, Dumper=Dumper)
    print("MA done")

    f.close()

    del df_sp3
