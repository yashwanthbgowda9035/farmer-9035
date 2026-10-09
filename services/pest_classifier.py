import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SAVED_MODELS_DIR = BASE_DIR / "saved_models"

class PestClassifierService:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    def __init__(self):
        self.labels_path = SAVED_MODELS_DIR / "pest_labels.json"
        self.model_path = SAVED_MODELS_DIR / "pest_model.pkl"
        self._load_registry()
        
    def _load_registry(self):
        if self.labels_path.exists():
            with open(self.labels_path, "r") as f:
                self.supported_species = json.load(f)
        else:
            self.supported_species = ["aphids", "armyworm", "whitefly", "fruit_borer", "spider_mites"]
            
    def is_configured(self):
        # A separate dedicated pest visual model is required
        return self.model_path.exists()
        
    def get_supported_species(self):
        return [
            {"id": "aphids", "name": "Aphids (Aphis gossypii / Myzus persicae)", "target_crops": "Tomato, Cotton, Vegetables"},
            {"id": "armyworm", "name": "Fall Armyworm (Spodoptera frugiperda)", "target_crops": "Maize, Rice, Sorghum"},
            {"id": "whitefly", "name": "Silverleaf Whitefly (Bemisia tabaci)", "target_crops": "Tomato, Cotton, Chili"},
            {"id": "fruit_borer", "name": "Tomato Fruit Borer (Helicoverpa armigera)", "target_crops": "Tomato, Gram, Cotton"},
            {"id": "spider_mites", "name": "Two-Spotted Spider Mite (Tetranychus urticae)", "target_crops": "Vegetables, Fruit trees"}
        ]

    def predict(self, image_path):
        if not self.is_configured():
            return {
                "status": "not_configured",
                "error": "Dedicated Pest Vision Model checkpoint (pest_model.pkl) is not configured yet. The crop disease model cannot and will not be reused for insect identification to prevent invalid agronomic guidance.",
                "supported_species": self.get_supported_species(),
                "instructions": "Place labeled insect dataset under training/datasets/pests and train the dedicated pest classifier."
            }
            
        return {
            "status": "not_configured",
            "error": "Pest classification model is currently in standby registry mode."
        }

pest_classifier_service = PestClassifierService.get_instance()
