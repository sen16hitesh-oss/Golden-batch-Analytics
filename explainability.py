import xgboost as xgb
import shap
import pandas as pd
import numpy as np

class ExplainabilityEngine:
    def __init__(self, target_col="Total_Impurity"):
        self.model = xgb.XGBRegressor(objective="reg:squarederror", random_state=42)
        self.target_col = target_col
        self.explainer = None
        self.features = None

    def train_model(self, df: pd.DataFrame, feature_cols: list):
        self.features = feature_cols
        X = df[feature_cols]
        y = df[self.target_col]
        self.model.fit(X, y)
        self.explainer = shap.Explainer(self.model)

    def get_global_prioritization(self, df: pd.DataFrame) -> dict:
        if not self.explainer:
            return {"error": "Model not trained yet."}
        X = df[self.features]
        shap_values = self.explainer(X)
        mean_shap = np.abs(shap_values.values).mean(axis=0)
        importance_dict = dict(zip(self.features, mean_shap))
        return dict(sorted(importance_dict.items(), key=lambda item: item[1], reverse=True))
