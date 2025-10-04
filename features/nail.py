# nail.py
import os
import io
import logging
import numpy as np
from PIL import Image

from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, session
from werkzeug.utils import secure_filename

from tensorflow import keras
from tensorflow.keras.applications.resnet50 import preprocess_input

nail_bp = Blueprint('nail', __name__, template_folder='../templates')

# ⚠️ Must exactly match the order used during training
NAIL_CLASSES = ["healthy", "onychomycosis", "psoriasis"]

# Lazy-loaded classifier
_nail_classifier = None


class NailDiseaseClassifier:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.classes = NAIL_CLASSES
        self.input_h, self.input_w = 224, 224
        self.model = self._load_model()
        # check if last layer already has softmax
        self.has_softmax = self._check_softmax()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Nail model not found: {self.model_path}")
        return keras.models.load_model(self.model_path, compile=False)

    def _check_softmax(self) -> bool:
        """Check if the last layer has softmax activation"""
        try:
            last_layer = self.model.layers[-1]
            if hasattr(last_layer, "activation") and last_layer.activation.__name__ == "softmax":
                return True
        except Exception:
            pass
        return False

    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        if image.mode != "RGB":
            image = image.convert("RGB")
        image = image.resize((self.input_w, self.input_h), Image.BILINEAR)
        arr = np.asarray(image).astype("float32")

        # Ensure 3 channels
        if arr.ndim == 2:
            arr = np.stack([arr] * 3, axis=-1)
        elif arr.shape[-1] == 4:
            arr = arr[..., :3]

        arr = preprocess_input(arr)
        return np.expand_dims(arr, axis=0)

    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        exp = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        return exp / np.sum(exp, axis=1, keepdims=True)

    def predict(self, image_bytes: bytes) -> dict:
        image = Image.open(io.BytesIO(image_bytes))
        input_tensor = self._preprocess_image(image)
        outputs = self.model.predict(input_tensor, verbose=0)

        # ✅ Apply softmax only if model doesn’t already have it
        probs = outputs if self.has_softmax else self._softmax(outputs)

        best_idx = int(np.argmax(probs[0]))
        return {
            "label": self.classes[best_idx],
            "probability": float(probs[0][best_idx])
        }


def _get_nail_classifier() -> NailDiseaseClassifier | None:
    global _nail_classifier
    if _nail_classifier is not None:
        return _nail_classifier

    models_dir = current_app.config.get("MODELS_DIR")
    if not models_dir:
        logging.error("MODELS_DIR not set in Flask config")
        return None

    model_file = os.path.join(models_dir, "best_nail_model.keras")
    if not os.path.exists(model_file):
        logging.error("Nail model file missing: %s", model_file)
        return None

    try:
        _nail_classifier = NailDiseaseClassifier(model_file)
        logging.info("Loaded nail model from %s (softmax=%s)", model_file, _nail_classifier.has_softmax)
        return _nail_classifier
    except Exception as e:
        logging.exception("Failed to load nail model: %s", e)
        return None


@nail_bp.route("/", methods=["GET"])
def upload():
    if not session.get("user_id"):
        return redirect("/login?next=/nail/")
    return render_template("nail.html")


@nail_bp.route("/predict", methods=["POST"])
def predict():
    if not session.get("user_id"):
        return redirect("/login?next=/nail/")

    file = request.files.get("image")
    if not file:
        flash("Please upload an image", "error")
        return redirect(url_for("nail.upload"))

    filename = secure_filename(file.filename or "")
    if not filename:
        flash("Invalid filename", "error")
        return redirect(url_for("nail.upload"))

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    save_path = os.path.join(upload_folder, filename)
    file.save(save_path)

    result = None
    clf = _get_nail_classifier()
    if clf is not None:
        try:
            with open(save_path, "rb") as f:
                img_bytes = f.read()
            pred = clf.predict(img_bytes)
            result = {
                "model": "best_nail_model.keras",
                "classes": clf.classes,
                "predicted": pred["label"].title(),
                "confidence": round(pred["probability"], 4),
            }
        except Exception as e:
            logging.exception("Prediction error: %s", e)
            flash("Prediction failed: " + str(e), "error")

    if result is None:
        flash("Nail model not available; showing demo output.", "info")
        result = {
            "model": "demo",
            "classes": NAIL_CLASSES,
            "predicted": "Healthy",
            "confidence": 0.88,
        }

    return render_template("nail.html", result=result, image_filename=filename)
