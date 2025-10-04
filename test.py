from tensorflow import keras

model = keras.models.load_model("models/skin_disease_finetuned (1).keras", compile=False)
print("Loaded Skin Model OK")

model = keras.models.load_model("models/best_nail_model.keras", compile=False)
print("Loaded Nail Model OK")
