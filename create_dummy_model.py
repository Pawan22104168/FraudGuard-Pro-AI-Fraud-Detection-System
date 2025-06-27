import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# Match the sample_transactions.csv structure: V1, V2, V3
columns = ['V1', 'V2', 'V3']
X = np.random.rand(100, 3)
y = np.random.randint(0, 2, 100)

# Train a simple model
model = RandomForestClassifier()
model.fit(X, y)

# Save the model
joblib.dump(model, 'fraud_detection_model.joblib')
print("Dummy model saved as fraud_detection_model.joblib (3 features: V1, V2, V3)") 