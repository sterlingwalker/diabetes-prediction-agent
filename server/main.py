from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import pickle
import logging
import json
import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import uvicorn
from typing import Union


# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

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



class PatientData(BaseModel):
    Pregnancies: Union[float, str] = 0.0
    Glucose: Union[float, str] = 0.0
    BloodPressure: Union[float, str] = 0.0
    SkinThickness: Union[float, str] = 0.0
    Insulin: Union[float, str] = 0.0
    BMI: Union[float, str] = 0.0
    DiabetesPedigreeFunction: Union[float, str] = 0.0
    Age: Union[float, str] = 0.0


# Load the pre-trained scaler and model
try:
    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
except Exception as e:
    logger.error("Error loading model/scaler: %s", str(e))
    raise Exception("Error loading model/scaler. Ensure they are trained and saved correctly.") from e

# Middleware to log requests and prevent response stream errors
@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            if body:
                json_body = json.loads(body.decode("utf-8"))
                logger.info(f"Incoming request to {request.url.path} with body: {json.dumps(json_body, indent=2)}")
        else:
            logger.info(f"Incoming {request.method} request to {request.url.path}")
    except Exception as e:
        logger.error(f"Error logging request: {str(e)}")

    response = await call_next(request)
    return response

# Define a prediction function
def predict_patient(patient_data: dict):
    try:
        patient_df = pd.DataFrame([patient_data])
        patient_scaled = scaler.transform(patient_df)
        risk = model.predict(patient_scaled)[0]
        risk_probability = model.predict_proba(patient_scaled)[0][1] * 100
        
        return {
            "predictedRisk": "Diabetes" if risk == 1 else "No Diabetes",
            "riskProbability": f"{risk_probability:.2f}%"
        }
    except Exception as e:
        logger.error("Prediction error: %s", str(e))
        raise

@app.post("/predict")
async def predict(patient: PatientData):
    try:
        # Convert input values to float, defaulting empty strings to 0
        patient_data = {
            key: float(value) if isinstance(value, (int, float)) or value.strip() else 0.0
            for key, value in patient.dict().items()
        }

        logger.info(f"Received valid patient data with defaults: {patient_data}")

        result = predict_patient(patient_data)
        logger.info(f"Prediction result: {result}")
        return result

    except ValueError as e:
        logger.error(f"Invalid input: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Initialize OpenAI model with API Key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise Exception("Missing OpenAI API key. Set OPENAI_API_KEY in environment variables.")

llm = ChatOpenAI(temperature=0.7, openai_api_key=openai_api_key)

# Define expert prompts
endocrinologist_prompt = PromptTemplate(
    input_variables=['patient'],
    template="As an endocrinologist, provide a treatment plan for the following patient: {patient}"
)
dietitian_prompt = PromptTemplate(
    input_variables=['patient'],
    template="As a dietitian, create a dietary plan for the following patient: {patient}"
)
fitness_prompt = PromptTemplate(
    input_variables=['patient'],
    template="As a fitness expert, create an exercise plan for the following patient: {patient}"
)

# Define expert chains
endocrinologist_chain = LLMChain(llm=llm, prompt=endocrinologist_prompt)
dietitian_chain = LLMChain(llm=llm, prompt=dietitian_prompt)
fitness_chain = LLMChain(llm=llm, prompt=fitness_prompt)

# Meta-agent prompt to consolidate expert recommendations
meta_agent_prompt = PromptTemplate(
    input_variables=['endocrinologist', 'dietitian', 'fitness', 'patient'],
    template=(
        "You are a health consultant consolidating recommendations for a patient. "
        "Patient Data: {patient}\n\n"
        "Endocrinologist Recommendation:\n{endocrinologist}\n\n"
        "Dietitian Recommendation:\n{dietitian}\n\n"
        "Fitness Expert Recommendation:\n{fitness}\n\n"
        "Provide a final consolidated plan for the patient."
    )
)
meta_agent_chain = LLMChain(llm=llm, prompt=meta_agent_prompt)

@app.post("/recommendations")
async def get_recommendations(patient: PatientData):
    try:
        # Convert input values to float, defaulting empty strings to 0.0
        patient_data = {
            key: float(value) if isinstance(value, (int, float)) or value.strip() else 0.0
            for key, value in patient.dict().items()
        }

        logger.info(f"Received patient data with defaults: {patient_data}")

        # Run expert chains
        endocrinologist_recommendation = endocrinologist_chain.run(patient=str(patient_data))
        dietitian_recommendation = dietitian_chain.run(patient=str(patient_data))
        fitness_recommendation = fitness_chain.run(patient=str(patient_data))

        logger.info(f"Endocrinologist: {endocrinologist_recommendation}")
        logger.info(f"Dietitian: {dietitian_recommendation}")
        logger.info(f"Fitness: {fitness_recommendation}")

        # Consolidate recommendations
        final_recommendation = meta_agent_chain.run(
            endocrinologist=endocrinologist_recommendation,
            dietitian=dietitian_recommendation,
            fitness=fitness_recommendation,
            patient=str(patient_data)
        )

        response_data = {
            "rndocrinologistRecommendation": endocrinologist_recommendation,
            "dietitianRecommendation": dietitian_recommendation,
            "fitnessRecommendation": fitness_recommendation,
            "finalRecommendation": final_recommendation
        }

        logger.info(f"Final Response: {json.dumps(response_data, indent=2)}")
        return response_data

    except Exception as e:
        logger.error(f"Error processing recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Ensure compatibility with Render
    uvicorn.run(app, host="0.0.0.0", port=port, timeout_keep_alive=300)
