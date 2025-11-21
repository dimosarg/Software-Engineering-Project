import sys
import os
import numpy as np
import pandas as pd
import yfinance as yf
from PyQt5 import QtWidgets, uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import calcs


class WarningSEApp(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        # Load interface
        uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'warningSE.ui'), self)

        # Disable buttons at start
        self.btn_execute.setEnabled(False)
        self.btn_export.setEnabled(False)

        # BUTTON CONNECTIONS
        # Load CSV/NPY file
        self.csv_button_input.clicked.connect(self.load_file)
        # Download from Yahoo Finance
        self.btn_generate_values.clicked.connect(self.download_data_from_yahoo)
        # Execute algorithm
        self.btn_execute.clicked.connect(self.execute_script)
        # Export graph to image
        self.btn_export.clicked.connect(self.export_plot)

        # VARIABLES
        self.data = None
        self.labels = None

        # Plot variables
        self.figure = None
        self.canvas = None
        self.toolbar = None
        self.original_data_col = None
        self.original_labels = None

        # Layout for the plot
        if self.plot_view_result.layout() is None:
            self.plot_view_result.setLayout(QtWidgets.QVBoxLayout())

    def download_data_from_yahoo(self):
        """Robust download method compatible with new yfinance versions"""

        # 1. Read ticker
        ticker = self.data_collection.text().strip().upper()

        if not ticker:
            QtWidgets.QMessageBox.warning(self, "Error", "Please enter a ticker symbol (e.g. AAPL)")
            return

        try:
            print(f"--- Starting download for: {ticker} ---")

            # 2. Download
            df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)

            print("Download completed by yfinance.")
            print(f"Data dimensions: {df.shape}")

            if df.empty:
                QtWidgets.QMessageBox.warning(self, "Error",
                                              f"No data found for {ticker}. Check spelling or internet connection.")
                return

            # 3. Clean data
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Ensure we have a price column
            if 'Close' not in df.columns:
                print("Column 'Close' not found, using first available column.")
                prices = df.iloc[:, 0].values.flatten()
            else:
                prices = df['Close'].values.flatten()

            # 4. Create structure for the algorithm
            indices = np.arange(len(prices))
            self.data = np.column_stack((indices, prices))

            print("Data processed successfully. Ready to run.")

            QtWidgets.QMessageBox.information(self, "Success", f"Downloaded {len(prices)} days for {ticker}")
            self.btn_execute.setEnabled(True)

        except Exception as e:
            print(f"CRITICAL ERROR: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to download: {str(e)}")

    def load_file(self):
        """Load files and show path in csv_txt_input"""

        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select file",
            "",
            "Data files (*.npy *.csv *.xlsx *.xls);;Numpy (*.npy);;CSV (*.csv);;Excel (*.xlsx *.xls)"
        )

        if file_path:
            self.csv_txt_input.setText(file_path)

            try:
                # CASE A: NumPy (.npy)
                if file_path.endswith('.npy'):
                    self.data = np.load(file_path, allow_pickle=True)

                # CASE B: Table files (CSV, Excel)
                else:
                    if file_path.endswith('.csv'):
                        df = pd.read_csv(file_path)
                    elif file_path.endswith(('.xlsx', '.xls')):
                        df = pd.read_excel(file_path)

                    # Column selection logic
                    if 'Close' in df.columns:
                        prices = df['Close'].values
                    elif 'Adj Close' in df.columns:
                        prices = df['Adj Close'].values
                    elif len(df.columns) > 1:
                        prices = df.iloc[:, 1].values
                    else:
                        prices = df.iloc[:, 0].values

                    prices = prices[~pd.isna(prices)]
                    indices = np.arange(len(prices))
                    self.data = np.column_stack((indices, prices))

                print(f"File loaded: {file_path}")
                self.btn_execute.setEnabled(True)

            except Exception as e:
                print(f"Error loading file: {e}")
                QtWidgets.QMessageBox.critical(self, "Error", f"Could not read file: {str(e)}")

    def execute_script(self):
        # Original logic intact
        if self.data is not None:
            data_col = self.data[:, 1:2]

            # Call your calcs module
            self.labels = calcs.calculations(data=data_col, std_multiplier=2.5)

            # Clear previous graph
            if self.canvas is not None:
                for i in reversed(range(self.plot_view_result.layout().count())):
                    widget_to_remove = self.plot_view_result.layout().itemAt(i).widget()
                    if widget_to_remove is not None:
                        widget_to_remove.setParent(None)
                self.canvas = None
                self.toolbar = None

            # Create new plot
            self.figure = Figure()
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Expanding)
            self.plot_view_result.layout().addWidget(self.canvas)

            self.toolbar = NavigationToolbar(self.canvas, self)
            self.plot_view_result.layout().addWidget(self.toolbar)

            self.original_data_col = data_col
            self.original_labels = self.labels

            self.plot_data(self.original_data_col, self.original_labels)
            self.btn_export.setEnabled(True)

    def plot_data(self, data_col, labels):
        """Helper function to plot the financial line chart with outlier alerts"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        x_data = np.arange(len(data_col))

        # 1. PLOT PRICE LINE (Trend)
        # We use plot instead of scatter to connect the points
        ax.plot(x_data, data_col, color='#1f77b4', linewidth=1.5, label='Price History', alpha=0.8)

        # 2. PLOT ONLY OUTLIERS (Red Points)
        # Filter to get only the indices where label == 1
        outlier_mask = labels.flatten() == 1

        if np.any(outlier_mask):  # Only plot if there are outliers
            ax.scatter(
                x_data[outlier_mask],
                data_col[outlier_mask],
                color='red',
                s=60,  # Larger size to make them stand out
                edgecolor='black',  # Black edge for contrast
                label='Anomaly / Outlier',
                zorder=5  # Ensures points stay ON TOP of the line
            )

        # 3. FINANCIAL STYLING
        ax.set_title("Price Evolution & Anomaly Detection")
        ax.set_ylabel("Price ($)")
        ax.set_xlabel("Time (Days)")

        # Add grid, essential for reading stock charts
        ax.grid(True, which='major', linestyle='--', linewidth=0.5, color='grey', alpha=0.5)

        ax.legend()
        self.canvas.draw()

    def export_plot(self):
        if self.figure is not None:
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "Save image", "scatter.png", "PNG files (*.png)"
            )
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
