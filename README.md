# 📈 OptionScope

### Professional Options Trading Analytics Dashboard

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white">
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white">
  <img src="https://img.shields.io/badge/Plotly-Visualization-3F4F75?style=for-the-badge&logo=plotly&logoColor=white">
  <img src="https://img.shields.io/badge/yFinance-Live%20Market-success?style=for-the-badge">
</p>

---

# 🚀 Overview

**OptionScope** is a professional options trading dashboard built using **Python** and **Streamlit**. It helps traders monitor positions, analyze portfolio performance, calculate option Greeks, manage trading risk, and visualize market insights—all from a single dashboard.

The application combines live market data, analytics, and trade management into an easy-to-use interface.

---

# ✨ Features

### 📡 Live Market Dashboard

* Live prices for NIFTY
* BANKNIFTY
* FINNIFTY
* SENSEX
* Auto refresh every 10 seconds

### 📒 Position Manager

* Add option positions
* Update premiums
* Delete trades
* Track OPEN and CLOSED positions
* Store trades using SQLite

### 📊 Trading Analytics

* Strategy-wise P&L analysis
* Portfolio exposure
* Net Profit & Loss
* Win Rate
* Equity Curve
* Export portfolio to CSV

### 📈 Greeks Calculator

Calculate:

* Delta
* Gamma
* Theta
* Vega
* Theoretical Option Price

using the **Black-Scholes Model**.

### 🛡 Risk Management

Monitor important trading metrics including:

* Maximum Loss
* Risk Reward Ratio
* Capital Utilization
* Portfolio Exposure

---

# 🛠 Tech Stack

## 💻 Languages

* Python

## 📚 Libraries

* Streamlit
* Pandas
* NumPy
* Plotly
* yFinance

## 🗄 Database

* SQLite

## 📈 Financial Concepts

* Black-Scholes Model
* Option Greeks
* Risk Management
* Portfolio Analytics

---

# ⚙ Project Workflow

```
📡 Live Market Data
          │
          ▼
   yFinance API
          │
          ▼
   Data Processing
          │
          ▼
 SQLite Database
          │
          ▼
 Portfolio Analytics
          │
          ▼
 Interactive Dashboard
```

---

# 📂 Project Structure

```
OptionScope
│
├── 📄 app.py
├── 📄 database.py
├── 📄 requirements.txt
├── 📄 options.db
├── 📁 assets
├── 📄 README.md
```

---

# 📊 Dashboard Modules

✅ Live Market Tracker

✅ Position Management

✅ Portfolio Dashboard

✅ Strategy Analytics

✅ Equity Curve

✅ Greeks Calculator

✅ Risk Manager

---

# 📸 Dashboard Preview

> *(Add screenshots here)*

Example:

```
assets/
    dashboard.png
    analytics.png
    greeks.png
```

Then use:

```markdown
![Dashboard](assets/dashboard.png)

![Analytics](assets/analytics.png)

![Greeks](assets/greeks.png)
```

---

# 🚀 Installation

```bash
git clone https://github.com/Narasimha2308/OptionScope.git

cd OptionScope

pip install -r requirements.txt

streamlit run app.py
```

---

# 🎯 Future Improvements

* 🔔 Price Alerts
* 📱 Mobile Responsive Dashboard
* ☁ Cloud Deployment
* 📊 More Trading Strategies
* 📈 Historical Performance Reports
* 🤖 AI-powered Trade Suggestions

---

# 👨‍💻 Author

### **Thulabandhu Narasimha**

🎓 B.Tech Computer Science Engineering (AI Minor)

**Skills**

* 🐍 Python
* 📊 Streamlit
* 📈 Plotly
* 🗄 SQLite
* 💹 Financial Analytics

---

## ⭐ If you found this project useful, consider giving it a star!
