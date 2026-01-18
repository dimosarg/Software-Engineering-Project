# 📈 Financial Outlier Detection System

A desktop application for detecting anomalies (outliers) in financial time-series data. The software allows users to load market data, apply different outlier detection methods, and visualize the results through an interactive graphical interface.

The system supports **two different outlier detection algorithms**:

* A **Standard Deviation–based method**
* A **Kalman Filter–based method**

The application is implemented in **Python** using **PyQt5** for the user interface and **Matplotlib** for visualization.

---

## 🚀 Main Features

* Load financial time-series data from:

  * Yahoo Finance (via ticker symbols)
  * Local files (`.csv`, `.xlsx`, `.xls`, `.npy`)
* Two outlier detection methods selectable from the interface
* Interactive visualization of price evolution and detected anomalies
* Robust handling of missing or invalid data
* Export plots as image files (`.png`)

---

## 🧠 Outlier Detection Methods

### 1. Standard Deviation–Based Method

This method uses rolling statistics to detect anomalies:

* A **lookback period** defines how many previous data points are used
* A **sensitivity multiplier** controls how strict the detection is

For each data point, the algorithm computes a dynamic upper and lower bound based on the rolling mean and standard deviation. Values outside these bounds are marked as outliers.

**Typical behavior:**

* Lower multiplier → more sensitive (more outliers)
* Higher multiplier → less sensitive (fewer outliers)

---

### 2. Kalman Filter–Based Method

The Kalman filter method estimates the expected value of the signal over time and compares incoming measurements to this estimate.

Outliers are detected when the deviation between the measured value and the estimated value exceeds a given threshold.

**Key characteristics:**

* More robust to noisy data
* Often reduces false positives
* Does not compute explicit upper/lower bounds

---

## 🖥️ How to Use the Application

### 1. Start the Program

You can run the program either from source code or as a compiled executable.

If running from source:

```bash
python main.py
```

Once started, the graphical interface will open.

---

### 2. Load Data

You have two options to load data:

#### Option A: Download from Yahoo Finance

1. Enter a ticker symbol (e.g. `AAPL`, `TSLA`) in the text field
2. Click **"Download Data"**
3. The program downloads one year of daily price data

#### Option B: Load a Local File

1. Click **"Load File"**
2. Select a file with one of the supported formats
3. The program automatically extracts the price column

If missing or invalid values are detected, the program will ask how to handle them.

---

### 3. Select the Outlier Detection Method

Use the dropdown menu to select the detection method:

* **STD based** → Standard deviation method
* **Kalman filters** → Kalman filter method

The meaning of the input fields depends on the selected method.

---

### 4. Set Parameters

#### For STD-Based Method:

* **Lookback**: Number of previous points used for statistics (integer > 0)
* **Multiplier**: Sensitivity of detection (float ≥ 0)

Example:

* Lookback = 14
* Multiplier = 2.5

#### For Kalman Filter Method:

* **Lookback field** → Measurement noise (integer ≥ 0)
* **Multiplier field** → Outlier threshold (float > 0)

Example:

* Measurement noise = 50
* Outlier threshold = 3.0

---

### 5. Execute Detection

1. Click **"Execute"**
2. The algorithm runs on the loaded data
3. Results are shown in the plot area

**Visualization:**

* Blue line: price evolution
* Red points: detected outliers
* (STD method only) upper and lower bounds are shown

---

### 6. Export Results

* Click **"Export"** to save the current plot as a PNG image

---

## ⚠️ Notes and Limitations

* Only one ticker is processed at a time when using Yahoo Finance
* Parameter values strongly affect detection results
* Kalman filter does not display statistical bounds

---

## 📦 Requirements

* Python 3.8+
* NumPy
* Pandas
* Matplotlib
* PyQt5
* yfinance

---

## 📄 License

This project is intended for academic purposes within the Software Engineering course.
