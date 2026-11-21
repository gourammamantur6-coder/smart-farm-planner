
import pandas as pd
import joblib
from huggingface_hub import hf_hub_download

# Download model files
model_path = hf_hub_download(
    repo_id="coderprem/crop-recommendation",
    filename="soil.pkl"
)

encoder_path = hf_hub_download(
    repo_id="coderprem/crop-recommendation",
    filename="label_encoder.pkl"
)

# Load trained model and label encoder
model = joblib.load(model_path)
label_encoder = joblib.load(encoder_path)


def recommend_crop(n, p, k, temperature, humidity, ph, rainfall):

    inputs = pd.DataFrame(
        [[n, p, k, temperature, humidity, ph, rainfall]],
        columns=["N", "P", "K", "temperature",
                 "humidity", "ph", "rainfall"]
    )

    prediction = model.predict(inputs)

    crop = label_encoder.inverse_transform(prediction)

    return {
        "recommended_crop": str(crop[0])
    }
