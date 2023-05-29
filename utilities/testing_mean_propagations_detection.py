import datetime
import matplotlib
import matplotlib.pyplot as plt
from util import convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements
from skyfield.api import load as skyfield_load
import astropy.constants
import pandas as pd
import numpy as np
from params import TLE_Lifetime_Analysis_Parameters
from plotting_TLE_propagation_residuals import calc_residuals_for_propagation_distance
import yaml
from joblib import Parallel, delayed

PLOT_INDEX = 0

TLE_FILE_NAMES = [
    "Fengyun-2D.tle",
    "Fengyun-2E.tle",
    "Fengyun-2F.tle",
    "Fengyun-2H.tle",
    "Fengyun-4A.tle",
    "Sentinel-3A.tle",
    "Sentinel-3B.tle",
    "Sentinel-6A.tle",
    "Jason-1.tle",
    "Jason-2.tle",
    "Jason-3.tle",
    "SARAL.tle",
    "CryoSat-2.tle",
    "Haiyang-2A.tle",
    "TOPEX.tle",
]

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

NAMES_LIST = [
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

Y_AXIS_LABELS = [
    "diff in semi-major axes (km)",
    "diff in eccentricity",
    "diff in inclination (radians)",
]

OUTPUT_FIGURE_NAMES = [
    "multi_sats-SMA_diffs_mean_and_osculating.pdf",
    "multi_sats-ecc_diffs_mean_and_osculating.pdf",
    "multi_sats-inc_diffs_mean_and_osculating.pdf",
]

params = TLE_Lifetime_Analysis_Parameters()

N_JOBS = 10

SIMPLE_MATCHING_MAX_DISTANCE_DAYS = 3
matchingMaxDistanceTimedelta = pd.Timedelta(days=SIMPLE_MATCHING_MAX_DISTANCE_DAYS)
matchingMaxDistanceSeconds = matchingMaxDistanceTimedelta.total_seconds()


def computeSimpleMatchingPrecisionRecallForOneThreshold(
    manoeuvreTimestamps,
    timeStamps,
    manoeuvreTimestampsSeconds,
    timeStampsSeconds,
    preds,
    threshold,
    precision,
    recall,
    ind,
    returnTimeDeviationsAndPreds=False,
):
    predToTrueDict = {}
    trueToPredDict = {}

    for i in range(preds.shape[0]):
        if preds[i] >= threshold:
            leftIndex = np.searchsorted(
                manoeuvreTimestampsSeconds, timeStampsSeconds[i]
            )

            if leftIndex != 0:
                leftIndex -= 1

            indexOfClosest = leftIndex

            if (leftIndex < manoeuvreTimestamps.shape[0] - 1) and (
                abs(manoeuvreTimestampsSeconds[leftIndex] - timeStampsSeconds[i])
                > abs(manoeuvreTimestampsSeconds[leftIndex + 1] - timeStampsSeconds[i])
            ):

                indexOfClosest = leftIndex + 1

            # diffs = np.abs(manoeuvreTimestampsSeconds - timeStampsSeconds[i])
            # indexOfClosest = np.argmin(diffs)

            # diff = abs(
            #     manoeuvreTimestampsSeconds[indexOfClosest] - timeStampsSeconds[i]
            # )
            # commented by Yang, only considering the onward window
            diff = manoeuvreTimestampsSeconds[indexOfClosest] - timeStampsSeconds[i]

            if diff < matchingMaxDistanceSeconds:
                predToTrueDict[i] = (
                    indexOfClosest,
                    diff,
                )
                if indexOfClosest in trueToPredDict:
                    trueToPredDict[indexOfClosest].append(i)
                else:
                    trueToPredDict[indexOfClosest] = [i]

    predPositives = np.argwhere(preds >= threshold)[:, 0]
    falsePositives = {
        predInd for predInd in predPositives if predInd not in predToTrueDict.keys()
    }

    groundPositives = np.arange(0, len(manoeuvreTimestamps))
    falseNegatives = {
        trueInd for trueInd in groundPositives if trueInd not in trueToPredDict.keys()
    }
    precision[ind] = len(trueToPredDict) / (len(trueToPredDict) + len(falsePositives))
    recall[ind] = len(trueToPredDict) / (len(trueToPredDict) + len(falseNegatives))

    if returnTimeDeviationsAndPreds:
        predTimeStamps = pd.Series(
            [timeStamps[predIndex] for predIndex in predToTrueDict.keys()]
        )
        timeDeviations = np.array([pair[1] for pair in predToTrueDict.values()])
        return timeDeviations, predTimeStamps


def convertTimestampSeriesToEpoch(series):
    return (
        (series - pd.Timestamp(year=1970, month=1, day=1)) // pd.Timedelta(seconds=1)
    ).values


def getPrecisionRecallCurveSimpleMatching(manoeuvreTimestamps, predTimestamps, preds):
    sortedPreds = np.sort(preds)
    # remove infs:
    sortedPreds = sortedPreds[sortedPreds < 1e9]
    precision = np.zeros((sortedPreds.shape[0] - 1))
    recall = np.zeros((sortedPreds.shape[0] - 1))
    # Exclude last element as it leads to division by 0 for the precision

    manoeuvreTimestampsSeconds = convertTimestampSeriesToEpoch(manoeuvreTimestamps)
    predTimeStampsSeconds = convertTimestampSeriesToEpoch(predTimestamps)

    # Parallel(n_jobs=N_JOBS, require="sharedmem")(
    #     delayed(computeSimpleMatchingPrecisionRecallForOneThreshold)(
    #         manoeuvreTimestamps,
    #         predTimestamps,
    #         manoeuvreTimestampsSeconds,
    #         predTimeStampsSeconds,
    #         preds,
    #         sortedPreds[i],
    #         precision,
    #         recall,
    #         i,
    #     )
    #     for i in range(sortedPreds.shape[0] - 1)
    # )

    for i in range(sortedPreds.shape[0] - 1):
        computeSimpleMatchingPrecisionRecallForOneThreshold(
            manoeuvreTimestamps,
            predTimestamps,
            manoeuvreTimestampsSeconds,
            predTimeStampsSeconds,
            preds,
            sortedPreds[i],
            precision,
            recall,
            i,)

    return precision, recall, sortedPreds[:-1]

for j in range(len(TLE_FILE_NAMES)):

    print(TLE_FILE_NAMES[j])

    mean_residuals = calc_residuals_for_propagation_distance(1, TLE_FILE_NAMES[j])["mean_to_mean_SMA_diff"]
    #print(NAMES_LIST[j], residuals["mean_to_mean_SMA_diff"].iloc[:3])

    manoeuvres = pd.Series(yaml.load(open(params.manoeuver_files_directory + MANOEUVRE_FILE_NAMES[j], 'r'), yaml.FullLoader)["manoeuvre_timestamps"])

    print(manoeuvres[:10])
    print(mean_residuals.index.to_series()[:10])
    print(mean_residuals.abs().values[:10])

    precision, recall, sortedPreds = getPrecisionRecallCurveSimpleMatching(manoeuvres, mean_residuals.index.to_series(), mean_residuals.abs().values)



    print(len(precision), precision.shape, type(precision))
    print(len(recall), recall.shape)

    print(precision[:10])
    print(recall[:10])

    print(precision[-10:])
    print(recall[-10:])

    plt.clf()
    fig = plt.figure(figsize = (10, 10))
    plt.plot(recall, precision, linewidth = 3)
    plt.title(NAMES_LIST[j])
    plt.xlabel("recall")
    plt.ylabel("precision")
    plt.ylim([0, 1.1])
    plt.xlim([0, 1.1])
    plt.savefig("../plots/" + NAMES_LIST[j] + ".png")
