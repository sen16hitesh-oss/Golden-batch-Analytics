import os
import datetime
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI(title="AI Golden Batch Ingestion Engine", version="1.2")

class SMECorridorOverride(BaseModel):
    parameter_name: str
    sme_manual_min: float
    sme_manual_max: float

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        port=int(os.getenv("DB_PORT", 5432)),
        cursor_factory=RealDictCursor
    )

@app.post("/api/upload")
async def upload_batch_data(file: UploadFile = File(...)):
    filename = file.filename
    try:
        if filename.endswith('.csv'): df = pd.read_csv(file.file)
        elif filename.endswith(('.xlsx', '.xls')): df = pd.read_excel(file.file)
        else: raise HTTPException(status_code=400, detail="Invalid format type layout.")
        
        conn = get_db_connection(); cur = conn.cursor()
        for _, row in df.iterrows():
            cur.execute("""INSERT INTO batch_metadata VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                   ON CONFLICT (batch_id) DO UPDATE SET reagent_purity=EXCLUDED.reagent_purity;""",
                (row['batch_id'], row['product_code'], datetime.datetime.now(), 'UserUpload',
                 float(row['reagent_purity']), float(row['moisture_content']), float(row['particle_size_d50']),
                 float(row.get('final_impurity', 0.05)), float(row.get('final_yield', 85.0)), float(row.get('final_cycle_time', 14.0))))
        conn.commit(); cur.close(); conn.close()
        return {"status": "Success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/compare")
async def get_analytical_comparison(batch_id: str = Query(...), mode: str = Query("AI")):
    try:
        conn = get_db_connection(); cur = conn.cursor()
        cur.execute("SELECT * FROM batch_metadata WHERE batch_id = %s;", (batch_id,))
        meta = cur.fetchone()
        if not meta: raise HTTPException(status_code=404, detail="Batch index missing.")
        
        cur.execute("SELECT * FROM golden_corridors;")
        corridors = {row['parameter_name']: row for row in cur.fetchall()}
        
        s_impurity = max(0, min(100, (0.35 - float(meta['final_impurity'])) / (0.35 - 0.01) * 100))
        s_yield = max(0, min(100, (float(meta['final_yield']) - 70.0) / (100.0 - 70.0) * 100))
        s_cycle = max(0, min(100, (24.0 - float(meta['final_cycle_time'])) / (24.0 - 10.0) * 100))
        composite_score = (0.50 * s_impurity) + (0.25 * s_yield) + (0.25 * s_cycle)
        
        purity_val = float(meta['reagent_purity'])
        cooling_min = float(corridors['cooling_rate']['ai_min'])
        cooling_max = float(corridors['cooling_rate']['ai_max'])
        if purity_val < 97.0:
            cooling_min -= 2.0; cooling_max -= 1.5
            
        if mode == "AI":
            active_bounds = {
                "internal_temp": {"min": float(corridors['internal_temp']['ai_min']), "max": float(corridors['internal_temp']['ai_max'])},
                "cooling_rate": {"min": cooling_min, "max": cooling_max}
            }
        else:
            active_bounds = {
                "internal_temp": {"min": float(corridors['internal_temp']['sme_manual_min']), "max": float(corridors['internal_temp']['sme_manual_max'])},
                "cooling_rate": {"min": float(corridors['cooling_rate']['sme_manual_min']), "max": float(corridors['cooling_rate']['sme_manual_max'])}
            }
        cur.close(); conn.close()
        return {
            "batch_id": batch_id, "evaluation_mode": mode,
            "cma_profile": {"purity": purity_val, "moisture": float(meta['moisture_content']), "particle_size_d50": float(meta['particle_size_d50'])},
            "scores": {"composite": round(composite_score, 2), "impurity_subscore": round(s_impurity, 2), "yield_subscore": round(s_yield, 2), "cycle_subscore": round(s_cycle, 2)},
            "active_bounds": active_bounds
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
