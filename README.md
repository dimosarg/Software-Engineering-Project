# 📈 Financial Outlier Detection System

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green) ![License](https://img.shields.io/badge/License-MIT-lightgrey)

A desktop application designed to analyze financial time-series data and automatically detect statistical outliers (anomalies). Built with **Python** and **PyQt5**, this tool allows traders and analysts to visualize price trends and spot irregularities using Yahoo Finance data or local datasets.

## 🚀 Features

* **Dual Input Methods:**
    * **Live Data:** Download real-time historical data directly from Yahoo Finance (e.g., AAPL, TSLA).
    * **Local Files:** Support for `.csv`, `.xlsx`, `.xls`, and `.npy` files.
* **Visual Analysis:** Interactive **Matplotlib** integration to display price history trends.
* **Anomaly Detection:** Automatically highlights statistical outliers in **Red** for instant identification.
* **Export Capabilities:** Save your analysis graphs as high-quality PNG images.
* **User-Friendly Interface:** Clean GUI built with PyQt5.

---

## 📥 How to Install & Run

### Method 1: The Easy Way (No Python Required)
If you just want to use the app without installing anything:
1. Go to the **[Releases](../../releases)** page of this repository.
2. Download the latest `main.exe` file.
3. Double-click to run. (Note: Windows may flag it as "Unverified"—this is normal for new apps. Click "More Info" > "Run Anyway").

### Method 2: For Developers (Run from Source)
If you want to modify the code or run it via Python:

#### 1. Prerequisites
Ensure you have [Python 3.8+](https://www.python.org/downloads/) installed.

#### 2. Clone the Repository
```bash
git clone [https://github.com/YourUsername/YourRepoName.git](https://github.com/YourUsername/YourRepoName.git)
cd YourRepoName
