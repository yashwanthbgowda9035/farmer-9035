import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SAVED_MODELS_DIR = BASE_DIR / "saved_models"

def print_evaluation_summary():
    metrics_path = SAVED_MODELS_DIR / "tomato_metrics.json"
    if not metrics_path.exists():
        print("No evaluation metrics file found. Run training/train_classifier.py first.")
        return
        
    with open(metrics_path, "r") as f:
        data = json.load(f)
        
    print("=" * 60)
    print("KRISHIMITRA AI - TOMATO DISEASE MODEL EVALUATION METRICS")
    print("=" * 60)
    print(f"Overall Accuracy: {data['accuracy'] * 100:.2f}%\n")
    print("Per-Class Performance Report:")
    report = data["report"]
    for cls_name, vals in report.items():
        if isinstance(vals, dict):
            print(f" - {cls_name:<16}: Precision={vals['precision']:.2f}, Recall={vals['recall']:.2f}, F1-Score={vals['f1-score']:.2f}, Support={vals['support']}")
            
    print("\nConfusion Matrix:")
    for row in data["confusion_matrix"]:
        print("  ", row)
    print("=" * 60)

if __name__ == "__main__":
    print_evaluation_summary()
