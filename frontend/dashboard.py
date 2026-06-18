import streamlit as st
import pandas as pd
import os
import requests

st.set_page_config(page_title="Golden Batch Dashboard", layout="wide")
API_URL = "http://127.0.0.1:8000/api/v1/score_batches"

@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "..", "data", "pharma_batches.xlsx")
    if os.path.exists(file_path):
        return pd.read_excel(file_path)
    return pd.DataFrame()

df = load_data()
st.title("🧪 AI Golden Batch Analytics Platform")

if df.empty:
    st.warning("No data found. Please run dummy_data_generator.py first.")
    st.stop()

page = st.sidebar.radio("Navigation", ["Executive Summary", "Golden Batch Analytics", "CPP Recommendation Engine"])

if page == "Executive Summary":
    st.header("Executive Summary")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Batches", len(df))
    c2.metric("Average Yield", f"{df['Yield'].mean():.2f}%")
    c3.metric("Average Cycle Time", f"{df['Cycle_Time'].mean():.2f} hrs")
    c4.metric("Avg Total Impurity", f"{df['Total_Impurity'].mean():.2f}%")

elif page == "Golden Batch Analytics":
    st.header("Golden Batch Analytics")
    payload_df = df.copy()
    payload_df['Batch_Date'] = payload_df['Batch_Date'].astype(str)
    try:
        response = requests.post(API_URL, json={"batches": payload_df.to_dict(orient="records")})
        if response.status_code == 200:
            golden_batches = pd.DataFrame(response.json()["golden_batches"])
            st.success(f"Isolated Top {len(golden_batches)} Golden Batches!")
            st.dataframe(golden_batches[['Batch_ID', 'Yield', 'Cycle_Time', 'Total_Impurity', 'Golden_Score']].head(20))
    except:
        st.error("Could not connect to backend. Is golden_batch_core.py running?")

elif page == "CPP Recommendation Engine":
    st.header("CPP Traffic-Light Analysis")
    selected_batch = st.selectbox("Select Batch ID to Analyze", df['Batch_ID'].head(50))
    batch_data = df[df['Batch_ID'] == selected_batch].iloc[0]
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Reaction Temperature:** {batch_data['Reaction_Temp']:.2f} C")
    with c2:
        st.write(f"**Cooling Rate:** {batch_data['Cooling_Rate']:.2f} C/min")
        st.write(f"**Starting Purity context:** {batch_data['Reagent_Active_Purity']:.2f}%")
