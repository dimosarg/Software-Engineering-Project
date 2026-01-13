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

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class WarningSEApp(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        # --- UPDATED LINE BELOW ---
        # Use resource_path to find the UI file inside the EXE
        ui_file = resource_path('Exercise3\\Software-Engineering-Project\\warningSE.ui')
        uic.loadUi(ui_file, self)
        # --------------------------

    # def __init__(self):
    #     super().__init__()

    #     # Load interface
    #     uic.loadUi(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'warningSE.ui'), self)

        # Disable buttons at the start
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
        # Checkbox
        self.zero_checkbox.toggled.connect(self.get_checkbox_value)
        
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

    def get_checkbox_value(self):
        if self.zero_checkbox.isChecked():
            keep_zeros = True
        else:
            keep_zeros = False

        return keep_zeros

    def download_data_from_yahoo(self):
        """Robust download method compatible with new yfinance versions"""
        
        # 1. Read ticker
        
        #ticker = self.data_collection.text().strip().upper()
        tickers_text = self.data_collection.text().strip().upper()
        if not tickers_text:
            QtWidgets.QMessageBox.warning(self, "Error", "Please enter a ticker symbol (e.g. AAPL)")
            return
        
        tickers = tickers_text.replace(',', ' ').split()
        unique_tickers = set(tickers)
        print(len(tickers))
        count = len(unique_tickers)
        if count > 1:
            QtWidgets.QMessageBox.warning(self,"The amount of tickers is more than 1"f' :{len(tickers)}', f'Using: {tickers[0]}')

        try:
            print(f"--- Starting download for: {tickers[0]} ---")

            # 2. Download
            df = yf.download(tickers[0], period="1y", interval="1d", progress=False, auto_adjust=True)

            print("Download completed by yfinance.")
            print(f"Data dimensions: {df.shape}")

            if df.empty:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Error",
                    f"No data found for {tickers[0]}. Check spelling or internet connection."
                )
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

            QtWidgets.QMessageBox.information(self, "Success", f"Downloaded {len(prices)} days for {tickers[0]}")
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

        if not file_path:
            return  # User cancelled

        self.csv_txt_input.setText(file_path)

        try:
            # -------------------------------------------------------
            # CASE A: NumPy (.npy)
            # -------------------------------------------------------
            if file_path.endswith('.npy'):
                self.data = np.load(file_path, allow_pickle=True)

                # Attempt to extract price column
                raw_prices = self.data[:, 1].astype(str)

            # -------------------------------------------------------
            # CASE B: CSV / Excel
            # -------------------------------------------------------
            else:
                if file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                    df = pd.read_excel(file_path)
                else:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "Invalid Format",
                        f"The selected file does not have the correct format. Please try again with another file"
                    )
                    self.data = None
                    self.btn_execute.setEnabled(False)
                
                # Select price column
                if 'Close' in df.columns:
                    raw_prices = df['Close'].astype(str).values
                elif 'Adj Close' in df.columns:
                    raw_prices = df['Adj Close'].astype(str).values
                elif len(df.columns) > 1:
                    raw_prices = df.iloc[:, 1].astype(str).values
                else:
                    raw_prices = df.iloc[:, 0].astype(str).values

            # -------------------------------------------------------
            # STEP 1 — Detect invalid (non-numeric) values
            # -------------------------------------------------------
            invalid_indices = []
            clean_prices = []

            for i, val in enumerate(raw_prices):
                try:
                    clean_prices.append(float(val))
                except ValueError:
                    invalid_indices.append(i)
                    clean_prices.append(np.nan)

            clean_prices = np.array(clean_prices, dtype=float)

            # If invalid (text) values exist → ask user
            if len(invalid_indices) > 0:
                msg = QtWidgets.QMessageBox(self)
                msg.setWindowTitle("Invalid Values Detected")
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText(
                    "The file contains invalid (non-numeric) values in these rows:\n"
                    f"{[i + 1 for i in invalid_indices]}\n\n"
                    "What would you like to do?"
                )

                btn_delete = msg.addButton("Delete these rows", QtWidgets.QMessageBox.AcceptRole)
                btn_fill = msg.addButton("Replace with 0", QtWidgets.QMessageBox.ActionRole)
                btn_cancel = msg.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)

                msg.exec_()
                clicked = msg.clickedButton()

                keep_zeros = self.get_checkbox_value()

                if clicked == btn_cancel:
                    self.data = None
                    self.btn_execute.setEnabled(False)
                    return

                elif clicked == btn_delete:
                    clean_prices,_ = calcs.clean_data(clean_prices, keep_zeros=keep_zeros)

                elif clicked == btn_fill:
                    clean_prices = np.nan_to_num(clean_prices, nan=0.0)

            prices = clean_prices

            # -------------------------------------------------------
            # STEP 2 — Detect NaN values (after cleaning text)
            # -------------------------------------------------------
            nan_rows = np.where(pd.isna(prices))[0]

            if len(nan_rows) > 0:
                msg = QtWidgets.QMessageBox(self)
                msg.setWindowTitle("Missing Values Detected")
                msg.setIcon(QtWidgets.QMessageBox.Warning)

                msg.setText(
                    f"The file contains missing values (NaN) in these rows:\n"
                    f"{(nan_rows + 1).tolist()}\n\n"
                    "What would you like to do?"
                )

                btn_delete = msg.addButton("Delete rows", QtWidgets.QMessageBox.AcceptRole)
                btn_fill = msg.addButton("Fill with 0", QtWidgets.QMessageBox.ActionRole)
                btn_cancel = msg.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)

                msg.exec_()
                clicked = msg.clickedButton()

                keep_zeros = self.get_checkbox_value()

                if clicked == btn_cancel:
                    self.data = None
                    self.btn_execute.setEnabled(False)
                    return

                elif clicked == btn_delete:
                    prices,_ = calcs.clean_data(prices,keep_zeros=keep_zeros)

                elif clicked == btn_fill:
                    prices = np.nan_to_num(prices, nan=0.0)

            # -------------------------------------------------------
            # Step 3 — Build final numeric data structure
            # -------------------------------------------------------
            indices = np.arange(len(prices))
            self.data = np.column_stack((indices, prices))

            print(f"File loaded successfully: {file_path}")
            self.btn_execute.setEnabled(True)

        except Exception as e:
            print(f"Error loading file: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Could not read file: {str(e)}")

    def execute_script(self):
        # Original logic intact

        keep_zeros = self.get_checkbox_value()

        if self.data is not None:
            data_col = self.data[:, 1:2]

            self.my_data,_ = calcs.clean_data(data = data_col, keep_zeros=keep_zeros)

            try:
                # Get text from input fields
                lookbackField = int(self.loockback_txtField.text())
                multiplierField = float(self.multiplier_txtField.text())

            except ValueError:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Please enter valid numbers. Lookback must be an integer."
                )
                return

            # Validate positive values
            if lookbackField <= 0:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Invalid Lookback",
                    "Lookback must be a positive integer."
                )
                return

            if multiplierField < 0:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Invalid Multiplier",
                    "Multiplier must be zero or positive."
                )
                return

            # Call your calculation module
            self.labels, self.upper, self.bottom, boundaries = calcs.calculations(
                data=data_col,
                lookback_period=lookbackField,
                std_multiplier=multiplierField
            )

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
            self.canvas.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
            self.plot_view_result.layout().addWidget(self.canvas)

            self.toolbar = NavigationToolbar(self.canvas, self)
            self.plot_view_result.layout().addWidget(self.toolbar)

            self.original_data_col = data_col
            self.original_labels = self.labels

            self.plot_data(self.original_data_col, self.original_labels, boundaries)
            self.btn_export.setEnabled(True)

    def execute_kalman_script(self):
        # Original logic intact

        keep_zeros = self.get_checkbox_value()

        if self.data is not None:
            data_col = self.data[:, 1:2]

            self.my_data,_ = calcs.clean_data(data = data_col, keep_zeros=keep_zeros)

            try:
                # Get text from input fields
                outl_thresh = int(self.outlier_txtField.text())
                pr_noise = int(self.loockback_txtField.text())
                meas_noise = float(self.multiplier_txtField.text())

            except ValueError:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Please enter valid numbers. Lookback must be an integer."
                )
                return

            # Validate positive values
            if outl_thresh <= 0:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Invalid Outlier Threshold",
                    "Outlier Threshold must be a positive integer."
                )
                return

            if pr_noise <= 0:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Invalid Lookback",
                    "Lookback must be a positive integer."
                )
                return

            if meas_noise < 0:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Invalid Multiplier",
                    "Multiplier must be zero or positive."
                )
                return

            # Call your calculation module
            self.labels, self.upper, self.bottom, boundaries = calcs.kalman_filters(
                data=data_col,
                outlier_threshold=outl_thresh,
                process_noise=pr_noise, 
                measurement_noise=meas_noise
            )

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
            self.canvas.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
            self.plot_view_result.layout().addWidget(self.canvas)

            self.toolbar = NavigationToolbar(self.canvas, self)
            self.plot_view_result.layout().addWidget(self.toolbar)

            self.original_data_col = data_col
            self.original_labels = self.labels

            self.plot_data(self.original_data_col, self.original_labels, boundaries)
            self.btn_export.setEnabled(True)

    def plot_data(self, data_col, labels, boundaries):
        """Helper function to plot the financial line chart with outlier alerts"""
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        x_data = np.arange(len(data_col))

        # 1. PLOT PRICE LINE (Trend)
        ax.plot(x_data, data_col, color='#1f77b4', linewidth=1.5, label='Price History', alpha=0.8)

        # Plot boundaries
        if boundaries == True:
            ax.plot(x_data,self.upper, color='#32CD32', linewidth=1, label='Upper boundary', alpha=0.4)
            ax.plot(x_data,self.bottom, color='#e10000', linewidth=1, label='Bottom boundary', alpha=0.4)
        
        # 2. PLOT ONLY OUTLIERS (Red Points)
        outlier_mask = labels.flatten() == 1

        if np.any(outlier_mask):
            ax.scatter(
                x_data[outlier_mask],
                data_col[outlier_mask],
                color='red',
                s=60,
                edgecolor='black',
                label='Anomaly / Outlier',
                zorder=5
            )

        # 3. FINANCIAL STYLING
        ax.set_title("Price Evolution & Anomaly Detection")
        ax.set_ylabel("Price ($)")
        ax.set_xlabel("Time (Days)")

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