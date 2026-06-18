import streamlit as st
import numpy as np
import plotly.graph_objects as go
import requests
import os

st.set_page_config(layout="wide", page_title="AI Golden Batch Control Tower")

# Environment-Aware Routing Layer: Targets inner container network interfaces securely
API_BASE = os.getenv("API_URL", "http://127.0.0.1:8000")

st.title("Pharma API Optimization Control Tower Dashboard")
st.markdown("---")

toggle_mode = st.radio(
    "Global Operating Threshold Evaluation Mode Context:",
    ["AI Recommended Corridor (Adaptive to Material Attributes)", "Manual SME Baselines Mode"],
    horizontal=True
)
mode_param = "AI" if "AI Recommended" in toggle_mode else "Manual"

st.sidebar.header("Data Management Portal")
uploaded_file = st.sidebar.file_uploader("Upload Manufacturing Run Sheet (.csv, .xlsx)", type=["csv", "xlsx"])

if uploaded_file is not None:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    try:
        res = requests.post(f"{API_BASE}/api/upload", files=files)
        if res.status_code == 200: st.sidebar.success("File verified and processed successfully.")
        else: st.sidebar.error("Data pipeline rejected format structures.")
    except Exception as e:
        st.sidebar.error(f"Backend network tracking link offline: {e}")

target_batch = st.sidebar.text_input("Active Target Tracking Batch ID Reference:", "BAT-2026-001")

try:
    response = requests.get(f"{API_BASE}/api/analytics/compare?batch_id={target_batch}&mode={mode_param}", timeout=4)
    if response.status_code == 200:
        p = response.json()
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Unified Performance Score", f"{p['scores']['composite']} / 100")
        c2.metric("Impurity Subscore Target", f"{p['scores']['impurity_subscore']}%")
        c3.metric("Yield Subscore Target", f"{p['scores']['yield_subscore']}%")
        c4.metric("Cycle Subscore Target", f"{p['scores']['cycle_subscore']}%")
        
        st.markdown("---")
        st.subheader("Process Trajectory Overlaid Against Active Operating Boundaries")
        
        steps = [f"Step T+{x*30}m" for x in range(10)]
        np.random.seed(42)
        sim_temp = np.sin(np.linspace(0, 3, 10)) * 5 + 182.5 + np.random.normal(0, 0.5, 10)
        bounds = p["active_bounds"]["internal_temp"]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=steps, y=sim_temp, mode='lines+markers', name='Telemetry Trace Curve', line=dict(color='blue', width=3)))
        fig.add_trace(go.Scatter(x=steps, y=[bounds["max"]]*10, mode='lines', name='Upper Envelope Boundary', line=dict(color='red', dash='dash')))
        fig.add_trace(go.Scatter(x=steps, y=[bounds["min"]]*10, mode='lines', name='Lower Envelope Boundary', line=dict(color='green', dash='dash')))
        
        fig.update_layout(xaxis_title="Telemetry Step Increments", yaxis_title="Rxn Internal Temperature (°C)", legend_orientation="h")
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"Associated Material Parameters Summary Context -> Reagent Active Purity: {p['cma_profile']['purity']}% | Moisture Content Fraction: {p['cma_profile']['moisture']}%")
    else:
        st.error("Analytics calculations returned an invalid response schema.")
except Exception as e:
    st.error(f"Dashboard backend connection fault: Could not communicate with FastAPI service layer on {API_BASE}. System details: {e}")
