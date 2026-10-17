# COVID-19 Analytics Dashboard 📊

An interactive data analytics dashboard built using **Python, Dash, Pandas, and Plotly** to explore and visualize COVID-19 patient data.

## 📌 Project Overview

This project provides interactive visualizations to analyze COVID-19 patient records, understand patient status distributions, and explore trends across different age groups, genders, and states.

## ✨ Features

- **Patient Status Distribution:** Visualize patient status categories.
- **Daily Reported Records:** Analyze daily reporting trends.
- **Monthly Reported Records:** Explore monthly reporting patterns.
- **Age Group Analysis:** Understand the distribution of patients across age groups.
- **Gender Distribution:** Compare records by gender.
- **State-wise Patient Status Comparison:** Compare patient statuses across states.
- **State-wise Case Distribution:** Explore case distribution with an interactive status filter.
- **Interactive Visualizations:** Explore data using Plotly charts.

## 🛠️ Technologies Used

- Python
- Dash
- Pandas
- Plotly
- Gunicorn

## 📂 Project Structure

```text
covid-19-dashboard/
├── app.py
├── IndividualDetails.csv
├── requirements.txt
├── Procfile
└── README.md
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/covid-19-dashboard.git
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Navigate to the Project Folder

```bash
cd covid-19-dashboard
```

### 3. Create a Virtual Environment (Optional)

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Dashboard

```bash
python app.py
```

Open the local URL displayed in your terminal, usually:

`http://127.0.0.1:5000`

## 📊 Dataset

The dashboard uses `IndividualDetails.csv` to analyze COVID-19 patient records. The visualizations depend on the data available in the dataset.

## 🚀 Deployment

The application is designed to be deployable on a compatible Python web hosting platform using Gunicorn and the included dependency file.

## 🎯 Project Objective

The objective of this project is to practice data analysis, data visualization, and interactive dashboard development using Python.

## 👨‍💻 Author

**Mukesh Shah**

---

*This project is created for learning and educational purposes.*
