# AI Golden Batch Architecture Tool - Pharma API Optimization
Production repository layout for material-adaptive pharmaceutical analytical platforms.

## Run Stack Deployment
1. Initialize local tables: `psql -U postgres -f database/init.sql`
2. Populate tracking logs: `python scripts/generate_data.py`
3. Launch API frame layer: `uvicorn backend.app:app --port 8000`
4. Access UI terminal panel: `streamlit run frontend/dashboard.py --server.port 8501`
