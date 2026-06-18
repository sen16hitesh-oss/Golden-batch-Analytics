# AI Golden Batch Optimization Tool
Robust multi-service pharmaceutical process manufacturing data validation workspace.

## Local Evaluation Startup Flow
1. Build local assets out: `python scripts/generate_data.py`
2. Run single container build locally: `docker build -t pharma-app . && docker run -p 8501:8501 pharma-app`
