import streamlit as st
import numpy as np
import plotly.graph_objects as go
import requests
import os

st.set_page_config(layout="wide", page_title="AI Golden Batch Dashboard")
API_BASE = os.getenv("API_URL", "http://localhost:8000")

st.title("Pharma API Optimization Control Tower")
st.markdown("---")

toggle_mode = st.radio("Global Operating Threshold Switcher:", ["AI Recommended Corridor (Adaptive)", "Manual SME Baselines Mode"], horizontal=True)
mode_param = "AI" if "AI Recommended" in toggle_mode else "Manual"

st.sidebar.header("Data Intake Layer")
uploaded_file = st.sidebar.file_uploader("Upload Run Profile Layout", type=["csv", "xlsx"])
if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    try:
        res = requests.post(f"{API_BASE}/api/upload", files=files)
        if res.status_code == 200: st.sidebar.success("File uploaded cleanly.")
        else: st.sidebar.error("Upload rejected.")
    except Exception as e: st.sidebar.error(f"Backend unreachable: {e}")

target_batch = st.sidebar.text_input("Active Target Batch Evaluation ID Reference:", "BAT-2026-001")

try:
    response = requests.get(f"{API_BASE}/api/analytics/compare?batch_id={target_batch}&mode={mode_param}")
    if response.status_code == 200:
        p = response.json()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Unified Performance Score", f"{p['scores']['composite']} / 100")
        c2.metric("Impurity Subscore", f"{p['scores']['impurity_subscore']}%")
        c3.metric("Yield Subscore", f"{p['scores']['yield_subscore']}%")
        c4.metric("Cycle Subscore", f"{p['scores']['cycle_subscore']}%")
        
        st.markdown("---")
        steps = [f"Step T+{x*30}m" for x in range(10)]
        np.random.seed(42)
        sim_temp = np.sin(np.linspace(0, 3, 10)) * 5 + 182.5 + np.random.normal(0, 0.5, 10)
        bounds = p["active_bounds"]["internal_temp"]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=steps, y=sim_temp, mode='lines+markers', name='Telemetry Trace Curve', line=dict(color='blue', width=3)))
        fig.add_trace(go.Scatter(x=steps, y=[bounds["max"]]*10, mode='lines', name='Upper Specification Limit', line=dict(color='red', dash='dash')))
        fig.add_trace(go.Scatter(x=steps, y=[bounds["min"]]*10, mode='lines', name='Lower Specification Limit', line=dict(color='green', dash='dash')))
        st.plotly_chart(fig, use_container_width=True)
    else: st.warning("Ensure data generation step has completed successfully.")
except Exception as e: st.error(f"Dashboard backend connection fault: {e}")
