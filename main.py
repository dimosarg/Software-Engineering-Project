import sys
import os
import numpy as np
from PyQt5 import QtWidgets, uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import calcs  # Module with calculations functions


class WarningSEApp(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        # Load the .ui file
        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'warningSE.ui'), self)

        # Disable buttons initially
        self.btn_execute.setEnabled(False)
        self.btn_export.setEnabled(False)

        # Connect buttons
        self.csv_button_input.clicked.connect(self.load_file)
        self.btn_execute.clicked.connect(self.execute_script)
        self.btn_export.clicked.connect(self.export_plot)

        # Variables to store data and figure
        self.data = None
        self.labels = None
        self.figure = None
        self.canvas = None
        self.toolbar = None
        self.original_data_col = None
        self.original_labels = None

        # Ensure the plot widget has a layout
        if self.plot_view_result.layout() is None:
            self.plot_view_result.setLayout(QtWidgets.QVBoxLayout())

    def load_file(self):
        # Open file dialog to select the document
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select .npy file", "", "Numpy files (*.npy)")
        if file_path:
            self.csv_txt_input.setText(file_path)  # Show path in text field
            self.data = np.load(file_path, allow_pickle=True)
            # Enable execute button
            self.btn_execute.setEnabled(True)

    def execute_script(self):
        if self.data is not None:
            data_col = self.data[:, 1:2]
            self.labels = calcs.calculations(data=data_col, std_multiplier=6)

            # Clear old canvas and toolbar if exists
            if self.canvas is not None:
                for i in reversed(range(self.plot_view_result.layout().count())):
                    widget_to_remove = self.plot_view_result.layout().itemAt(i).widget()
                    if widget_to_remove is not None:
                        widget_to_remove.setParent(None)
                self.canvas = None
                self.toolbar = None

            # Create new figure and canvas
            self.figure = Figure()
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Expanding)
            self.plot_view_result.layout().addWidget(self.canvas)

            # Add navigation toolbar for interactive zoom/pan
            self.toolbar = NavigationToolbar(self.canvas, self)
            self.plot_view_result.layout().addWidget(self.toolbar)

            # Store original data for reference
            self.original_data_col = data_col
            self.original_labels = self.labels

            # Plot initial data
            self.plot_data(self.original_data_col, self.original_labels)

            # Enable export button
            self.btn_export.setEnabled(True)

    def plot_data(self, data_col, labels):
        """Helper function to plot the scatter chart"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        x_data = np.arange(len(data_col))
        for cls in [0, 1]:
            mask = labels.flatten() == cls
            ax.scatter(
                x_data[mask],
                data_col[mask],
                c=("black" if cls == 0 else "red"),
                label=("Normal" if cls == 0 else "Outlier"),
                marker="."
            )
        ax.set_title("My scatter")
        ax.legend()
        self.canvas.draw()

    def export_plot(self):
        if self.figure is not None:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save image", "scatter.png", "PNG files (*.png)")
            if file_path:
                self.figure.savefig(file_path)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.canvas is not None:
            self.canvas.draw()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = WarningSEApp()
    window.show()
    sys.exit(app.exec_())
