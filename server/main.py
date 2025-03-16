import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import joblib
import logging
import json
import os
import io
import base64
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import uvicorn
from typing import Union, List, Dict
from sklearn.impute import SimpleImputer
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from imblearn.pipeline import Pipeline
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
import asyncio

# Load environment variables
load_dotenv()

# Define `openai_api_key`
openai_api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define PatientData Model
class PatientData(BaseModel):
    patient_name: str = ""  # ✅ Added patient_name field
    Glucose: Union[float, str] = 0.0
    BloodPressure: Union[float, str] = 0.0
    BMI: Union[float, str] = 0.0
    Age: Union[float, str] = 0.0
    Gender: Union[float, str] = 0.0
    Ethnicity: Union[float, str] = 0.0

# Define ChatRequest Model
class ChatRequest(BaseModel):
    history: List[Dict[str, str]]
    user_input: str
    patient_name: str = ""  # ✅ Added patient_name field
    patient_data: Dict[str, Union[str, float]]
    recommendations: Dict[str, str]
    predicted_risk: str
    risk_probability: str

# Load Models
try:
    lgbm_model = joblib.load("lightgbm_model.pkl")
    tuned_rf_model = joblib.load("tuned_rf_model.pkl")
except Exception as e:
    logger.error("Error loading models: %s", str(e))
    raise Exception("Error loading LightGBM or Random Forest models.") from e

llm = ChatOpenAI(temperature=0.4, openai_api_key=openai_api_key)

# Chat Agent Prompt
chat_prompt = PromptTemplate(
    input_variables=['history', 'user_input', 'patient_name', 'patient_data', 'recommendations', 'predicted_risk', 'risk_probability'],
    template=(
        "You are a medical AI assistant helping a patient manage their health.\n\n"
        "**Patient Name:** {patient_name}\n\n"
        "**Patient Details:**\n"
        "{patient_data}\n\n"
        "**Predicted Risk:** {predicted_risk}\n"
        "**Risk Probability:** {risk_probability}\n\n"
        "**Expert Recommendations:**\n"
        "{recommendations}\n\n"
        "**Conversation History:**\n"
        "{history}\n\n"
        "Now, the user is asking:\n{user_input}\n\n"
        "Provide an informative response considering the patient's data, medical risk, and expert recommendations."
    )
)
chat_chain = LLMChain(llm=llm, prompt=chat_prompt)

@app.post("/predict")
async def predict(patient: PatientData):
    try:
        patient_data = {k: float(v) if str(v).strip() else np.nan for k, v in patient.model_dump().items() if k != "patient_name"}
        logger.info(f"Received prediction request for patient: {patient.patient_name}")

        result = predict_diabetes_risk(patient_data)
        logger.info(f"Prediction result for {patient.patient_name}: {result}")

        return result

    except Exception as e:
        logger.error(f"Error processing request for {patient.patient_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    try:
        cleaned_patient_data = {key: float(value) if isinstance(value, (int, float)) or str(value).strip() else 0.0 for key, value in chat_request.patient_data.items()}
        formatted_history = "\n".join([f"**{msg['role'].capitalize()}**: {msg['content']}" for msg in chat_request.history])
        formatted_patient_data = f"Patient Name: {chat_request.patient_name}\n"
        formatted_patient_data += "\n".join([f"- {key}: {value}" for key, value in cleaned_patient_data.items()])
        formatted_recommendations = "\n".join([f"- {key}: {value}" for key, value in chat_request.recommendations.items()])

        response = chat_chain.run(
            history=formatted_history,
            user_input=chat_request.user_input,
            patient_name=chat_request.patient_name,
            patient_data=formatted_patient_data,
            recommendations=formatted_recommendations,
            predicted_risk=chat_request.predicted_risk,
            risk_probability=str(float(chat_request.risk_probability.strip().replace("%", "")))
        )

        chat_request.history.append({"role": "assistant", "content": response})

        return {
            "response": response,
            "updated_history": chat_request.history
        }

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, timeout_keep_alive=300)
