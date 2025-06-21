#Install Required Packages
#pip install streamlit pandas openpyxl
# pip install Pandas
# pip install streamlit
# pip install streamlit pandas openpyxl streamlit-extras
import pandas as pd
import streamlit as st
import re
from datetime import datetime
from streamlit_extras.dataframe_explorer import dataframe_explorer

st.set_page_config(page_title="KPI Forge Dashboard", layout="wide")

st.markdown("""
    <style>
        .centered-title {
            text-align: center;
            color: #4B8BBE;
            font-size: 36px;
        }
    </style>
    <div class="centered-title">📈 Fibre Bond KPI Dashboard</div>
""", unsafe_allow_html=True)

st.markdown("Upload the 3 Excel files to auto-process KPIs, run queries, and explore insights.")

# 📤 Upload files
purchase_file = st.file_uploader("Upload purchase_register.xlsx", type="xlsx")
production_file = st.file_uploader("Upload production_batchwise.xlsx", type="xlsx")
kpi_file = st.file_uploader("Upload kpi_reference.xlsx", type="xlsx")

if purchase_file and production_file and kpi_file:
    try:
        # 🔄 Load files
        purchase_df = pd.read_excel(purchase_file)
        production_df = pd.read_excel(production_file)
        kpi_df = pd.read_excel(kpi_file)

        # ✅ Part A: Cleaning & KPI Logic
        total_cost_per_batch = purchase_df.groupby("Batch_ID")["Total_Cost"].sum().reset_index()
        total_cost_per_batch.rename(columns={"Total_Cost": "Total_Raw_Material_Cost"}, inplace=True)

        merged_df = pd.merge(total_cost_per_batch, production_df, on="Batch_ID", how="inner")
        merged_df = pd.merge(merged_df, kpi_df, on="Batch_ID", how="inner")

        merged_df["Cost_Per_Unit"] = merged_df["Total_Raw_Material_Cost"] / merged_df["Output_Units"]
        merged_df["Variance_%"] = ((merged_df["Cost_Per_Unit"] - merged_df["Target_Cost_Per_Unit"]) / 
                                   merged_df["Target_Cost_Per_Unit"]) * 100
        merged_df["Variance_Flag"] = merged_df["Variance_%"].apply(
            lambda x: "High Variance" if abs(x) > 10 else "Within Range"
        )
        merged_df["Output_Date"] = pd.to_datetime(merged_df["Output_Date"])
        merged_df["Month"] = merged_df["Output_Date"].dt.strftime("%B")

        st.success("✅ Data loaded and KPIs calculated.")

        # 📊 Metric Summary
        col1, col2, col3 = st.columns(3)
        col1.metric("📦 Total Batches", len(merged_df))
        col2.metric("⚠️ High Variance", merged_df["Variance_Flag"].eq("High Variance").sum())
        col3.metric("💸 Avg Cost/Unit", f"{merged_df['Cost_Per_Unit'].mean():.2f}")

        st.markdown("---")
        chart_type = st.selectbox("📊 Select Chart Type", ["Bar Chart", "Line Chart"])

        if chart_type == "Bar Chart":
            st.bar_chart(merged_df.set_index("Batch_ID")["Cost_Per_Unit"])
        elif chart_type == "Line Chart":
            st.line_chart(merged_df.set_index("Batch_ID")["Variance_%"])
        # withou dropdown 2 chart which highly prefered
         # 📈 Charts
        st.subheader("📊 Visual KPI Insights")
        col4, col5 = st.columns(2)
        with col4:
            st.write("**Bar Chart: Cost per Unit by Batch**")
            st.bar_chart(merged_df.set_index("Batch_ID")["Cost_Per_Unit"])

        with col5:
            st.write("**Line Chart: Variance % by Batch**")
            st.line_chart(merged_df.set_index("Batch_ID")["Variance_%"])  
        st.markdown("---")
        with st.expander("🎛️ Apply Filter Conditions (Dropdown Style)"):
            col4, col5 = st.columns(2)

            with col4:
                cost_cond = st.selectbox("Cost/Unit Condition", [">", "<", ">=", "<=", "=="])
                cost_val = st.number_input("Cost/Unit Value", value=0.0)

            with col5:
                selected_month = st.selectbox("Month", ["All"] + sorted(merged_df["Month"].unique().tolist()))

            variance_range = st.slider("Variance % Range", 
                                       float(merged_df["Variance_%"].min()), 
                                       float(merged_df["Variance_%"].max()),
                                       (float(merged_df["Variance_%"].min()), float(merged_df["Variance_%"].max())))

            flag_filter = st.selectbox("Variance Flag", ["All", "High Variance", "Within Range"])

        filtered_df = merged_df.copy()
        if cost_val is not None:
            filtered_df = filtered_df.query(f"Cost_Per_Unit {cost_cond} @cost_val")
        if selected_month != "All":
            filtered_df = filtered_df[filtered_df["Month"] == selected_month]
        filtered_df = filtered_df[(filtered_df["Variance_%"] >= variance_range[0]) & 
                                  (filtered_df["Variance_%"] <= variance_range[1])]
        if flag_filter != "All":
            filtered_df = filtered_df[filtered_df["Variance_Flag"] == flag_filter]

        st.write("### 🧾 Search & Filtered Results (Interactive)")
        filtered_searchable_df = dataframe_explorer(filtered_df)
        st.dataframe(filtered_searchable_df, use_container_width=True)

        def filter_batches_by_query(query):
            df = merged_df.copy()
            query = query.lower()

            cost_match = re.search(r"cost/?unit\s*([<>=]=?|=)\s*(\d+(?:\.\d+)?)", query)
            if cost_match:
                op = cost_match.group(1)
                value = float(cost_match.group(2))
                if op in ["=", "=="]:
                    df = df[df["Cost_Per_Unit"] == value]
                else:
                    df = df.query(f"Cost_Per_Unit {op} @value")

            target_match = re.search(r"target.*between\s*(\d+(?:\.\d+)?)\s*to\s*(\d+(?:\.\d+)?)", query)
            if target_match:
                low = float(target_match.group(1))
                high = float(target_match.group(2))
                df = df[(df["Target_Cost_Per_Unit"] >= low) & (df["Target_Cost_Per_Unit"] <= high)]

            variance_match = re.search(r"variance.*between\s*(-?\d+(?:\.\d+)?)\s*to\s*(-?\d+(?:\.\d+)?)", query)
            if variance_match:
                low = float(variance_match.group(1))
                high = float(variance_match.group(2))
                df = df[(df["Variance_%"] >= low) & (df["Variance_%"] <= high)]

            month_match = re.search(r"(january|february|march|april|may|june|july|august|september|october|november|december)", query)
            if month_match:
                month = month_match.group(1).capitalize()
                df = df[df["Month"] == month]

            if "high variance" in query:
                df = df[df["Variance_Flag"] == "High Variance"]
            elif "within range" in query:
                df = df[df["Variance_Flag"] == "Within Range"]

            return df

        st.markdown("### 💬 Natural Language Query (Optional)")
        query = st.text_input("Type your query: e.g., cost/unit > 8 in April")
        if query:
            try:
                voice_result = filter_batches_by_query(query)
                if not voice_result.empty:
                    st.success(f"{len(voice_result)} matching result(s) found.")
                    st.dataframe(voice_result, use_container_width=True)
                else:
                    st.warning("No matching records found.")
            except Exception as e:
                st.error(f"❌ Query error: {e}")
