import pandas as pd
import numpy as np
import os

def generate_dummy_data(num_batches=500):
    print(f"Generating {num_batches} synthetic batch records...")
    np.random.seed(42)
    
    data = {
        "Batch_ID": [f"BATCH_{str(i).zfill(4)}" for i in range(1, num_batches + 1)],
        "Batch_Date": pd.date_range(start="2025-01-01", periods=num_batches, freq="D"),
        "Equipment_ID": np.random.choice(["RX-101", "RX-102", "RX-103", "RX-104"], num_batches),
        "Reagent_Active_Purity": np.random.uniform(95.0, 99.5, num_batches),
        "Reaction_Temp": np.random.normal(73.5, 2.0, num_batches),
        "Cooling_Rate": np.random.normal(0.65, 0.15, num_batches),
        "Yield": np.random.normal(85.0, 5.0, num_batches),
        "Cycle_Time": np.random.normal(48.0, 4.0, num_batches),
        "Impurity_A": np.random.uniform(0.01, 0.5, num_batches),
        "Impurity_B": np.random.uniform(0.01, 0.5, num_batches),
        "Impurity_C": np.random.uniform(0.01, 0.5, num_batches),
    }
    
    df = pd.DataFrame(data)
    df["Total_Impurity"] = df["Impurity_A"] + df["Impurity_B"] + df["Impurity_C"]
    
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
    file_path = os.path.join(os.path.dirname(__file__), "..", "data", "pharma_batches.xlsx")
    df.to_excel(file_path, index=False)
    print(f"Data saved to {file_path}")

if __name__ == "__main__":
    generate_dummy_data()
