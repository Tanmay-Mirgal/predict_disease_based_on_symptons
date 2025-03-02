from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import traceback
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get the absolute path of the server directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Paths to model and dataset files
MODEL_PATH = os.path.join(BASE_DIR, "disease_prediction_model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "label_encoder.pkl")
DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")

# Load the trained model and label encoder
try:
    model = joblib.load(MODEL_PATH)
    label_encoder = joblib.load(ENCODER_PATH)
    print("✅ Model and Label Encoder loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model or label encoder: {str(e)}")
    exit(1)  # Exit if models can't be loaded

# Load dataset and extract feature names
try:
    df = pd.read_csv(DATASET_PATH)
    X_columns = [col for col in df.columns if col not in ["disease", "cures", "doctor", "risk level"]]
    disease_info = df[['disease', 'cures', 'doctor', 'risk level']].drop_duplicates()
    print("✅ Dataset loaded successfully!")
except Exception as e:
    print(f"❌ Error loading dataset: {str(e)}")
    exit(1)  # Exit if dataset can't be loaded

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        user_symptoms = set(data.get("symptoms", []))

        if not user_symptoms:
            return jsonify({"error": "No symptoms provided"}), 400

        # Ensure only valid symptoms are used
        unexpected_symptoms = user_symptoms - set(X_columns)
        if unexpected_symptoms:
            return jsonify({"error": f"Unexpected symptoms found: {list(unexpected_symptoms)}"}), 400

        # Convert symptoms to binary format
        symptoms_binary = [1 if symptom in user_symptoms else 0 for symptom in X_columns]
        input_df = pd.DataFrame([symptoms_binary], columns=X_columns)

        # Make predictions
        prediction_proba = model.predict_proba(input_df)
        prediction = model.predict(input_df)
        predicted_disease = label_encoder.inverse_transform(prediction)[0]

        # Get disease details
        disease_details = disease_info[disease_info['disease'] == predicted_disease].iloc[0]

        response = {
            "disease": predicted_disease,
            "cure": disease_details["cures"],
            "doctor": disease_details["doctor"],
            "risk_level": disease_details["risk level"],
            "accuracy": round(max(prediction_proba[0]) * 100, 2)
        }

        return jsonify(response)

    except Exception as e:
        print("❌ ERROR:", str(e))
        traceback.print_exc()  # Print full error details in console
        return jsonify({"error": "An internal server error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
