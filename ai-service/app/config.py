import os

MODEL_DIR = os.environ.get("MODEL_DIR", "/app/models")
DISEASE_MODEL_PATH = os.path.join(MODEL_DIR, "disease_model.onnx")
IRRIGATION_MODEL_PATH = os.path.join(MODEL_DIR, "irrigation_model.pkl")
MODEL_VERSION = os.environ.get("MODEL_VERSION", "1.0.0")
