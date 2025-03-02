from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import traceback
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get absolute path of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load trained model and label encoder
try:
    model_path = os.path.join(BASE_DIR, "server", "disease_prediction_model.pkl")
    label_encoder_path = os.path.join(BASE_DIR, "server", "label_encoder.pkl")

    model = joblib.load(model_path)
    label_encoder = joblib.load(label_encoder_path)
    print("✅ Model and Label Encoder loaded successfully!")
except Exception as e:
    print("❌ Error loading model or label encoder:", str(e))
    exit(1)  # Stop execution if models can't be loaded

# Load dataset and extract feature names (excluding non-symptom columns)
try:
    dataset_path = os.path.join(BASE_DIR, "server", "dataset.csv")
    df = pd.read_csv(dataset_path)
    X_columns = [col for col in df.columns if col not in ["disease", "cures", "doctor", "risk level"]]
    disease_info = df[['disease', 'cures', 'doctor', 'risk level']].drop_duplicates()
    print("✅ Dataset loaded successfully!")
except Exception as e:
    print("❌ Error loading dataset:", str(e))
    exit(1)  # Stop execution if dataset can't be loaded

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        user_symptoms = set(data.get("symptoms", []))

        if not user_symptoms:
            return jsonify({"error": "No symptoms provided"}), 400

        # Ensure input symptoms match expected feature names
        unexpected_symptoms = user_symptoms - set(X_columns)
        if unexpected_symptoms:
            return jsonify({"error": f"Unexpected symptoms found: {list(unexpected_symptoms)}"}), 400

        missing_features = set(X_columns) - user_symptoms  # Missing symptoms from input
        print(f"🔹 Missing Features: {missing_features}")

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
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
