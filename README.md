# TLE Satellite Observation Data

This repository contains a dataset with Two Line Element (TLE) data for 15 satellites. Its purpose is to serve as a benchmark dataset for 
studies examining changes in satellite orbits over larger time scales. It also contains the ground-truth manoeuvre timestamps
for these satellites. Highly-accurate positional data from DORIS ground beacons is also included for some satellites.

Please see the paper: *Wide-scale Monitoring of Satellite Lifetimes: Pitfalls and a Benchmark Dataset* for a detailed 
description of the dataset.

The folder `processed_files` contains the TLE files as well as the manoeuvre timestamps. The TLE files conform to the 
[TLE standard](https://celestrak.org/NORAD/documentation/tle-fmt.php) as defined by NORAD. A good starting point for  
working with them is the [Skyfield library](https://rhodesmill.org/skyfield/toc.html) 
([see here](https://rhodesmill.org/skyfield/earth-satellites.html#loading-a-tle-file) for documentation on loading TLE files).
The manoeuvre timestamps are stored in YAML files. 
These files also contain the satellite's [SATCAT number](https://en.wikipedia.org/wiki/Satellite_Catalog_Number) 
as a piece of useful metadata. The timestamps are stored in an item named `manoeuvre_timestamps`. This is a list of
strings of [ISO8601](https://www.iso.org/iso-8601-date-and-time-format.html) timestamps which contain the UTC time and 
date of each manoeuvre.

The following table lists the satellites in the dataset:

| Name         |  SATCAT Number | First Manoeuvre | Last Manoeuvre |
|--------------|----------------|-----------------|----------------|
|Fengyun-2D    | 29640          | 2011-02-01      | 2015-04-10     |   
|Fengyun-2E    | 33463          | 2011-03-17      | 2018-10-15     |
|Fengyun-2F    | 38049          | 2012-09-11      | 2022-01-05     |
|Fengyun-2H    | 43491          | 2019-01-18      | 2022-01-18     |
|Fengyun-4A    | 41882          | 2018-05-22      | 2022-02-21     |
|Sentinel-3A   | 41335          | 2016-02-23      | 2022-10-07     |
|Sentinel-3B   | 43437          | 2018-05-01      | 2022-10-07     |
|Sentinel-6A   | 46984          | 2020-11-24      | 2022-10-14     |
|Jason-1       | 26997          | 2001-12-12      | 2013-06-14     |
|Jason-2       | 33105          | 2008-06-24      | 2019-10-05     |
|Jason-3       | 41240          | 2016-01-20      | 2022-10-11     |
|SARAL         | 39086          | 2013-02-28      | 2022-09-22     |
|CryoSat-2     | 36508          | 2010-04-16      | 2022-10-06     |
|Haiyang-2A    | 37781          | 2011-09-29      | 2020-06-10     |
|TOPEX         | 22076          | 1992-08-18      | 2004-11-18     |

The accurate positional data from the DORIS ground beacons is stored in the DORIS_beacon_positions directory in CSV files.

The directory `plotting` contains the scripts for creating the plots in that paper.
- `plotting_TLE_propagation_residuals.py` creates the plots in figures 2, 11, 12 and 13.
- `plotting_osculating_mean_and_DORIS.py` creates the plots in figure 3.
- `plotting_osculating_and_mean_diffs_distribution.py` creates the plots in figure 4.
- `plotting_osculating_propagation_to_mean_diff.py` creates the plots in figure 5.
- `plot_satellite_liftimes_gantt.py` creates the plot in figure 6.
- `plotting_propagation_accuracy_TLE_to_SP3.py` creates the plots in figure 7.
- `plotting_DORIS_fourier_analysis.py` creates the plots in figures 8, 9 and 10.

you will need to change the file paths in params.py

The directory `dataset_formatting` contains scripts for manipulating the raw data into the compiled files.