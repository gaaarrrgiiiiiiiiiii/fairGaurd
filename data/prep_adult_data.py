import os
import pandas as pd
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
import joblib

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

def load_and_prep_data():
    print("Downloading Adult dataset...")
    data = fetch_openml(data_id=1590, as_frame=True, parser='auto')
    df = data.frame
    
    # Target is class (e.g. >50K or <=50K)
    y = df['class'].apply(lambda x: 1 if '>50K' in str(x) else 0)
    X = df.drop(columns=['class'])
    
    # Save the raw data for testing and local usage
    X.to_csv(os.path.join(DATA_DIR, 'adult_features.csv'), index=False)
    y.to_csv(os.path.join(DATA_DIR, 'adult_labels.csv'), index=False)
    
    print("Training biased baseline model...")
    # Define features
    categorical_features = ['workclass', 'education', 'marital-status', 'occupation', 'relationship', 'race', 'sex', 'native-country']
    numeric_features = ['age', 'fnlwgt', 'education-num', 'capital-gain', 'capital-loss', 'hours-per-week']
    
    # Only keep features that exist in the dataframe (some versions might have different names)
    categorical_features = [c for c in categorical_features if c in X.columns]
    numeric_features = [c for c in numeric_features if c in X.columns]

    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
        
    clf = Pipeline(steps=[('preprocessor', preprocessor),
                          ('classifier', LogisticRegression(max_iter=1000, random_state=42))])
                          
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    print(f"Model accuracy: {score:.3f}")
    
    model_path = os.path.join(DATA_DIR, 'biased_model.joblib')
    joblib.dump(clf, model_path)
    print(f"Model saved to {model_path}")
    
if __name__ == "__main__":
    load_and_prep_data()
