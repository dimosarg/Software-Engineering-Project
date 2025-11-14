import matplotlib.pyplot as plt
import numpy as np

def plot_scatter(y_data, labels, title, x_data=None, save_scatter=False):
    """Visualization of results\n
    **args**:\n
    y_data = 1 dimensional numpy array of time series data (np)\n
    labels = outlier labels that derive from the calculations (np)\n
    title = title of the diagram (str)\n
    x_data = *not necessary* list of custom x axis label data ([])\n
    save_scatter = save diagram with the name same as the title given (bool)\n
    """

    #checks for custom x axis labels
    if x_data is None:

        #if not found aranges the length of the time series data as integers
        x_data = np.arange(len(y_data))

    #definition of label names
    label_names = {0: "Normal", 1: "Outlier"}

    #custom colors for visualization
    colors = {0: "black", 1: "red"}

    #creation of the scatter diagram
    plt.figure()
    for cls in [0,1]:
        mask = labels ==cls
        plt.scatter(x=x_data[mask], y=y_data[mask], c=colors[cls], label=label_names[cls], marker=".")
    plt.title(title)
    plt.legend()
    plt.show()
    if save_scatter==True:
        plt.savefig(f"{title}.png")