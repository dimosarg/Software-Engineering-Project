import calcs
import visualization as vis
import numpy as np

#Download time series data from a npy file
all_data = np.load("btc-usd.npy")

#Select only one column
data = all_data[:,1:2]

#Outlier labeling
labels = calcs.calculations(data=data, std_multiplier=10)

#Plotting
vis.plot_scatter(y_data=data,labels=labels,title="My scatter", save_scatter=True)