# First checkbox for search result
        query = st.text_input("e.g., cost/unit > 8  in April")
        if query:
            result = filter_batches_by_query(query)
            if not result.empty:
                st.success(f"{len(result)} matching batch(es) found.")
                st.dataframe(result, use_container_width=True)
            else:
                st.warning("No matching records found.")

        # Second checkbox for search result
        query2 = st.text_input("Show batches with target cost between 70 to 90 in April")
        if query2:
            result = filter_batches_by_query(query2)
            if not result.empty:
                st.success(f"{len(result)} matching batch(es) found.")
                st.dataframe(result, use_container_width=True)
            else:
                st.warning("No matching records found.")    
        # Third checkbox for search result
        query3= st.text_input("Show batches with variance between -70 to -50 in April")
        if query3:
            result = filter_batches_by_query(query3)
            if not result.empty:
                st.success(f"{len(result)} matching batch(es) found.")
                st.dataframe(result, use_container_width=True)
            else:
                st.warning("No matching records found.")
        # Fourth checkbox for search result
        query4 = st.text_input("Batches with high variance in April")
        if query4:
            result = filter_batches_by_query(query4)
            if not result.empty:
                st.success(f"{len(result)} matching batch(es) found.")
                st.dataframe(result, use_container_width=True)
            else:
                st.warning("No matching records found.")
    except Exception as e:
        st.error(f"❌ Processing Error: {e}")
else:
    st.info("📎 Please upload all 3 Excel files to begin.")
