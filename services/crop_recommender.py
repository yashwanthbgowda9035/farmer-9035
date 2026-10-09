import joblib
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "saved_models" / "crop_recommender.pkl"

class CropRecommenderService:
    _instance = None
    _model = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        self._load_model()
        
    def _load_model(self):
        if MODEL_PATH.exists():
            try:
                self._model = joblib.load(MODEL_PATH)
            except Exception as e:
                print(f"Error loading crop recommender model: {e}")
                self._model = None
        else:
            self._model = None
            
    def is_configured(self):
        if self._model is None:
            self._load_model()
        return self._model is not None
        
    def recommend(self, n, p, k, temperature, humidity, ph, rainfall):
        if not self.is_configured():
            return {
                "status": "not_configured",
                "error": "Crop recommender model checkpoint (crop_recommender.pkl) not found. Run 'python training/train_classifier.py' to train the model."
            }
            
        # Validation of agronomic units
        if not (0 <= n <= 300 and 0 <= p <= 300 and 0 <= k <= 300):
            return {"status": "error", "error": "Nutrient values (N, P, K) must be between 0 and 300 kg/ha."}
        if not (0 <= temperature <= 55):
            return {"status": "error", "error": "Temperature must be between 0°C and 55°C."}
        if not (0 <= humidity <= 100):
            return {"status": "error", "error": "Relative humidity must be between 0% and 100%."}
        if not (3.0 <= ph <= 10.0):
            return {"status": "error", "error": "Soil pH must be between 3.0 and 10.0."}
        if not (0 <= rainfall <= 3000):
            return {"status": "error", "error": "Rainfall must be between 0 and 3000 mm."}
            
        features = np.array([[n, p, k, temperature, humidity, ph, rainfall]])
        probs = self._model.predict_proba(features)[0]
        classes = self._model.classes_
        
        # Rank predictions
        top_indices = np.argsort(probs)[::-1][:4]
        recommendations = []
        for idx in top_indices:
            crop_name = classes[idx].title()
            conf = float(probs[idx])
            if conf > 0.05:
                recommendations.append({
                    "crop": crop_name,
                    "confidence": round(conf * 100, 1),
                    "rationale": f"Optimal fit for soil N={n}, P={p}, K={k} with climate Temp={temperature}°C, RH={humidity}%, Rain={rainfall}mm."
                })
                
        return {
            "status": "success",
            "top_crop": recommendations[0]["crop"] if recommendations else "None",
            "recommendations": recommendations,
            "inputs": {
                "N": n, "P": p, "K": k,
                "temperature": temperature,
                "humidity": humidity,
                "ph": ph,
                "rainfall": rainfall
            },
            "model_type": "Supervised Random Forest Classifier (Trained on 2200 Agro-Climatic Records)",
            "limitations_notice": "Preliminary decision support recommendation. Field suitability also depends on local soil depth, water table, and market proximity. Verify with your district Krishi Vigyan Kendra."
        }

crop_recommender_service = CropRecommenderService.get_instance()
