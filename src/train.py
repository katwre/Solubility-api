# Training the final model
# Saving it to a file with pickle

# Core
import os
import pickle
# Data and math
import pandas as pd
# Modeling
from sklearn.model_selection import train_test_split, RandomizedSearchCV
# Regression model
from xgboost import XGBRegressor

# Set working directory (optional)
os.chdir("/home/katwre/projects/Solubility/")

# Load data
df = pd.read_csv('./data/Solubility_data-1.0/Descriptors/water_set_narrow_descriptors.csv')
X = df.drop(columns=["LogS", "SMILES", "StdInChIKey", "Train_test"])  # remove target + metadata
y = df["LogS"]

# Split to train and test datasets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# XGBoost model
xgb = XGBRegressor(
    objective="reg:squarederror",
    eval_metric="rmse",
    random_state=42
)

# Hyperparameter search space
param_dist = {
    "n_estimators": [300, 500, 800],
    "learning_rate": [0.01, 0.05, 0.1, 0.2],
    "max_depth": [3, 5, 7, 9],
    "subsample": [0.6, 0.8, 1.0],
    "colsample_bytree": [0.6, 0.8, 1.0],
    "reg_alpha": [0.0, 0.1, 1.0],  # L1
    "reg_lambda": [0.5, 1.0, 2.0], # L2
}

rs = RandomizedSearchCV(
    xgb,
    param_distributions=param_dist,
    n_iter=30,                  
    cv=3,
    scoring="neg_root_mean_squared_error",
    verbose=1,
    n_jobs=-1,
    random_state=42
)

# Fit
rs.fit(X_train, y_train)

# Final trained model
best_xgb = rs.best_estimator_

xgb_importance = pd.DataFrame({
    "feature": X.columns,
    "importance": best_xgb.feature_importances_
}).sort_values("importance", ascending=False)
xgb_importance.head(15)
# Reduce number of features by half with preserved predictive power (see the notebook)
top_features = xgb_importance.head(20)["feature"].tolist()

X_train_top = X_train[top_features]
X_test_top = X_test[top_features]

best_xgb.fit(X_train_top, y_train)

# predict on the reduced feature set
y_pred_top = best_xgb.predict(X_test_top)


# Save model to a pickle file
with open("models/xgboost_model.pkl", "wb") as f:
    pickle.dump((top_features, best_xgb), f)
