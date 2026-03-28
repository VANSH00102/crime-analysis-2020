# 🔍 Indian Crime Data Analysis 2020

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?style=flat&logo=flask)
![Pandas](https://img.shields.io/badge/Pandas-2.x-green?style=flat&logo=pandas)
![JavaScript](https://img.shields.io/badge/JavaScript-Vanilla-yellow?style=flat&logo=javascript)

A complete full-stack Data Science project analyzing India's 2020 crime statistics — built with **Python (Flask + Pandas + Seaborn + Matplotlib)** on the backend and **HTML / CSS / Vanilla JS** on the frontend.

---

## 🌐 Live Preview

> Run locally — see setup instructions below.

---

## 📸 Screenshots

### Home Page
![Home](https://via.placeholder.com/900x400/0D1117/C0392B?text=Home+Page)

### Dashboard
![Dashboard](https://via.placeholder.com/900x400/0D1117/C0392B?text=Dashboard)

### Visualizations
![Charts](https://via.placeholder.com/900x400/0D1117/C0392B?text=8+Charts+Generated)

---

## 📁 Project Structure
```
crime_project/
│
├── backend/
│   ├── app.py               ← Flask REST API (7 endpoints)
│   ├── analysis.py          ← Data preprocessing + 8 chart generators
│   ├── requirements.txt     ← Python dependencies
│   ├── data/
│   │   └── crime_data_2020.csv   ← 280 records (28 states × 10 crimes)
│   └── outputs/             ← Auto-generated PNG charts saved here
│
├── frontend/
│   ├── index.html           ← Home / Landing page
│   ├── dashboard.html       ← Live KPI dashboard
│   ├── data.html            ← Interactive filterable data table
│   ├── visualizations.html  ← Chart gallery with lightbox
│   ├── analysis.html        ← Trigger analysis pipeline
│   ├── style.css            ← Dark theme responsive styles
│   └── script.js            ← Shared utilities + API calls
│
└── README.md
```

---

## ⚡ How to Run Locally

### Step 1 — Install dependencies
```bash
cd backend
conda install pandas numpy matplotlib seaborn -y
pip install flask --prefer-binary
```

### Step 2 — Start Flask backend
```bash
python app.py
```
Server starts at → `http://localhost:5001`

### Step 3 — Start frontend (new terminal tab)
```bash
cd frontend
python3 -m http.server 8081
```

### Step 4 — Open browser
```
http://localhost:8081
```

### Step 5 — Generate charts
Click **Analysis** in navbar → Click **▶ Run Full Analysis**

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/data` | Full dataset as JSON |
| GET | `/stats` | Key statistics & insights |
| GET | `/visualizations` | List of chart images |
| POST | `/run-analysis` | Run full pipeline |
| GET | `/image/<filename>` | Serve chart PNG |
| GET | `/states` | All states list |
| GET | `/state/<name>` | State-specific analysis |

---

## 📊 Dataset

**Source:** Modelled on NCRB (National Crime Records Bureau) 2020  
**Records:** 280 rows — 28 States × 10 Crime Types

| Column | Description |
|--------|-------------|
| State_UT | Indian State or Union Territory |
| Crime_Type | IPC crime category |
| Cases_Registered | Total FIRs filed in 2020 |
| Cases_Chargesheeted | Cases taken to court |
| Cases_Convicted | Cases resulting in conviction |
| Persons_Arrested | Total persons arrested |
| Crime_Rate | Cases per lakh population |

**Crime Types:** Murder, Rape, Kidnapping & Abduction, Robbery, Burglary, Theft, Riots, Cheating, Counterfeiting, Criminal Breach of Trust

---

## 📈 Visualizations (8 Charts)

| # | Chart | Type |
|---|-------|------|
| 1 | Top 10 States by Cases | Horizontal Bar |
| 2 | Crime Type Distribution | Pie Chart |
| 3 | Major Crimes – Top 5 States | Grouped Bar |
| 4 | Crime Rate Heatmap | Heatmap |
| 5 | Conviction Rate by Crime | Horizontal Bar |
| 6 | State-wise Crime Rate | Vertical Bar |
| 7 | Arrests vs Cases | Scatter Plot |
| 8 | Crime Composition by State | Stacked Bar |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.x, Flask |
| Data Analysis | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Fonts | Google Fonts (Rajdhani, IBM Plex Mono, Inter) |

---

## ✅ Features

- 📊 Live KPI cards with animated counters
- 📋 Sortable & filterable data table with CSV export
- 🖼 Chart lightbox with keyboard navigation (← →)
- 📱 Fully responsive with mobile hamburger menu
- ⏳ Skeleton loading states
- 🔴 Graceful error handling on all pages
- 🌐 CORS-enabled REST API

---

## 👨‍💻 Author

**Vansh Goyal**  
📧 Connect on [GitHub](https://github.com/VANSH00102)

---

## 📄 License

This project is for academic/educational purposes.  
Data modelled on NCRB 2020 public report.
