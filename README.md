# TLE Satellite Observation Data

This repository contains a dataset of Two Line Element (TLE) data for 15 satellites. Its purpose is to serve as a benchmark dataset for 
studies examining changes in satellite orbits over larger time scales. It also contains the ground-truth manoeuvre timestamps
for these satellites. Highly-accurate positional data from DORIS ground beacons is also included for some satellites.

Please see the paper: *Wide-scale Monitoring of Satellite Lifetimes: Pitfalls and a Benchmark Dataset* for a detailed 
description of the dataset.

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


The folder `processed_files` contains the TLE files as well as the manoeuvre timestamps. The TLE files conform to the 
[TLE standard](https://celestrak.org/NORAD/documentation/tle-fmt.php) as defined by NORAD. A good starting point for working with them 
is the [Skyfield library](https://rhodesmill.org/skyfield/toc.html) 

Some brief advice on getting started using Skyfield in conjunction with this data. You can use the 
[`tle_file()`](https://rhodesmill.org/skyfield/api-iokit.html#:~:text=on%20its%20name.-,tle_file,-(url%2C ) function to load the TLE file into a list of Skyfield
[`EarthSatellite`](https://rhodesmill.org/skyfield/api-satellites.html#skyfield.sgp4lib.EarthSatellite)  objects. 
([see here](https://rhodesmill.org/skyfield/earth-satellites.html#loading-a-tle-file) 
for some general documentation on loading TLE files). Each `EarthSatellite` object is associated with the data published for one
satellite epoch, which corresponds with a pair of lines in the original TLE file. One can call the `.at()` function on 
these objects to get the satellite position in cartesian geocentric coordinates. One can then use the
[`osculating_elements_of()`](https://rhodesmill.org/skyfield/api-elements.html#skyfield.elementslib.osculating_elements_of) function
to convert this position into osculating keplerian elements. Moreover, by providing times other than the published epoch to the 
`at()` function, it can also perform propagation of the position and osculating elements to different points in time. If one 
is interested in monitoring changes in satellite orbits over longer time scales (weeks to years), we suggest that using the
`at()` function is counter-productive, due to the fact that it uses models of orbiting satellites to add in non-Keplerian
components of the orbit. This is discussed in detail in the paper *Wide-scale Monitoring of Satellite Lifetimes: Pitfalls and a Benchmark Dataset*. 
Rather, we suggest using the mean Keplerian elements that are presented in the raw TLE records. One can still use Skyfield 
to conveniently load and manipulate the data. The mean Keplerian elements are stored as instance variables of the `model` variable of 
each `EarthSatellite` object. Note that these mean elements are also propagated and updated each time the `at()` method 
is called on the `EarthSatellite` object.

The manoeuvre timestamps are stored in YAML files, also found in the directory `processed_files`. 
These files also contain the satellite's [SATCAT number](https://en.wikipedia.org/wiki/Satellite_Catalog_Number) 
as a piece of useful metadata. The timestamps are stored in an item named `manoeuvre_timestamps`. This is a list of
strings of [ISO8601](https://www.iso.org/iso-8601-date-and-time-format.html) timestamps which contain the UTC time and 
date of each manoeuvre.

The accurate positional data from the DORIS ground beacons is stored in the `DORIS_beacon_positions directory` in CSV files.

The directory `plotting` contains the scripts for creating the plots in the paper
*Wide-scale Monitoring of Satellite Lifetimes: Pitfalls and a Benchmark Dataset*.
- `plotting_TLE_propagation_residuals.py` creates the plots in figures 2, 11, 12 and 13.
- `plotting_osculating_mean_and_DORIS.py` creates the plots in figure 3.
- `plotting_osculating_and_mean_diffs_distribution.py` creates the plots in figure 4.
- `plotting_osculating_propagation_to_mean_diff.py` creates the plots in figure 5.
- `plot_satellite_liftimes_gantt.py` creates the plot in figure 6.
- `plotting_propagation_accuracy_TLE_to_SP3.py` creates the plots in figure 7.
- `plotting_DORIS_fourier_analysis.py` creates the plots in figures 8, 9 and 10.

you will need to change the file paths in `params.py`.

The directory `dataset_formatting` contains scripts for manipulating the raw data into the compiled files.