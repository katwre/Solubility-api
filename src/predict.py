# Loading the model
# Serving it via a web service with Flask

import pickle
import os
import pandas as pd

from pathlib import Path

from flask import Flask
from flask import request
from flask import jsonify


# Paths that work both locally and in Docker
HERE = Path(__file__).resolve().parent        # /app/src
PROJECT_ROOT = HERE.parent                    # /app
model_file = PROJECT_ROOT / "models/xgboost_model.pkl"
with open(model_file, 'rb') as f_in:
    FEATURES, MODEL = pickle.load(f_in)

app = Flask('solubility')

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.route('/predict', methods=['POST'])
def predict():

    data = request.get_json(force=True) or {}
    # Validate presence of features
    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": "missing_features", "missing": missing}), 400

    # Build a 1-row DataFrame in a fixed order and cast to float
    row = {f: float(data[f]) for f in FEATURES}
    X = pd.DataFrame([row], columns=FEATURES)

    predicted_solubility = MODEL.predict(X)
    soluble = predicted_solubility >= -2

    result = {
        'predicted_solubility': round(float(predicted_solubility),2),
        'soluble': bool(soluble)
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)