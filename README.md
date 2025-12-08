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

## 📦 Installation & Setup

### 1. Prerequisites
Ensure you have Python 3.8 or higher installed on your system.

### 2. Install Dependencies
You need to install the required Python libraries to run the application. Open your terminal or command prompt and run:

```bash
pip install numpy pandas yfinance PyQt5 matplotlib openpyxl
