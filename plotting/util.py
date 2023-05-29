from skyfield.api import load as skyfield_load
import numpy as np
import pandas as pd
import skyfield.elementslib as skyfield_ele

def convert_skyfield_earthSatellites_into_dataframe_of_keplerian_elements(list_of_skyfield_earthSatellites, date_offset = 0):

    """
    Convert the tle data into classical Keplerian elements (semi-major axis, eccentricity and inclination)

    Refactoring of tleKepEleTimeSeries, mostly to help David with understanding the code

    Also includes the position and velocity in both ECI cartesian and RIC.

    Args:
        dataSat (_Skyfield list_): _TLE data for all epochs by using Skyfield function load (Load and parse a TLE file, returning a list of Earth satellites)_

    Returns:
        _pandas dataframe_: _classical Keperian elements (semi-major axis, eccentricity and inclination) with time stamps_
    """

    skyfield_timescale = skyfield_load.timescale()

    list_of_timestamps = []
    list_of_SMA_values = []
    list_of_eccentricity_values = []
    list_of_inclination_values = []
    list_of_LOAN_values = []
    list_of_AOP_values = []
    list_of_mean_anomaly_values = []
    np_mean_kepler_elements = np.zeros((len(list_of_skyfield_earthSatellites) - date_offset, 7))
    np_ECI_coords = np.zeros((len(list_of_skyfield_earthSatellites) - date_offset, 6))
    np_RIC_coords = np.zeros((len(list_of_skyfield_earthSatellites) - date_offset, 6))
    #for skyfield_earth_satellite in list_of_skyfield_earth_satellites:
    for i in range(date_offset, len(list_of_skyfield_earthSatellites)):

        # transfer the time at the next epoch
        current_epoch = list_of_skyfield_earthSatellites[i].epoch.utc_datetime()
        t_current = skyfield_timescale.utc(
            year=current_epoch.year,
            month=current_epoch.month,
            day=current_epoch.day,
            hour=current_epoch.hour,
            minute=current_epoch.minute,
            second=current_epoch.second,
        )

        #time_stamp = pd.to_datetime(pd_timestamp_of_current_epoch)

        # obtain _keplerian elements at the next epoch from _t_l_e
        skyfield_earth_satellite_at_current = list_of_skyfield_earthSatellites[i - date_offset].at(t_current)
        sky_field_keplerian_elements = skyfield_ele.osculating_elements_of(skyfield_earth_satellite_at_current)
        r_ECI = skyfield_earth_satellite_at_current.position.km
        v_ECI = skyfield_earth_satellite_at_current.velocity.km_per_s
        r_RIC, v_RIC = eci_2_ric(r_ECI, v_ECI)



        pd_timestamp_of_current_epoch = pd.Timestamp(current_epoch)
        pd_timestamp_of_current_epoch = pd_timestamp_of_current_epoch.replace(tzinfo=None)

        list_of_timestamps.append(pd_timestamp_of_current_epoch)
        list_of_SMA_values.append(sky_field_keplerian_elements.semi_major_axis.km)
        list_of_eccentricity_values.append(sky_field_keplerian_elements.eccentricity)
        list_of_inclination_values.append((sky_field_keplerian_elements.inclination.radians / np.pi) * 180.0)
        list_of_LOAN_values.append((sky_field_keplerian_elements.longitude_of_ascending_node.radians / np.pi) * 180.0)
        list_of_AOP_values.append((sky_field_keplerian_elements.argument_of_periapsis.radians / np.pi) * 180.0)
        list_of_mean_anomaly_values.append((sky_field_keplerian_elements.mean_anomaly.radians / np.pi) * 180.0)
        np_mean_kepler_elements[i-date_offset, 0] = (list_of_skyfield_earthSatellites[i - date_offset].model.am *
                                                     list_of_skyfield_earthSatellites[i - date_offset].model.radiusearthkm)
        np_mean_kepler_elements[i - date_offset, 1] = list_of_skyfield_earthSatellites[i - date_offset].model.em
        np_mean_kepler_elements[i - date_offset, 2] = list_of_skyfield_earthSatellites[i - date_offset].model.im
        np_mean_kepler_elements[i - date_offset, 3] = list_of_skyfield_earthSatellites[i - date_offset].model.Om
        np_mean_kepler_elements[i - date_offset, 4] = list_of_skyfield_earthSatellites[i - date_offset].model.om
        np_mean_kepler_elements[i - date_offset, 5] = list_of_skyfield_earthSatellites[i - date_offset].model.mm
        np_mean_kepler_elements[i - date_offset, 6] = list_of_skyfield_earthSatellites[i - date_offset].model.nm

        np_ECI_coords[i-date_offset, :3] = r_ECI
        np_ECI_coords[i-date_offset, 3:] = v_ECI
        np_RIC_coords[i-date_offset, :3] = r_RIC
        np_RIC_coords[i-date_offset, 3:] = v_RIC

    df_keplerian_elements = pd.DataFrame({
        "timestamp" : list_of_timestamps,
        "semi-major axis" : list_of_SMA_values,
        "eccentricity" : list_of_eccentricity_values,
        "inclination" : list_of_inclination_values,
        "_lo_a_n" : list_of_LOAN_values,
        "_ao_p" : list_of_AOP_values,
        "mean anomaly" : list_of_mean_anomaly_values,
        "x": np_ECI_coords[:, 0],
        "y": np_ECI_coords[:, 1],
        "z": np_ECI_coords[:, 2],
        "v_x": np_ECI_coords[:, 3],
        "v_y": np_ECI_coords[:, 4],
        "v_z": np_ECI_coords[:, 5],
        "U": np_RIC_coords[:, 0],
        "V": np_RIC_coords[:, 1],
        "W": np_RIC_coords[:, 2],
        "v_U": np_RIC_coords[:, 3],
        "v_V": np_RIC_coords[:, 4],
        "v_W": np_RIC_coords[:, 5],
        "average semi-major axis": np_mean_kepler_elements[:, 0],
        "average eccentricity": np_mean_kepler_elements[:, 1],
        "average inclination": np_mean_kepler_elements[:, 2],
        "average right ascension of ascending node": np_mean_kepler_elements[:, 3],
        "average argument of perigee": np_mean_kepler_elements[:, 4],
        "average mean anomaly": np_mean_kepler_elements[:, 5],
        "average mean motion": np_mean_kepler_elements[:, 6],
    })
    df_keplerian_elements = df_keplerian_elements.set_index("timestamp")

    return df_keplerian_elements


