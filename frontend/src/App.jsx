import React, { useState } from "react";

// List of all symptoms
const allSymptoms = [
  "keeping an erection", "itchy nose", "swelling", "lightheadedness", "sore throat",
  "pain during sex", "urgency to urinate", "pink eye", "vomiting", "difficulty getting",
  "blood in the stool", "chest tightness", "persistent cough", "unexplained heat intolerance",
  "muscle aches", "difficulty with balance", "dizziness", "tremors", "fatigue", "rash",
  "memory loss", "coughing", "shortness of breath", "diarrhea", "headache", "nausea",
  "chest pain", "abdominal cramps", "loss of interest in activities", "difficulty speaking",
  "high blood pressure", "night sweats", "pale skin", "changes in appetite", "confusion",
  "painful urination", "blurred vision", "itching", "runny nose", "difficulty breathing",
];

function App() {
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCheckboxChange = (symptom) => {
    setSelectedSymptoms((prev) =>
      prev.includes(symptom) ? prev.filter((s) => s !== symptom) : [...prev, symptom]
    );
  };

  const handlePredict = async () => {
    setLoading(true);
    setResult(null);

    if (selectedSymptoms.length === 0) {
      alert("⚠️ Please select at least one symptom.");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("https://predict-disease-vmy1.onrender.com/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symptoms: selectedSymptoms }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      alert("❌ Failed to get prediction.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row items-center bg-gray-900">
      {/* Symptoms Section */}
      <div className="w-full lg:w-3/5 bg-white/10 backdrop-blur-lg shadow-xl rounded-xl p-8 border border-white/30 text-white">
        <h1 className="text-2xl font-bold text-center mb-4">🏥 Disease Prediction</h1>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 h-96  p-4 rounded-lg shadow-md bg-white/20">
          {allSymptoms.map((symptom, index) => (
            <label key={index} className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={selectedSymptoms.includes(symptom)}
                onChange={() => handleCheckboxChange(symptom)}
                className="w-4 h-4 accent-indigo-600"
              />
              <span className="text-sm">{symptom}</span>
            </label>
          ))}
        </div>

        <button
          onClick={handlePredict}
          className="w-full bg-white p-3 mt-4 rounded-lg text-black hover:scale-105 transition"
        >
          {loading ? "🔍 Predicting..." : "Predict"}
        </button>
      </div>

      {/* Diagnosis Report */}
      <div className="w-full lg:w-2/5 bg-white/90 text-gray-900 p-6 rounded-md mt-6 lg:mt-0 lg:ml-6 shadow-xl">
        <h2 className="text-xl font-bold text-center text-indigo-600">✅ Diagnosis Report</h2>

        {result ? (
          <div className="mt-4 space-y-2">
            <p><strong>🦠 Disease:</strong> {result.disease}</p>
            <p><strong>💊 Cure:</strong> {result.cure}</p>
            <p><strong>👨‍⚕️ Consult:</strong> {result.doctor}</p>
            <p><strong>⚠️ Risk Level:</strong> {result.risk_level}</p>
            <p><strong>📊 Accuracy:</strong> {result.accuracy}%</p>
          </div>
        ) : (
          <p className="text-gray-500 text-center mt-4">No diagnosis yet.</p>
        )}
      </div>
    </div>
  );
}

export default App;
