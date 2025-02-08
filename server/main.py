from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import pickle
import logging
import json
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

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
            "PredictedRisk": "Diabetes" if risk == 1 else "No Diabetes",
            "RiskProbability": f"{risk_probability:.2f}%"
        }
    except Exception as e:
        logging.error("Prediction error: %s", str(e))
        raise

def parse_patient_data(patient: dict = Depends()):
    """Convert string values to floats before validation."""
    try:
        return {key: float(value) for key, value in patient.items()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")

@app.post("/predict")
async def predict(patient: dict = Depends(parse_patient_data)):
    try:
        logging.info(f"Received valid patient data: {patient}")
        result = predict_patient(patient)
        return result
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Initialize OpenAI model with API Key
openai_api_key = os.getenv("OPENAI_API_KEY")  # Load API key from environment variables
llm = ChatOpenAI(temperature=0.7, openai_api_key=openai_api_key)

# Define expert prompts
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
        "Focus on managing diabetes and improving health."
    )
)
fitness_prompt = PromptTemplate(
    input_variables=['patient'],
    template=(
        "As a fitness expert, create an exercise plan for the following patient. "
        "Here is the patient data: {patient}\n\n"
        "Focus on managing diabetes and overall fitness."
    )
)

# Define expert chains
endocrinologist_chain = LLMChain(llm=llm, prompt=endocrinologist_prompt)
dietitian_chain = LLMChain(llm=llm, prompt=dietitian_prompt)
fitness_chain = LLMChain(llm=llm, prompt=fitness_prompt)

# Meta-agent prompt to consolidate expert recommendations
meta_agent_prompt = PromptTemplate(
    input_variables=['endocrinologist', 'dietitian', 'fitness', 'patient'],
    template=(
        "You are a health consultant consolidating recommendations from multiple experts for a patient. "
        "Here is the patient data: {patient}\n\n"
        "Endocrinologist Recommendation:\n{endocrinologist}\n\n"
        "Dietitian Recommendation:\n{dietitian}\n\n"
        "Fitness Expert Recommendation:\n{fitness}\n\n"
        "Based on these expert recommendations, provide a final consolidated plan for the patient."
    )
)
meta_agent_chain = LLMChain(llm=llm, prompt=meta_agent_prompt)

@app.post("/recommendations")
async def get_recommendations(patient: PatientData):
    try:
        patient_data = patient.dict()

        # Run expert chains using properly formatted inputs
        endocrinologist_recommendation = endocrinologist_chain.invoke({"patient": str(patient_data)})
        dietitian_recommendation = dietitian_chain.invoke({"patient": str(patient_data)})
        fitness_recommendation = fitness_chain.invoke({"patient": str(patient_data)})

        # Consolidate recommendations
        final_recommendation = meta_agent_chain.invoke({
            "endocrinologist": endocrinologist_recommendation,
            "dietitian": dietitian_recommendation,
            "fitness": fitness_recommendation,
            "patient": str(patient_data)
        })

        return {
            "EndocrinologistRecommendation": endocrinologist_recommendation,
            "DietitianRecommendation": dietitian_recommendation,
            "FitnessRecommendation": fitness_recommendation,
            "FinalRecommendation": final_recommendation
        }
    except Exception as e:
        logging.error(f"Error processing recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
