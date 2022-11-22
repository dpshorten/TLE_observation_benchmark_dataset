import pandas as pd
import sp3
import sys
from astropy import coordinates as coord
from astropy import units
from astropy.time import Time
from pytwobodyorbit import TwoBodyOrbit
import os

DOWNSAMPLE_FACTOR = 1

INPUT_FOLDER_PATH =  "/home/david/Projects/TLE_observation_benchmark_dataset/raw_data/DORIS_beacon_data/sp3_cs2/"
OUTPUT_FOLDER_PATH = "/home/david/Projects/TLE_observation_benchmark_dataset/raw_data/DORIS_beacon_data/sp3_cs2_processed/"
SATELLITE_SP3_CODE = b"L12"
SATELLITE_NAME = "CS2"

num_instances = int(sys.argv[1])
this_instance = int(sys.argv[2])

all_files_to_process = []
# iterate through all file
for file_name in sorted(os.listdir(INPUT_FOLDER_PATH)):
    # Check whether file is in .001 format or not
    if file_name.endswith(".001"):
        all_files_to_process.append(file_name)

this_instances_files_to_process = [all_files_to_process[i] for i in range(this_instance, len(all_files_to_process), num_instances)]

for file_name in this_instances_files_to_process:

    output_file_name = OUTPUT_FOLDER_PATH + file_name + "_d" + str(DOWNSAMPLE_FACTOR) + ".csv"

    if os.path.exists(output_file_name):
        print("output", file_name, "already exists")
        continue

    print("instance", this_instance, "processing file", file_name)

    product = sp3.Product.from_file(INPUT_FOLDER_PATH + file_name)
    sat_item = product.satellite_with_id(SATELLITE_SP3_CODE).records
    satellite_recordings = sat_item[0:len(sat_item):DOWNSAMPLE_FACTOR]

    mu_earth = 3.986004418e14
    orbit = TwoBodyOrbit(SATELLITE_NAME, mu=mu_earth)
    t_epoch = []
    sp3_x = []
    sp3_y = []
    sp3_z = []
    sp3_Vx = []
    sp3_Vy = []
    sp3_Vz = []
    sp3_SMA = []
    sp3_ecc = []
    sp3_inc = []
    sp3_LoAN = []
    sp3_AoP = []
    sp3_MA = []

    for sat_record in satellite_recordings:
        sat_pos = sat_record.position
        sat_vel = sat_record.velocity
        time_epoch = Time(sat_record.time)

        coordITRS = coord.ITRS(
            obstime=time_epoch,
            x=sat_pos[0] * units.m,
            y=sat_pos[1] * units.m,
            z=sat_pos[2] * units.m,
            v_x=sat_vel[0] * units.m / units.s,
            v_y=sat_vel[1] * units.m / units.s,
            v_z=sat_vel[2] * units.m / units.s,
            representation_type=coord.CartesianRepresentation,
            differential_type=coord.CartesianDifferential,
        )

        # Convert to GCRS
        cartesian_GCRS = coordITRS.transform_to(coord.GCRS(obstime=time_epoch))
        orbit.setOrbCart(0, cartesian_GCRS.cartesian.xyz, cartesian_GCRS.velocity.d_xyz * 10 ** 3)
        t_epoch.append(time_epoch.datetime)
        elements = orbit.elmKepl()
        sp3_x.append(cartesian_GCRS.cartesian.xyz[0].value)
        sp3_y.append(cartesian_GCRS.cartesian.xyz[1].value)
        sp3_z.append(cartesian_GCRS.cartesian.xyz[2].value)
        sp3_Vx.append(cartesian_GCRS.velocity.d_xyz[0].value * 10 ** 3)
        sp3_Vy.append(cartesian_GCRS.velocity.d_xyz[1].value * 10 ** 3)
        sp3_Vz.append(cartesian_GCRS.velocity.d_xyz[2].value * 10 ** 3)
        sp3_SMA.append(elements["a"])
        sp3_ecc.append(elements["e"])
        sp3_inc.append(elements["i"])
        sp3_LoAN.append(elements["LoAN"])
        sp3_AoP.append(elements["AoP"])
        sp3_MA.append(elements["TA"])

    output_dataFrame = pd.DataFrame({
        "x": sp3_x,
        "y": sp3_y,
        "z": sp3_z,
        "Vx": sp3_Vx,
        "Vy": sp3_Vy,
        "Vz": sp3_Vz,
        "time stamp" : t_epoch,
        "semi-major axis": sp3_SMA,
        "eccentricity": sp3_ecc,
        "Inclination": sp3_inc,
        "LoAN": sp3_LoAN,
        "AoP": sp3_AoP,
        "Mean Anomaly": sp3_MA,
    })
    output_dataFrame = output_dataFrame.set_index("time stamp")
    output_dataFrame.to_csv(output_file_name)

