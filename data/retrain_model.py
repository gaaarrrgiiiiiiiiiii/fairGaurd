"""
Retrain the biased baseline model using existing CSV data.
Rebuilds biased_model.joblib with the current scikit-learn version.
Run from the backend directory:
    .\\venv\\Scripts\\python.exe ..\\data\\retrain_model.py
"""
import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
import joblib

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

FEAT_PATH  = os.path.join(DATA_DIR, "adult_features.csv")
LABL_PATH  = os.path.join(DATA_DIR, "adult_labels.csv")
MODEL_PATH = os.path.join(DATA_DIR, "biased_model.joblib")


def retrain():
    print("Loading existing dataset CSVs...")
    X = pd.read_csv(FEAT_PATH)
    y = pd.read_csv(LABL_PATH).squeeze()

    print(f"Dataset shape: {X.shape}, Labels: {y.value_counts().to_dict()}")

    categorical_features = [
        c for c in ["workclass", "education", "marital-status",
                     "occupation", "relationship", "race", "sex", "native-country"]
        if c in X.columns
    ]
    numeric_features = [
        c for c in ["age", "fnlwgt", "education-num",
                     "capital-gain", "capital-loss", "hours-per-week"]
        if c in X.columns
    ]

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    clf = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print("Training model...")
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    print(f"Model accuracy: {score:.3f}")

    joblib.dump(clf, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

    # Verify model loads and predicts correctly
    loaded = joblib.load(MODEL_PATH)
    sample = X_test.head(3)
    preds = loaded.predict_proba(sample)[:, 1]
    print(f"Sample predictions: {preds}")
    print("✅ Model retrained successfully with current scikit-learn version.")


if __name__ == "__main__":
    retrain()
