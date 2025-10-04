import os
from typing import List, Tuple


def _lazy_import_tf():
    try:
        import tensorflow as tf  # type: ignore
        return tf
    except Exception:
        return None


class ModelWrapper:
    def __init__(self, model_path: str, input_size: Tuple[int, int], class_names: List[str]):
        self.model_path = model_path
        self.input_size = input_size
        self.class_names = class_names
        self.model = None

    def load(self) -> bool:
        tf = _lazy_import_tf()
        if tf is None:
            return False
        if not os.path.exists(self.model_path):
            return False
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            return True
        except Exception:
            self.model = None
            return False

    def predict_image_path(self, image_path: str):
        tf = _lazy_import_tf()
        if tf is None or self.model is None:
            return None
        img = tf.keras.preprocessing.image.load_img(image_path, target_size=self.input_size)
        x = tf.keras.preprocessing.image.img_to_array(img)
        x = x / 255.0
        x = x[None, ...]
        preds = self.model.predict(x)
        if preds.ndim == 2 and preds.shape[0] == 1:
            preds = preds[0]
        idx = int(preds.argmax())
        confidence = float(preds[idx]) if hasattr(preds, '__getitem__') else 0.0
        label = self.class_names[idx] if 0 <= idx < len(self.class_names) else 'Unknown'
        return label, confidence


