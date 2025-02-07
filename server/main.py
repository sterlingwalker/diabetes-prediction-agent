# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import pickle
import os

# Import LangChain libraries
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms.openai import OpenAI


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
        "riskProbability": f"{risk_probability:.2f}"
    }

openai_api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(temperature=0.7, openai_api_key=openai_api_key)

# Define expert prompts and their chains.
endocrinologist_prompt = PromptTemplate(
    input_variables=['patient'],
    template=(
        "As an endocrinologist, provide a treatment plan for the following patient. "
        "Here is the patient data: {patient}\n\n"
        "Provide actionable and specific recommendations."
    )
)
dietitian_prompt = PromptTemplate(
    input_variables=['patient'],
    template=(
        "As a dietitian, create a dietary plan for the following patient. "
        "Here is the patient data: {patient}\n\n"
        "Focus on managing diabetes and improving overall health."
    )
)
fitness_prompt = PromptTemplate(
    input_variables=['patient'],
    template=(
        "As a fitness expert, create an exercise plan for the following patient. "
        "Here is the patient data: {patient}\n\n"
        "Focus on managing diabetes and enhancing overall fitness."
    )
)


# Create the individual LLM chains
endocrinologist_chain = LLMChain(llm=llm, prompt=endocrinologist_prompt)
dietitian_chain = LLMChain(llm=llm, prompt=dietitian_prompt)
fitness_chain = LLMChain(llm=llm, prompt=fitness_prompt)

# Define the meta-agent prompt to consolidate the responses.
meta_agent_prompt = PromptTemplate(
    input_variables=['endocrinologist', 'dietitian', 'fitness', 'patient'],
    template=(
        "You are a health consultant consolidating recommendations from multiple experts for a patient. "
        "Here is the patient data: {patient}\n\n"
        "Endocrinologist Recommendation:\n{endocrinologist}\n\n"
        "Dietitian Recommendation:\n{dietitian}\n\n"
        "Fitness Expert Recommendation:\n{fitness}\n\n"
        "Based on these expert recommendations, provide a final consolidated care plan for the patient."
    )
)

meta_agent_chain = LLMChain(llm=llm, prompt=meta_agent_prompt)

# API endpoint for predictions
@app.post("/predict")
async def predict(patient: PatientData):
    try:
        result = predict_patient(patient.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/recommendations")
async def get_recommendations(patient: PatientData):
    try:
        # Convert the patient data into a string representation that can be inserted into the prompts.
        patient_str = str(patient.dict())
        
        # Run the expert chains with the patient data.
        endocrinologist_rec = endocrinologist_chain.run(patient=patient_str)
        dietitian_rec = dietitian_chain.run(patient=patient_str)
        fitness_rec = fitness_chain.run(patient=patient_str)
        
        # Use the meta-agent chain to consolidate the recommendations.
        final_rec = meta_agent_chain.run(
            endocrinologist=endocrinologist_rec,
            dietitian=dietitian_rec,
            fitness=fitness_rec,
            patient=patient_str
        )
        
        # Return all recommendations as JSON.
        return {
            "endocrinologistRecommendation": endocrinologist_rec,
            "dietitianRecommendation": dietitian_rec,
            "fitnessRecommendation": fitness_rec,
            "finalRecommendation": final_rec
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the app (only if this file is executed directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)