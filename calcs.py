import numpy as np
import pandas as pd

def calculations(data:np, lookback_period=14, std_multiplier=2):
    """Labeling of dataset as outliers and normal values where 0 are normal values and 1 are outliers\n
    **args:**\n
    data = 1 dimensional numpy array of time series data (np)\n
    lookback_period = number of previous datapoints with which the std calculation is made (int)\n
    std_multiplier = Multiplication value of std. The higher it is the less sensitive the outliers get (float/int)\n
    """
    #Definition of upper and lower bounds of the buffer zone
    upper_bound = np.zeros(len(data))
    lower_bound = np.zeros(len(data))

    #Definition of the label matrix
    outlier_index = np.zeros(len(data))

    upper_bound[0:lookback_period] = np.sum(data[:lookback_period])/lookback_period
    lower_bound[0:lookback_period] = np.sum(data[:lookback_period])/lookback_period
    
    #Iterative process for calculations
    for i in range(lookback_period,len(data)):

        #Calculate standard deviation for current point
        std_now = np.std(data[i-lookback_period:i])

        #Calculate bounds of buffer zone
        upper_bound[i] = (np.sum(data[i-lookback_period:i])/lookback_period) + std_now*std_multiplier
        lower_bound[i] = (np.sum(data[i-lookback_period:i])/lookback_period) - std_now*std_multiplier

        #Criteria for outlier labeling
        if data[i] >= upper_bound[i] or data[i] <= lower_bound[i]:
            outlier_index[i] = 1

    diff = np.diff(outlier_index, prepend=0)

    # 2. Keep only where the difference is exactly 1 (the rising edge)
    outlier_index = (diff == 1)

    boundaries = True

    return outlier_index, upper_bound, lower_bound, boundaries

def clean_data(data:np,keep_zeros):

    #Conversion to pandas DataFrame
    my_data = pd.DataFrame(data)

    my_data_len_one = len(my_data)

    #Check for NaN
    my_data_len = len(my_data)
    my_data = my_data.dropna()
    print(f"Deleted data from NaN values: {my_data_len-len(my_data)}\n")

    #Check for 0
    if keep_zeros==False:
        my_data_len = len(my_data)
        no_zeros_mask = (my_data != 0).all(axis=1)
        my_data = my_data[no_zeros_mask]
        print(f"Deleted data from 0 values: {my_data_len-len(my_data)}\n")

    return my_data.to_numpy(), my_data_len_one-my_data_len


def kalman_filters(data:np, outlier_threshold, measurement_noise=1.0):

    x_est = data[0]
    cov = 1.0

    process_noise = measurement_noise/10

    outlier_index = np.zeros(len(data))


    for z in range(len(data)):
        x_pred = x_est
        cov_pred = cov + process_noise

        dif = data[z] - x_pred
        dif_cov = cov_pred + measurement_noise

        std = np.sqrt(dif_cov)
        z_score = np.abs(dif/std)

        if z_score >= outlier_threshold:
            outlier_index[z] = 1
            x_new = x_pred
            cov_new = cov_pred

        else:
            kalman_gain = cov_pred / dif_cov
            x_new = x_pred + kalman_gain * dif
            cov_new = (1 - kalman_gain) * cov_pred

        x_est = x_new
        cov = cov_new

    boundaries = False

    return outlier_index,  boundaries