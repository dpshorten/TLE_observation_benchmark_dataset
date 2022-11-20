import pandas as pd
import datetime
from skyfield.api import load as skyfieldLoad
import requests
import math
from sgp4.api import days2mdhms

RAW_DATA_DIR = "../raw_data/"
OUTPUT_DATA_DIR = "../processed_files/"
MAX_NUM_COLS = 100

output_file_names = [
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



def tleDownload(satellite_catalogue_number,
                output_file_name,
                start_date,
                end_date):
    """_download tle data given satellite and date information_

    Args:
        satDict (_dictionary_): _satellite information and date information_
        outFile (_string_): _*.txt file name to save tle data_
    """
    outFile = OUTPUT_DATA_DIR + output_file_name
    # Request URLs
    uriBase = "https://www.space-track.org"
    requestLogin = "/ajaxauth/login"
    requestCmdAction = "/basicspacedata/query"
    requestFindCustom1 = "/class/gp_history/NORAD_CAT_ID/"
    requestFindCustom2 = "/orderby/TLE_LINE1%20ASC/EPOCH/"
    requestFindCustom3 = "/format/tle"

    # API login ID
    configUsr = "david.shorten@adelaide.edu.au"
    configPwd = "6UrVkC*3mg4NJse"
    siteCred = {"identity": configUsr, "password": configPwd}

    # use requests package to drive the RESTful session with space-track.org
    with requests.Session() as session:
        # run the session in a with block to force session to close if we exit

        # need to log in first. note that we get a 200 to say the web site got the data, not that we are logged in
        resp = session.post(uriBase + requestLogin, data=siteCred)
        #print(resp)
        if resp.status_code != 200:
            print(resp)
            print("POST fail on login")

        # customSat = input("Please enter the satellite name : ")
        # catId = input("Please enter the NORAD ID of the satellite : ")
        # dateStart = input("Please enter the start date (YYYY-MM-DD format with hyphens) : ")
        # dateEnd = input("Please enter the end date (YYYY-MM-DD format with hyphens) : ")
        #customSat = satInfo[0]
        catId = str(satellite_catalogue_number)
        dateStart = start_date.strftime('%Y-%m-%d')
        dateEnd = end_date.strftime('%Y-%m-%d')

        # Retrieves the result of the custom query
        resp = session.get(
            uriBase
            + requestCmdAction
            + requestFindCustom1
            + catId
            + requestFindCustom2
            + dateStart
            + "--"
            + dateEnd
            + requestFindCustom3
        )
        if resp.status_code != 200:
            print(resp)
            print(resp.reason)
            print("GET fail on request")

        # Assign the result line by line
        retData = resp.text.splitlines()
    # Closing the session with the API and ending the program
    session.close()

    print(int(round(len(retData)/2)), "&")

    l1 = []  # Table for line "1"
    l2 = []  # Table for line "2"
    i = 1

    # For each line of the answer, we alternate between 1 and 2
    for line in retData:
        j = i
        if i == 1:
            # If it is 1, we add the line we are reading to l1
            l1.append(line[:69])
            j = 2
        elif i == 2:
            # If it is 2, we add the line we are reading to l2
            l2.append(line[:69])
            j = 1
        i = j

    MU = (398600.4418 * 10**9) * 2 * math.pi / 86400
    k = 0
    dayList = []
    # lists for two lines, deleting extra tles and leaving one tle per day
    tleLine1List = []
    tleLine2List = []

    #print(l1)
    #print(l2)
    while k < len(l1):

        # store the days in a list to retrieve 1 data per day
        month, day, hour, minute, second = days2mdhms(
            int(l1[k][18:20]), float(l1[k][20:32])
        )

        dayList.append(day)

        if (dayList[k] != dayList[k - 1]) or k == 0:
            tleLine1List.append(l1[k])
            tleLine2List.append(l2[k])

        k = k + 1

    # reset index k to the second data
    k = 0
    # Open the outFile.txt file in write mode
    outTLEFile = open(outFile, "w")
    while k < len(tleLine1List):
        # Write the two lines to the raw file
        outTLEFile.write(tleLine1List[k] + "\n")
        outTLEFile.write(tleLine2List[k] + "\n")

        k = k + 1
    # Close the file
    outTLEFile.close()

    # Load and parse a TLE file, returning a list of Earth satellites using Skyfield API load
    dataSat = skyfieldLoad.tle_file(
        outFile,
        reload=False,
    )

    return dataSat


for i in range(len(input_file_names)):

    #print(input_file_names[i], end=" & ")

    df_manoeuvre_history = pd.read_csv(RAW_DATA_DIR + input_file_names[i], delim_whitespace=True, names=range(MAX_NUM_COLS))

    if input_file_names[i].endswith(".fy"):
        first_date = datetime.datetime.strptime(df_manoeuvre_history.iloc[0, 2], '%Y-%m-%dT%H:%M:%S CST')
        last_date = datetime.datetime.strptime(df_manoeuvre_history.iloc[-1, 2], '%Y-%m-%dT%H:%M:%S CST')

    else:
        first_date = (datetime.datetime(year=df_manoeuvre_history.iloc[0, 1], month=1, day=1) +
                      datetime.timedelta(days=int(df_manoeuvre_history.iloc[0, 2])))
        last_date = (datetime.datetime(year=df_manoeuvre_history.iloc[-1, 1], month=1, day=1) +
                     datetime.timedelta(days=int(df_manoeuvre_history.iloc[-1, 2])))

    tleDownload(satcat_number[i], output_file_names[i],
                first_date + datetime.timedelta(days=7),
                last_date - datetime.timedelta(days=7))