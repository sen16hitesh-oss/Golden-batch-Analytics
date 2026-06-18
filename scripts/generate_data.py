import os
import random
import datetime
import pandas as pd
import psycopg2

def generate_synthetic_dataset(num_batches=500):
    print(f"Generating {num_batches} batches with embedded material constraints...")
    metadata_records = []
    telemetry_records = []
    start_base_date = datetime.datetime(2026, 1, 1, 8, 0, 0)
    
    for i in range(1, num_batches + 1):
        batch_id = f"BAT-2026-{i:03d}"
        product_code = "API-PRIME-01"
        batch_start = start_base_date + datetime.timedelta(days=(i - 1), hours=random.randint(0, 4))
        
        reagent_purity = round(random.uniform(95.0, 99.5), 2)
        moisture_content = round(random.uniform(0.1, 1.5), 2)
        particle_size_d50 = round(random.uniform(15.0, 45.0), 2)
        
        purity_factor = (99.5 - reagent_purity) / 4.5
        moisture_factor = (moisture_content - 0.1) / 1.4
        
        final_impurity = round(max(0.01, 0.05 + (purity_factor * 0.15) + random.uniform(-0.02, 0.02)), 3)
        final_yield = round(min(99.9, 82.0 + ((1.0 - purity_factor) * 12.0) + random.uniform(-3.0, 3.0)), 2)
        final_cycle_time = round(12.0 + (moisture_factor * 6.5) + random.uniform(-0.5, 1.5), 2)
        
        metadata_records.append({
            "batch_id": batch_id, "product_code": product_code, "start_time": batch_start,
            "execution_type": "Historical", "reagent_purity": reagent_purity,
            "moisture_content": moisture_content, "particle_size_d50": particle_size_d50,
            "final_impurity": final_impurity, "final_yield": final_yield, "final_cycle_time": final_cycle_time
        })
        
        phases = [
            ("Reaction", 4, {"temp": (170, 195), "press": (1.2, 3.5), "dose": (10, 50), "cool": 0, "seed": 0, "c_press": 0, "wash": 0, "vac": 0, "rpm": 0}),
            ("Crystallization", 4, {"temp": (50, 169), "press": (1.0, 1.2), "dose": 0, "cool": (10, 25), "seed": (45, 55), "c_press": 0, "wash": 0, "vac": 0, "rpm": 0}),
            ("Isolation", 4, {"temp": (20, 25), "press": (1.0, 1.1), "dose": 0, "cool": 0, "seed": 0, "c_press": (2.0, 4.5), "wash": (500, 1000), "vac": 0, "rpm": 0}),
            ("Drying", 4, {"temp": (40, 75), "press": (0.1, 0.5), "dose": 0, "cool": 0, "seed": 0, "c_press": 0, "wash": 0, "vac": (10, 50), "rpm": (20, 120)})
        ]
        
        current_time = batch_start
        for phase_name, steps, ranges in phases:
            for step in range(steps):
                current_time += datetime.timedelta(minutes=30)
                def get_val(r): return round(random.uniform(r[0], r[1]), 2) if isinstance(r, tuple) else r
                telemetry_records.append({
                    "batch_id": batch_id, "timestamp": current_time, "phase": phase_name,
                    "internal_temp": get_val(ranges["temp"]), "pressure": get_val(ranges["press"]),
                    "dosing_rate": get_val(ranges["dose"]), "cooling_rate": get_val(ranges["cool"]),
                    "seed_temp": get_val(ranges["seed"]), "cake_pressure": get_val(ranges["c_press"]),
                    "wash_volume": get_val(ranges["wash"]), "vacuum_level": get_val(ranges["vac"]),
                    "agitation_rpm": get_val(ranges["rpm"])
                })

    df_meta = pd.DataFrame(metadata_records)
    df_telemetry = pd.DataFrame(telemetry_records)
    
    os.makedirs("data", exist_ok=True)
    df_meta.to_csv("data/batch_metadata_master.csv", index=False)
    df_meta.to_excel("data/batch_metadata_master.xlsx", index=False)
    df_telemetry.to_csv("data/batch_telemetry_master.csv", index=False)
    print("✓ Data files generated successfully.")
    return df_meta, df_telemetry

def seed_database(df_meta, df_telemetry):
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "postgres"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "postgres"),
            port=int(os.getenv("DB_PORT", 5432))
        )
        cur = conn.cursor()
        for _, r in df_meta.iterrows():
            cur.execute("INSERT INTO batch_metadata VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING;",
                (r.batch_id, r.product_code, r.start_time, r.execution_type, r.reagent_purity, r.moisture_content, r.particle_size_d50, r.final_impurity, r.final_yield, r.final_cycle_time))
        for _, r in df_telemetry.iterrows():
            cur.execute("INSERT INTO batch_telemetry VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING;",
                (r.batch_id, r.timestamp, r.phase, r.internal_temp, r.pressure, r.dosing_rate, r.cooling_rate, r.seed_temp, r.cake_pressure, r.wash_volume, r.vacuum_level, r.agitation_rpm))
        conn.commit(); cur.close(); conn.close()
        print("✓ Database seeding complete.")
    except Exception as e:
        print(f"Skipping database write (PostgreSQL target not active local link): {e}")

if __name__ == "__main__":
    df_m, df_t = generate_synthetic_dataset(500)
    seed_database(df_m, df_t)
