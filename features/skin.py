# skin.py
import os
import io
import logging
import numpy as np
from PIL import Image

from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, session
from werkzeug.utils import secure_filename

# Prefer TensorFlow Keras; fallback if needed
try:
    from tensorflow import keras
    from tensorflow.keras.applications.efficientnet import preprocess_input
except Exception:
    import keras  # type: ignore
    from keras.applications.efficientnet import preprocess_input  # type: ignore

skin_bp = Blueprint("skin", __name__, template_folder="../templates")

# Correct class names
SKIN_CLASSES = ["Normal", "SkinCancer", "Eczema", "Psoriasis"]

# Lazy-loaded classifier
_skin_classifier = None


class SkinDiseaseClassifier:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.classes = SKIN_CLASSES
        self.input_h, self.input_w = 224, 224
        self.model = self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Skin model not found: {self.model_path}")
        return keras.models.load_model(self.model_path, compile=False)

    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        if image.mode != "RGB":
            image = image.convert("RGB")
        image = image.resize((self.input_w, self.input_h), Image.BILINEAR)

        arr = np.asarray(image).astype("float32")

        # Ensure 3 channels
        if arr.ndim == 2:
            arr = np.dstack([arr] * 3)
        elif arr.shape[-1] == 4:  # strip alpha
            arr = arr[..., :3]

        arr = preprocess_input(arr)
        return np.expand_dims(arr, axis=0)

    def _softmax_if_needed(self, logits: np.ndarray) -> np.ndarray:
        sums = np.sum(logits, axis=1, keepdims=True)
        if np.all(logits >= 0.0) and np.all(logits <= 1.0) and np.all(np.abs(sums - 1.0) < 1e-3):
            return logits
        exp = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        return exp / np.sum(exp, axis=1, keepdims=True)

    def predict(self, image_bytes: bytes) -> dict:
        image = Image.open(io.BytesIO(image_bytes))
        input_tensor = self._preprocess_image(image)
        preds = self.model.predict(input_tensor, verbose=0)
        probs = self._softmax_if_needed(preds)
        best_idx = int(np.argmax(probs[0]))
        return {
            "label": self.classes[best_idx],
            "probability": float(probs[0][best_idx]),
        }


def _get_skin_classifier() -> SkinDiseaseClassifier | None:
    global _skin_classifier
    if _skin_classifier is not None:
        return _skin_classifier

    models_dir = current_app.config.get("MODELS_DIR")
    if not models_dir:
        logging.error("MODELS_DIR not set in Flask config")
        return None

    model_file = os.path.join(models_dir, "skin_disease_finetuned (1).keras")
    if not os.path.exists(model_file):
        logging.error("Skin model file missing: %s", model_file)
        return None

    try:
        _skin_classifier = SkinDiseaseClassifier(model_file)
        logging.info("Loaded skin model from %s", model_file)
        return _skin_classifier
    except Exception as e:
        logging.exception("Failed to load skin model: %s", e)
        return None


@skin_bp.route("/", methods=["GET"])
def upload():
    if not session.get("user_id"):
        return redirect("/login?next=/skin/")
    return render_template("skin.html")


@skin_bp.route("/predict", methods=["POST"])
def predict():
    if not session.get("user_id"):
        return redirect("/login?next=/skin/")

    file = request.files.get("image")
    if not file:
        flash("Please upload an image", "error")
        return redirect(url_for("skin.upload"))

    filename = secure_filename(file.filename or "")
    if not filename:
        flash("Invalid filename", "error")
        return redirect(url_for("skin.upload"))

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_folder, exist_ok=True)
    save_path = os.path.join(upload_folder, filename)
    file.save(save_path)

    result = None
    clf = _get_skin_classifier()
    if clf is not None:
        try:
            with open(save_path, "rb") as f:
                img_bytes = f.read()
            pred = clf.predict(img_bytes)
            result = {
                "model": "skin_disease_finetuned (1).keras",
                "classes": clf.classes,
                "predicted": pred["label"],
                "confidence": round(pred["probability"], 4),
            }
        except Exception as e:
            logging.exception("Prediction error: %s", e)
            flash("Prediction failed: " + str(e), "error")

    if result is None:
        flash("Skin model not available; showing demo output.", "info")
        result = {
            "model": "demo",
            "classes": SKIN_CLASSES,
            "predicted": "Normal",
            "confidence": 0.92,
        }

    return render_template("skin.html", result=result, image_filename=filename)
