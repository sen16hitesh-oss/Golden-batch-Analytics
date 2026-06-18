import os
import random
import datetime
import pandas as pd
import psycopg2

def generate_historical_runs(num_batches=500):
    print(f"Generating {num_batches} synthetic runs with embedded multi-variable rules...")
    meta, tele = [], []
    base_date = datetime.datetime(2026, 1, 1, 8, 0, 0)
    
    for i in range(1, num_batches + 1):
        bid = f"BAT-2026-{i:03d}"
        purity = round(random.uniform(95.0, 99.5), 2)
        moisture = round(random.uniform(0.1, 1.5), 2)
        d50 = round(random.uniform(15.0, 45.0), 2)
        
        p_factor = (99.5 - purity) / 4.5
        m_factor = (moisture - 0.1) / 1.4
        
        impurity = round(max(0.01, 0.05 + (p_factor * 0.15) + random.uniform(-0.02, 0.02)), 3)
        yld = round(min(99.9, 82.0 + ((1.0 - p_factor) * 12.0) + random.uniform(-3.0, 3.0)), 2)
        cycle = round(12.0 + (m_factor * 6.5) + random.uniform(-0.5, 1.5), 2)
        
        meta.append({
            "batch_id": bid, "product_code": "API-PRIME-01", "start_time": base_date,
            "execution_type": "Historical", "reagent_purity": purity, "moisture_content": moisture,
            "particle_size_d50": d50, "final_impurity": impurity, "final_yield": yld, "final_cycle_time": cycle
        })
    
    df_m = pd.DataFrame(meta)
    os.makedirs("data", exist_ok=True)
    df_m.to_csv("data/batch_metadata_master.csv", index=False)
    df_m.to_excel("data/batch_metadata_master.xlsx", index=False)
    print("✓ Local sandbox sheets written to /data folder.")
    return df_m

if __name__ == "__main__":
    generate_historical_runs(500)
