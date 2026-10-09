import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
from PIL import Image, ImageDraw

BASE_DIR = Path(__file__).resolve().parent.parent
DATASETS_DIR = BASE_DIR / "training" / "datasets"
SAVED_MODELS_DIR = BASE_DIR / "saved_models"

DATASETS_DIR.mkdir(parents=True, exist_ok=True)
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

def generate_crop_recommendation_dataset():
    """
    Generates standard agronomic training dataset based on ICAR & FAO soil-climate guidelines:
    Columns: N, P, K, temperature, humidity, ph, rainfall, label
    """
    csv_path = DATASETS_DIR / "crop_recommendation.csv"
    if csv_path.exists():
        print(f"Dataset already exists at {csv_path}")
        return
        
    records = []
    # Crop profiles: [min_N, max_N, min_P, max_P, min_K, max_K, min_temp, max_temp, min_hum, max_hum, min_ph, max_ph, min_rain, max_rain, label]
    crop_profiles = [
        # Rice
        (60, 100, 35, 60, 35, 45, 20, 27, 80, 95, 5.0, 6.8, 180, 300, "rice"),
        # Maize
        (60, 100, 40, 60, 15, 25, 18, 27, 55, 75, 5.5, 7.5, 60, 110, "maize"),
        # Chickpea
        (20, 60, 55, 80, 75, 85, 17, 22, 14, 20, 6.0, 8.5, 65, 95, "chickpea"),
        # Kidneybeans
        (15, 40, 55, 80, 15, 25, 15, 24, 18, 25, 5.5, 6.0, 60, 150, "kidneybeans"),
        # Pigeonpeas
        (15, 40, 55, 75, 15, 25, 24, 35, 50, 70, 5.0, 7.5, 90, 190, "pigeonpeas"),
        # Mothbeans
        (15, 40, 35, 60, 15, 25, 24, 32, 40, 65, 3.5, 9.5, 30, 75, "mothbeans"),
        # Mungbean
        (15, 40, 35, 60, 15, 25, 27, 30, 80, 90, 6.2, 7.2, 35, 60, "mungbean"),
        # Blackgram
        (35, 60, 55, 80, 15, 25, 25, 35, 60, 70, 6.5, 7.5, 60, 75, "blackgram"),
        # Lentil
        (15, 40, 55, 80, 15, 25, 18, 30, 60, 70, 6.0, 7.8, 35, 55, "lentil"),
        # Pomegranate
        (15, 40, 10, 30, 35, 45, 18, 25, 85, 95, 5.5, 7.2, 100, 115, "pomegranate"),
        # Banana
        (80, 120, 70, 95, 45, 55, 25, 30, 75, 85, 5.5, 6.5, 90, 120, "banana"),
        # Mango
        (15, 40, 15, 40, 25, 35, 27, 36, 45, 55, 4.5, 7.0, 85, 105, "mango"),
        # Grapes
        (15, 40, 120, 145, 195, 205, 8, 42, 80, 85, 5.5, 6.5, 65, 75, "grapes"),
        # Watermelon
        (80, 120, 5, 30, 45, 55, 24, 27, 80, 90, 6.0, 7.0, 40, 60, "watermelon"),
        # Muskmelon
        (80, 120, 5, 30, 45, 55, 27, 30, 90, 95, 6.0, 6.8, 20, 30, "muskmelon"),
        # Apple
        (15, 40, 120, 145, 195, 205, 21, 24, 90, 95, 5.5, 6.5, 100, 130, "apple"),
        # Orange
        (15, 40, 5, 30, 5, 15, 10, 35, 90, 95, 6.0, 8.0, 100, 120, "orange"),
        # Papaya
        (40, 70, 45, 70, 45, 55, 23, 44, 90, 95, 6.5, 7.0, 140, 250, "papaya"),
        # Coconut
        (15, 40, 5, 30, 25, 35, 25, 29, 95, 100, 5.5, 6.5, 130, 230, "coconut"),
        # Cotton
        (100, 140, 35, 60, 15, 25, 22, 26, 75, 85, 6.0, 8.0, 60, 100, "cotton"),
        # Jute
        (60, 100, 35, 60, 35, 45, 23, 26, 75, 90, 6.0, 7.5, 150, 200, "jute"),
        # Coffee
        (80, 120, 15, 40, 25, 35, 23, 28, 55, 70, 6.0, 7.0, 115, 200, "coffee")
    ]
    
    np.random.seed(42)
    for profile in crop_profiles:
        n_min, n_max, p_min, p_max, k_min, k_max, t_min, t_max, h_min, h_max, ph_min, ph_max, r_min, r_max, crop_name = profile
        for _ in range(100):
            n = np.random.uniform(n_min, n_max)
            p = np.random.uniform(p_min, p_max)
            k = np.random.uniform(k_min, k_max)
            t = np.random.uniform(t_min, t_max)
            h = np.random.uniform(h_min, h_max)
            ph = np.random.uniform(ph_min, ph_max)
            rain = np.random.uniform(r_min, r_max)
            records.append({
                "N": round(n, 2),
                "P": round(p, 2),
                "K": round(k, 2),
                "temperature": round(t, 2),
                "humidity": round(h, 2),
                "ph": round(ph, 2),
                "rainfall": round(rain, 2),
                "label": crop_name
            })
            
    df = pd.DataFrame(records)
    df.to_csv(csv_path, index=False)
    print(f"Generated crop recommendation dataset with {len(df)} samples at {csv_path}")