def eci_2_ric(r_ECI, v_ECI):
    n_row = np.shape(r_ECI)[0]
    if r_ECI.ndim == 1:
        n_col = 1
    else:
        n_col = np.shape(r_ECI)[1]

    r_RIC = np.zeros((n_row, n_col))
    v_RIC = np.zeros((n_row, n_col))
    if r_ECI.ndim > 1:
        for i in range(n_col):
            u = normalise_array(r_ECI[:, i])
            w = normalise_array(np.cross(u, v_ECI[:, i]))
            v = normalise_array(np.cross(w, u))
            # reshaping the arrays into column vectors
            u = u.reshape((-1, 1))
            v = v.reshape((-1, 1))
            w = w.reshape((-1, 1))
            m_ECI_2_RIC = np.hstack((u, v, w))
            r_RIC[:, i] = m_ECI_2_RIC.dot(r_ECI[:, i])
            v_RIC[:, i] = m_ECI_2_RIC.dot(v_ECI[:, i])
    else:
        u = normalise_array(r_ECI)
        w = normalise_array(np.cross(u, v_ECI))
        v = normalise_array(np.cross(w, u))
        # reshaping the arrays into column vectors
        u = u.reshape((-1, 1))
        v = v.reshape((-1, 1))
        w = w.reshape((-1, 1))
        m_ECI_2_RIC = np.hstack((u, v, w))
        r_RIC = m_ECI_2_RIC.dot(r_ECI)
        v_RIC = m_ECI_2_RIC.dot(v_ECI)

    return r_RIC, v_RIC

def normalise_array(arr):
    norm_arr = np.linalg.norm(arr)
    if norm_arr == 0:
        return arr
    else:
        return arr / norm_arr