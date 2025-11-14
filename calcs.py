import numpy as np

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

    #Iterative process for calculations
    for i in range(lookback_period,len(data)):

        #Calculate standard deviation for current point
        std_now = np.std(data[i-lookback_period:i])

        #Calculate bounds of buffer zone
        upper_bound[i] = data[i] + std_now*std_multiplier
        lower_bound[i] = data[i] - std_now*std_multiplier

        #Criteria for outlier labeling
        if data[i] >= upper_bound[i-1] or data[i] <= lower_bound[i-1]:
            outlier_index[i] = 1

    return outlier_index