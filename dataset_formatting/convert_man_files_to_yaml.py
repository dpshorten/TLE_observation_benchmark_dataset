import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import pandas as pd
import datetime
import yaml

RAW_DATA_DIR = "../raw_data/"
OUTPUT_DATA_DIR = "../processed_files/"
MAX_NUM_COLS = 100

output_file_names = [
    "manoeuvres_Fengyun-2D.yaml",
    "manoeuvres_Fengyun-2E.yaml",
    "manoeuvres_Fengyun-2F.yaml",
    "manoeuvres_Fengyun-2H.yaml",
    "manoeuvres_Fengyun-4A.yaml",
    "manoeuvres_Sentinel-3A.yaml",
    "manoeuvres_Sentinel-3B.yaml",
    "manoeuvres_Sentinel-6A.yaml",
    "manoeuvres_Jason-1.yaml",
    "manoeuvres_Jason-2.yaml",
    "manoeuvres_Jason-3.yaml",
    "manoeuvres_SARAL.yaml",
    "manoeuvres_CryoSat-2.yaml",
    "manoeuvres_Haiyang-2A.yaml",
    "manoeuvres_TOPEX.yaml",
]

input_file_names = [
    "manFY2D.txt.fy",
    "manFY2E.txt.fy",
    "manFY2F.txt.fy",
    "manFY2H.txt.fy",
    "manFY4A.txt.fy",
    "s3aman.txt",
    "s3bman.txt",
    "s6aman.txt",
    "ja1man.txt",
    "ja2man.txt",
    "ja3man.txt",
    "srlman.txt",
    "cs2man.txt",
    "h2aman.txt",
    "topman.txt",
]

satellite_names = [
    "Fengyun-2D",
    "Fengyun-2E",
    "Fengyun-2F",
    "Fengyun-2H",
    "Fengyun-4A",
    "Sentinel-3A",
    "Sentinel-3B",
    "Sentinel-6A",
    "Jason-1",
    "Jason-2",
    "Jason-3",
    "SARAL",
    "CryoSat-2",
    "Haiyang-2A",
    "TOPEX",
]

satcat_number = [
    29640,
    33463,
    38049,
    43491,
    41882,
    41335,
    43437,
    46984,
    26997,
    33105,
    41240,
    39086,
    36508,
    37781,
    22076,
]


first_dates = []
last_dates = []
lengths = []
all_manoeuvres = []
for i in range(len(input_file_names)):

    print(input_file_names[i], end=" & ")

    #if not file_name.startswith("ja"):
     #   continue

    df_manoeuvre_history = pd.read_csv(RAW_DATA_DIR + input_file_names[i], delim_whitespace=True, names=range(MAX_NUM_COLS))

    manoeuvre_timestamps = []

    if input_file_names[i].endswith(".fy"):
        #first_date = datetime.datetime.strptime(df_manoeuvre_history.iloc[0, 2], '%Y-%m-%dT%H:%M:%S CST')
        #last_date = datetime.datetime.strptime(df_manoeuvre_history.iloc[-1, 2], '%Y-%m-%dT%H:%M:%S CST')
        manoeuvre_timestamps = [datetime.datetime.strptime(df_manoeuvre_history.iloc[j, 2], '%Y-%m-%dT%H:%M:%S CST')
                                for j in range(df_manoeuvre_history.shape[0])]
        manoeuvre_timestamps.sort()
        first_date = manoeuvre_timestamps[0]
        last_date = manoeuvre_timestamps[-1]
    else:
        first_date = (datetime.datetime(year=df_manoeuvre_history.iloc[0, 1], month=1, day=1) +
                      datetime.timedelta(days=int(df_manoeuvre_history.iloc[0, 2])))
        last_date = (datetime.datetime(year=df_manoeuvre_history.iloc[-1, 1], month=1, day=1) +
                     datetime.timedelta(days=int(df_manoeuvre_history.iloc[-1, 2])))
        for j in range(df_manoeuvre_history.shape[0]):
            manoeuvre_timestamps.append(datetime.datetime(year=df_manoeuvre_history.iloc[j, 1], month=1, day=1) +
                                        datetime.timedelta(days=int(df_manoeuvre_history.iloc[j, 2]),
                                                           hours=int(df_manoeuvre_history.iloc[j, 3]),
                                                           minutes=int(df_manoeuvre_history.iloc[j, 4]),
                                                           ))

    all_manoeuvres.append(manoeuvre_timestamps)

    #print(first_date.strftime('%Y-%m-%d'), end=" & ")
    #print(last_date.strftime('%Y-%m-%d'), end=" & ")
    print(len(manoeuvre_timestamps), end=" & ")
    print()
    first_dates.append(first_date)
    last_dates.append(last_date)
    lengths.append(last_date-first_date)
    #print(manoeuvre_timestamps[:10])

    f = open(OUTPUT_DATA_DIR + output_file_names[i], 'w')
    yaml.dump({"name" : satellite_names[i],
               "SATCAT number": satcat_number[i],
               "manoeuvre_timestamps": manoeuvre_timestamps}, f)


