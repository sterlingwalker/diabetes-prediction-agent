from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import pickle
import os
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI app
app = FastAPI()

# Enable CORS if needed (e.g., for a React frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define Pydantic model for input validation
class PatientData(BaseModel):
    Pregnancies: float
    Glucose: float
    BloodPressure: float
    SkinThickness: float
    Insulin: float
    BMI: float
    DiabetesPedigreeFunction: float
    Age: float

# Load the pre-trained scaler and model
try:
    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
except Exception as e:
    logging.error("Error loading model/scaler: %s", str(e))
    raise Exception("Error loading model/scaler. Please ensure they are trained and saved correctly.") from e

# Middleware to log incoming requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    body = await request.body()
    try:
        json_body = json.loads(body.decode("utf-8"))
        logging.info(f"Incoming request to {request.url.path} with body: {json.dumps(json_body, indent=2)}")
    except json.JSONDecodeError:
        logging.error(f"Could not parse request body for {request.url.path}: {body.decode('utf-8')}")
    
    response = await call_next(request)
    return response

# Define a prediction function
def predict_patient(patient_data: dict):
    try:
        # Convert dictionary to pandas DataFrame
        patient_df = pd.DataFrame([patient_data])
        
        # Scale data using the pre-trained scaler
        patient_scaled = scaler.transform(patient_df)
        
        # Make prediction and calculate probability
        risk = model.predict(patient_scaled)[0]
        risk_probability = model.predict_proba(patient_scaled)[0][1] * 100
        
        return {
            "predictedRisk": "Diabetes" if risk == 1 else "No Diabetes",
            "riskProbability": f"{risk_probability:.2f}"
        }
    except Exception as e:
        logging.error("Prediction error: %s", str(e))
        raise

# API endpoint for predictions with logging
@app.post("/predict")
async def predict(patient: PatientData):
    try:
        logging.info(f"Received valid patient data: {patient.dict()}")  # Log parsed request data
        result = predict_patient(patient.dict())
        return result
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# API endpoint for recommendations
@app.post("/recommendations")
async def get_recommendations(patient: PatientData):
    try:
        patient_str = str(patient.dict())
        
        # Dummy placeholders for expert chains (modify as needed)
        endocrinologist_rec = "Endocrinologist recommendation based on patient data"
        dietitian_rec = "Dietitian recommendation based on patient data"
        fitness_rec = "Fitness expert recommendation based on patient data"

        final_rec = (
            f"Final consolidated plan:\n\n"
            f"Endocrinologist: {endocrinologist_rec}\n"
            f"Dietitian: {dietitian_rec}\n"
            f"Fitness: {fitness_rec}"
        )

        return {
            "endocrinologistRecommendation": endocrinologist_rec,
            "dietitianRecommendation": dietitian_rec,
            "fitnessRecommendation": fitness_rec,
            "finalRecommendation": final_rec
        }
    except Exception as e:
        logging.error(f"Error processing recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