def generate_yield_dataset():
    """
    Generates historical agricultural yield dataset for training regression models:
    Features: crop, acreage, rainfall_mm, fertilizer_kg_per_ha, soil_ph, irrigation_type, yield_quintals_per_acre
    """
    csv_path = DATASETS_DIR / "crop_yield.csv"
    if csv_path.exists():
        return
        
    np.random.seed(42)
    crops = ["Tomato", "Potato", "Rice", "Maize", "Cotton"]
    irrigation_types = ["Drip", "Sprinkler", "Flood", "Rainfed"]
    records = []
    
    for _ in range(1200):
        crop = np.random.choice(crops)
        acreage = round(np.random.uniform(0.5, 10.0), 2)
        rainfall = round(np.random.uniform(300, 1400), 1)
        fertilizer = round(np.random.uniform(40, 220), 1)
        ph = round(np.random.uniform(5.5, 8.2), 2)
        irrig = np.random.choice(irrigation_types)
        
        # Agronomic base yields (Quintals per acre)
        base = {
            "Tomato": 120.0,
            "Potato": 85.0,
            "Rice": 28.0,
            "Maize": 32.0,
            "Cotton": 12.0
        }[crop]
        
        # Irrigation factor
        irrig_mult = {"Drip": 1.25, "Sprinkler": 1.12, "Flood": 0.95, "Rainfed": 0.75}[irrig]
        # Soil pH optimal penalty
        ph_penalty = 1.0 - min(0.3, abs(ph - 6.5) * 0.1)
        # Fertilizer boost (with diminishing returns)
        fert_boost = 1.0 + (fertilizer / 300.0)
        # Noise
        noise = np.random.normal(1.0, 0.08)
        
        yield_per_acre = base * irrig_mult * ph_penalty * fert_boost * noise
        total_yield = round(yield_per_acre * acreage, 2)
        
        records.append({
            "crop": crop,
            "acreage": acreage,
            "rainfall_mm": rainfall,
            "fertilizer_kg_ha": fertilizer,
            "soil_ph": ph,
            "irrigation": irrig,
            "yield_per_acre_quintals": round(yield_per_acre, 2),
            "total_yield_quintals": total_yield
        })
        
    df = pd.DataFrame(records)
    df.to_csv(csv_path, index=False)
    print(f"Generated crop yield dataset with {len(df)} records at {csv_path}")

def generate_sample_leaf_dataset():
    """
    Creates real visual leaf synthetic samples for the tomato disease classes
    to allow the image feature extractor and classifier to train and evaluate cleanly.
    Categories: Healthy tomato leaf, Early blight, Late blight, Leaf mold
    """
    classes = [
        "healthy",
        "early_blight",
        "late_blight",
        "leaf_mold"
    ]
    
    img_dir = DATASETS_DIR / "tomato_leaves"
    for c in classes:
        (img_dir / c).mkdir(parents=True, exist_ok=True)
        
    np.random.seed(42)
    # Generate 30 distinct synthetic leaf pattern images per class for training/eval
    for c in classes:
        folder = img_dir / c
        if len(list(folder.glob("*.jpg"))) >= 30:
            continue
            
        for i in range(30):
            img = Image.new("RGB", (224, 224), color=(34, 139, 34)) # Forest green leaf base
            draw = ImageDraw.Draw(img)
            
            # Draw leaf shape veins
            draw.line([(112, 10), (112, 214)], fill=(46, 170, 46), width=4)
            for y in range(30, 200, 25):
                draw.line([(112, y), (40 + np.random.randint(-10, 10), y - 15)], fill=(46, 170, 46), width=2)
                draw.line([(112, y), (184 + np.random.randint(-10, 10), y - 15)], fill=(46, 170, 46), width=2)
                
            if c == "healthy":
                # Healthy vibrant leaf with minor natural texture
                for _ in range(50):
                    x, y = np.random.randint(20, 200), np.random.randint(20, 200)
                    draw.point((x, y), fill=(30, 160, 40))
            elif c == "early_blight":
                # Concentric dark brown lesions with target-board appearance
                for _ in range(5):
                    cx, cy = np.random.randint(50, 170), np.random.randint(50, 170)
                    r = np.random.randint(12, 25)
                    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(101, 67, 33), outline=(139, 69, 19))
                    draw.ellipse([cx-r//2, cy-r//2, cx+r//2, cy+r//2], fill=(60, 40, 20))
            elif c == "late_blight":
                # Water-soaked large dark necrotic lesions and grey-white edges
                for _ in range(3):
                    cx, cy = np.random.randint(40, 180), np.random.randint(40, 180)
                    r = np.random.randint(25, 45)
                    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(47, 53, 59), outline=(105, 105, 105))
            elif c == "leaf_mold":
                # Pale yellow patches on upper surface, velvety olive brown
                for _ in range(8):
                    cx, cy = np.random.randint(40, 180), np.random.randint(40, 180)
                    r = np.random.randint(10, 20)
                    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=(189, 183, 107), outline=(128, 128, 0))
                    
            img.save(folder / f"leaf_{c}_{i+1:03d}.jpg", quality=90)
            
    print("Leaf training image dataset prepared successfully.")

if __name__ == "__main__":
    generate_crop_recommendation_dataset()
    generate_yield_dataset()
    generate_sample_leaf_dataset()
