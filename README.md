# KPI-Forge-AI-Driven-Batch-KPI-Dashboard-Software
# 📊 KPI Forge: AI-Driven Batch KPI Dashboard

This project was completed as part of a test assignment. It automates batch-wise KPI calculations using purchase, production, and target cost data, and presents results through an intelligent, user-friendly Streamlit dashboard.

------

## 📁 Files Included

- `app.py` – Streamlit dashboard application  
- `cleaned_kpi_output.csv` – Output of cleaned and merged data  
- `README.md` – This documentation

---

## 🧾 Project Objective

To build a smart dashboard that automates:

1. Cleaning and merging Excel files (purchase, production, KPI targets)  
2. Calculating:  
   - Total raw material cost  
   - Cost per unit  
   - Variance against target  
3. Flagging batches with variance beyond ±10%  
4. Enabling AI-style natural language search (e.g., "cost/unit > 80 in April")  
5. Presenting results visually with charts and filters

---

## 🔧 Technologies Used

- **Python 3**  
- **Pandas** – data processing  
- **Streamlit** – interactive dashboard  
- **Regex** – for interpreting natural language queries  
- **Matplotlib / Plotly** – for data visualization

---

## ✅ What We Built

- Cleaned and merged data from three Excel files using `Batch_ID`  
- Calculated core KPIs and flagged variance  
- Developed AI-style search that accepts queries like:  
  - `Show batches with high variance in March`  
  - `Cost/unit between 50 and 80 in April`  
- Built a fully interactive dashboard using Streamlit  
- Added support for:  
  - File uploads  
  - Query inputs  
  - Visual charts (bar, line, pie)  
  - Filtered data download

---

## 📊 Dashboard Features

- 📥 Upload 3 Excel files (`purchase`, `production`, `kpi_reference`)  
- 📋 View full KPI table with computed columns  
- 🔍 Use GPT-style query box to search using natural language  
- 📈 Visualizations:  
  - Bar chart: Cost/Unit by Batch  
  - Line chart: Variance % by Batch  
  - Pie chart: Variance Flag distribution  
- 📤 Download cleaned or filtered results as CSV

---

## 🚀 How to Run

1. Install required libraries:
   ```bash
   pip install streamlit pandas openpyxl
   ```

2. Run the dashboard:
   ```bash
   streamlit run app.py
   ```

3. Upload the required Excel files and interact with the dashboard.

---

## 📌 Assumptions

- `Batch_ID` is the primary key across all datasets  
- Cost per unit = Total Raw Material Cost / Output Units  
- Variance beyond ±10% is flagged as "High Variance"

------

## 🧠 Optional Improvements

- Integrate OpenAI API for enhanced query understanding  
- Add PDF/Excel export for reports  
- Set up scheduled reporting with alert system

---

## 👨‍💻 Author

**Vishal Yadav**  
Role: Data & Automation Developer  
Project: AI-Driven KPI Dashboard (Test Assignment)

---
