import yaml
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import datetime
from params import TLE_Lifetime_Analysis_Parameters

MANOEUVRE_FILE_NAMES = [
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

SATELLITE_NAMES = [
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

params = TLE_Lifetime_Analysis_Parameters()

all_manoeuvres = []
first_dates = []
lengths = []
for i in range(len(MANOEUVRE_FILE_NAMES)):
    f = open(params.manoeuver_files_directory + MANOEUVRE_FILE_NAMES[i], "r")
    manoeuvre_timestamps = yaml.safe_load(f)["manoeuvre_timestamps"]
    first_dates.append(manoeuvre_timestamps[0])
    lengths.append(manoeuvre_timestamps[-1] - manoeuvre_timestamps[0])
    all_manoeuvres.append(manoeuvre_timestamps)

font = {'size': 16}
matplotlib.rc('font', **font)
plt.figure(figsize=(7, 10))
ax = plt.gca()
plt.gcf().subplots_adjust(left=0.21)
satellite_names = list(reversed(SATELLITE_NAMES))
lengths = list(reversed(lengths))
first_dates = list(reversed(first_dates))
ax.barh(satellite_names, lengths, left=first_dates, height=0.5, color='b', alpha = 0.5)
all_manoeuvres.reverse()
ax.eventplot(all_manoeuvres, color='r', linelengths=0.5, linewidths=1, alpha=0.75)
ax.set_xlim([datetime.datetime(year=1992, month=1, day=1), datetime.datetime(year=2023, month=1, day=1)])
ax.set_xticks([
    datetime.datetime(year=1992, month=1, day=1),
    datetime.datetime(year=1997, month=1, day=1),
    datetime.datetime(year=2002, month=1, day=1),
    datetime.datetime(year=2007, month=1, day=1),
    datetime.datetime(year=2012, month=1, day=1),
    datetime.datetime(year=2017, month=1, day=1),
    datetime.datetime(year=2022, month=1, day=1),
])
ax.xaxis.set_major_formatter(DateFormatter("%Y"))
plt.grid(axis='x')
plt.savefig(params.figs_output_directory + "satellite_gantt.pdf")
#plt.show()