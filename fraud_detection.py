# This module is only for fraud detection logic. Chatbot logic is handled separately.
import numpy as np
import joblib

class FraudDetectionSystem:
    def __init__(self):
        self.model = None

    def load_model(self, model_path):
        self.model = joblib.load(model_path)

    def predict(self, X):
        if self.model is None:
            raise Exception("Model not loaded.")
        preds = self.model.predict(X)
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(X)[:, 1]
        else:
            probs = np.zeros(len(X))
        return preds, probs