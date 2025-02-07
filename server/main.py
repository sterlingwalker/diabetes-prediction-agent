# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import pickle

# Load the pre-trained scaler and model
try:
    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
except Exception as e:
    raise Exception("Error loading model/scaler. Please ensure they are trained and saved correctly.") from e

# Initialize the FastAPI app
app = FastAPI()

# Enable CORS if needed (e.g., for a React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a Pydantic model for input validation
class PatientData(BaseModel):
    Pregnancies: float
    Glucose: float
    BloodPressure: float
    SkinThickness: float
    Insulin: float
    BMI: float
    DiabetesPedigreeFunction: float
    Age: float

# Define a prediction function
def predict_patient(patient_data: dict):
    # Convert the dictionary to a pandas DataFrame
    patient_df = pd.DataFrame([patient_data])
    # Scale the data using the pre-trained scaler
    patient_scaled = scaler.transform(patient_df)
    # Make the prediction and calculate the probability
    risk = model.predict(patient_scaled)[0]
    risk_probability = model.predict_proba(patient_scaled)[0][1] * 100
    return {
        "predictedRisk": "Diabetes" if risk == 1 else "No Diabetes",
        "riskProbability": f"{risk_probability:.2f}%"
    }

# API endpoint for predictions
@app.post("/predict")
async def predict(patient: PatientData):
    try:
        result = predict_patient(patient.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app (only if this file is executed directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)