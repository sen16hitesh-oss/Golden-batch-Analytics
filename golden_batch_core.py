import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI(title="Golden Batch Analytics Engine", host="127.0.0.1", port=8000)

class DatabaseManager:
    def __init__(self):
        self.connected = False
        self.in_memory_cache = {}

    def connect(self):
        try:
            self.connected = True
        except Exception:
            self.connected = False
            print("DB Timeout: Switching to local in-memory cache proxy.")

class ScoringEngine:
    @staticmethod
    def calculate_golden_score(df: pd.DataFrame) -> pd.DataFrame:
        min_yield, max_yield = df['Yield'].min(), df['Yield'].max()
        df['Yield_Score'] = ((df['Yield'] - min_yield) / (max_yield - min_yield)) * 100

        min_imp, max_imp = df['Total_Impurity'].min(), df['Total_Impurity'].max()
        df['Impurity_Score'] = ((max_imp - df['Total_Impurity']) / (max_imp - min_imp)) * 100

        min_cycle, max_cycle = df['Cycle_Time'].min(), df['Cycle_Time'].max()
        df['Cycle_Time_Score'] = ((max_cycle - df['Cycle_Time']) / (max_cycle - min_cycle)) * 100

        df['Golden_Score'] = (0.50 * df['Impurity_Score']) + \
                             (0.25 * df['Cycle_Time_Score']) + \
                             (0.25 * df['Yield_Score'])
        return df

    @staticmethod
    def isolate_golden_batches(df: pd.DataFrame) -> pd.DataFrame:
        df = ScoringEngine.calculate_golden_score(df)
        threshold = df['Golden_Score'].quantile(0.80)
        return df[df['Golden_Score'] >= threshold].sort_values(by='Golden_Score', ascending=False)

class CPPRecommender:
    PARAMETER_BOUNDS = {
        "Reaction_Temp": {"green": (72.0, 75.0), "red_low": 70.0, "red_high": 77.0},
        "Reactor_Pressure": {"green": (2.1, 2.5), "red_low": 1.8, "red_high": 2.9},
        "Process_pH": {"green": (6.2, 6.5), "red_low": 5.8, "red_high": 6.9},
        "Agitation_RPM": {"green": (180, 210), "red_low": 150, "red_high": 240},
        "Cooling_Rate": {"green": (0.5, 0.8), "red_low": 0.3, "red_high": 1.2}
    }

    @staticmethod
    def evaluate_parameter(param_name: str, value: float, starting_purity: float = 99.0) -> str:
        if param_name == "Cooling_Rate" and starting_purity < 97.0:
            return "RED (Dynamic Override: Constricted cooling due to low purity)"

        bounds = CPPRecommender.PARAMETER_BOUNDS.get(param_name)
        if not bounds:
            return "UNKNOWN"

        if bounds["green"][0] <= value <= bounds["green"][1]:
            return "GREEN ZONE (Optimal Window)"
        elif value < bounds["red_low"] or value > bounds["red_high"]:
            return "RED ZONE (Avoid Window)"
        else:
            return "AMBER ZONE (Caution Window)"

@app.post("/api/v1/score_batches")
async def score_batches(payload: dict):
    try:
        df = pd.DataFrame(payload['batches'])
        golden_df = ScoringEngine.isolate_golden_batches(df)
        return {"golden_batches": golden_df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    db = DatabaseManager()
    db.connect()
    uvicorn.run(app, host="127.0.0.1", port=8000)
