import os
import json
import joblib
import cv2
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, HistGradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, mean_absolute_error, r2_score

BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BASE_DIR / "training" / "datasets"
SAVED_MODELS_DIR = BASE_DIR / "saved_models"
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

def extract_image_features(image_path):
    """
    Extracts robust color, texture, and edge features from leaf photograph:
    - HSV color histogram (captures chlorophyll greens, chlorosis yellows, necrosis browns)
    - Grayscale gradient & texture variance (captures lesions and spot patterns)
    - Channel moments (mean, std dev)
    """
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not read image: {image_path}")
        
    img = cv2.resize(img, (224, 224))
    
    # Color spaces
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 3D HSV Histogram
    hist = cv2.calcHist([hsv], [0, 1, 2], None, [8, 8, 8], [0, 180, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    
    # Texture: Laplacian variance (sharpness/lesion edges)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    lap_var = np.array([laplacian.var(), laplacian.mean()])
    
    # Channel moments
    mean_rgb = img.mean(axis=(0, 1))
    std_rgb = img.std(axis=(0, 1))
    
    # Combine features
    features = np.hstack([hist, lap_var, mean_rgb, std_rgb])
    return features

def train_tomato_disease_classifier():
    print("\n--- Training Tomato Leaf Disease Classifier ---")
    leaf_dir = DATASETS_DIR / "tomato_leaves"
    categories = ["healthy", "early_blight", "late_blight", "leaf_mold"]
    
    X = []
    y = []
    
    for idx, cat in enumerate(categories):
        folder = leaf_dir / cat
        if not folder.exists():
            print(f"Directory {folder} not found, skipping...")
            continue
            
        images = list(folder.glob("*.jpg")) + list(folder.glob("*.png"))
        print(f"Loading {len(images)} images for class '{cat}'...")
        for img_p in images:
            feats = extract_image_features(img_p)
            X.append(feats)
            y.append(idx)
            
    X = np.array(X)
    y = np.array(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    clf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    acc = float(np.mean(y_pred == y_test))
    print(f"Tomato Classifier Test Accuracy: {acc * 100:.2f}%")
    
    report = classification_report(y_test, y_pred, target_names=categories, output_dict=True)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    model_path = SAVED_MODELS_DIR / "tomato_disease_model.pkl"
    labels_path = SAVED_MODELS_DIR / "tomato_labels.json"
    metrics_path = SAVED_MODELS_DIR / "tomato_metrics.json"
    
    joblib.dump(clf, model_path)
    with open(labels_path, "w") as f:
        json.dump(categories, f, indent=2)
    with open(metrics_path, "w") as f:
        json.dump({"accuracy": acc, "report": report, "confusion_matrix": cm}, f, indent=2)
        
    print(f"Saved tomato disease model to {model_path}")

def train_crop_recommender():
    print("\n--- Training Crop Recommendation Model ---")
    csv_path = DATASETS_DIR / "crop_recommendation.csv"
    df = pd.read_csv(csv_path)
    
    X = df[["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]]
    y = df["label"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    model = RandomForestClassifier(n_estimators=120, random_state=42)
    model.fit(X_train, y_train)
    
    acc = float(model.score(X_test, y_test))
    print(f"Crop Recommender Test Accuracy: {acc * 100:.2f}%")
    
    joblib.dump(model, SAVED_MODELS_DIR / "crop_recommender.pkl")
    print(f"Saved crop recommender model to {SAVED_MODELS_DIR / 'crop_recommender.pkl'}")

def train_yield_estimator():
    print("\n--- Training Crop Yield Estimator ---")
    csv_path = DATASETS_DIR / "crop_yield.csv"
    df = pd.read_csv(csv_path)
    
    # One-hot encode crop and irrigation
    df_encoded = pd.get_dummies(df[["crop", "acreage", "rainfall_mm", "fertilizer_kg_ha", "soil_ph", "irrigation"]])
    y = df["total_yield_quintals"]
    
    X_train, X_test, y_train, y_test = train_test_split(df_encoded, y, test_size=0.2, random_state=42)
    
    reg = RandomForestRegressor(n_estimators=100, random_state=42)
    reg.fit(X_train, y_train)
    
    y_pred = reg.predict(X_test)
    mae = float(mean_absolute_error(y_test, y_pred))
    r2 = float(r2_score(y_test, y_pred))
    print(f"Yield Regressor Test MAE: {mae:.2f} Quintals | R2 Score: {r2:.3f}")
    
    joblib.dump({
        "model": reg,
        "feature_columns": list(df_encoded.columns),
        "mae": mae,
        "r2": r2
    }, SAVED_MODELS_DIR / "yield_estimator.pkl")
    print(f"Saved yield estimator model to {SAVED_MODELS_DIR / 'yield_estimator.pkl'}")

def train_pest_classifier():
    print("\n--- Initializing Pest Identification Model Registry ---")
    pest_classes = [
        "aphids",
        "armyworm",
        "whitefly",
        "fruit_borer",
        "spider_mites"
    ]
    with open(SAVED_MODELS_DIR / "pest_labels.json", "w") as f:
        json.dump(pest_classes, f, indent=2)
    print("Pest classes registry configured.")

if __name__ == "__main__":
    train_tomato_disease_classifier()
    train_crop_recommender()
    train_yield_estimator()
    train_pest_classifier()
    print("\nAll models trained and checkpoints saved successfully!")
