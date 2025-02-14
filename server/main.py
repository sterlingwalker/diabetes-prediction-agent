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
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
import uvicorn
from typing import Union, List, Dict
from sklearn.impute import SimpleImputer


# Load environment variables
load_dotenv()


# Define `openai_api_key` BEFORE using it
openai_api_key = os.getenv("OPENAI_API_KEY")


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

# Define Chat Request Model
class ChatRequest(BaseModel):
    history: List[Dict[str, str]]  # Chat history
    user_input: str  # User's latest message
    patient_data: Dict[str, float]  # Patient details
    recommendations: Dict[str, str]  # Expert recommendations
    predicted_risk: str  # Predicted risk result (e.g., "Diabetes" or "No Diabetes")
    risk_probability: str  # Probability score (e.g., "72.50%")

# Load the LightGBM and Random Forest models
try:
    lgbm_model = joblib.load("lightgbm_model.pkl")
    tuned_rf_model = joblib.load("tuned_rf_model.pkl")
except Exception as e:
    logger.error("Error loading models: %s", str(e))
    raise Exception("Error loading LightGBM or Random Forest models.") from e


llm = ChatOpenAI(temperature=0.7, openai_api_key=openai_api_key) 


# Chat Agent Prompt with Risk & Probability
chat_prompt = PromptTemplate(
    input_variables=['history', 'user_input', 'patient_data', 'recommendations', 'predicted_risk', 'risk_probability'],
    template=(
        "You are a medical AI assistant helping a patient manage their health.\n\n"
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

# Define a prediction function with model selection logic
def predict_diabetes_risk(patient_data: dict):
    try:
        lgbm_features = ['Glucose', 'BMI', 'Age']
        rf_features = ['Glucose', 'BMI', 'Age', 'Pregnancies', 'DiabetesPedigreeFunction', 'BloodPressure', 'Insulin']
        critical_features = ['Glucose', 'BMI', 'Age']
        features_to_check = ['BloodPressure', 'Insulin', 'Pregnancies', 'DiabetesPedigreeFunction', 'BMI', 'Glucose']

        # Convert data to DataFrame and handle missing values
        patient_df = pd.DataFrame([patient_data])
        patient_df[features_to_check] = patient_df[features_to_check].replace(0, np.nan)

        # Select model based on missing values
        if patient_df.isnull().any().any():
            selected_model, selected_features = lgbm_model, lgbm_features
            model_used = "LightGBM"
            logger.info("Using LightGBM (Missing Values Detected)")
        else:
            selected_model, selected_features = tuned_rf_model, rf_features
            model_used = "Tuned Random Forest"
            logger.info("Using Tuned Random Forest (Complete Data Detected)")

        # Keep only selected features
        patient_df = patient_df[selected_features]

        # Handle missing values
        if model_used == "LightGBM":
            missing_critical = patient_df[critical_features].isnull().any()
            if missing_critical.any():
                logger.info("Imputing Missing Critical Features for LightGBM...")
                for feature in critical_features:
                    if patient_df[feature].isnull().all():
                        default_values = {'Glucose': 120, 'BMI': 25, 'Age': 40}
                        patient_df[feature] = default_values[feature]
                    else:
                        imputer = SimpleImputer(strategy='median')
                        patient_df[[feature]] = imputer.fit_transform(patient_df[[feature]])
        elif model_used == "Tuned Random Forest":
            if patient_df.isnull().any().any():
                imputer = SimpleImputer(strategy='median')
                patient_df = pd.DataFrame(imputer.fit_transform(patient_df), columns=patient_df.columns)

        # Make predictions
        risk = selected_model.predict(patient_df)[0]
        risk_probability = selected_model.predict_proba(patient_df)[:, 1][0] * 100

        return {
            "predictedRisk": "Diabetes" if risk == 1 else "No Diabetes",
            "riskProbability": f"{risk_probability:.2f}%",
            "modelUsed": model_used
        }
    except Exception as e:
        logger.error("Prediction error: %s", str(e))
        raise

@app.post("/predict")
async def predict(patient: PatientData):
    try:
        # ✅ Convert input values to float safely, handling invalid values
        patient_data = {}
        for key, value in patient.model_dump().items():  # ✅ Updated from `dict()`
            try:
                # ✅ Strip whitespace, remove invalid characters, and convert to float
                cleaned_value = str(value).strip().replace("`", "").replace("'", "")
                patient_data[key] = float(cleaned_value) if cleaned_value else 0.0
            except ValueError:
                logger.error(f"Invalid input for {key}: {value}")
                raise HTTPException(status_code=400, detail=f"Invalid input for {key}: {value}")

        logger.info(f"Received patient data with defaults: {patient_data}")

        result = predict_diabetes_risk(patient_data)
        logger.info(f"Prediction result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



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


# Initialize OpenAI model with API Key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise Exception("Missing OpenAI API key. Set OPENAI_API_KEY in environment variables.")

llm = ChatOpenAI(temperature=0.7, openai_api_key=openai_api_key)


# Biomedical Evidence Fetching Function
def get_biomedical_evidence(patient_data):
    query_parts = ["diabetes treatment"]
    if patient_data.get("Glucose"):
        query_parts.append(f"glucose {patient_data['Glucose']}")
    if patient_data.get("BMI"):
        query_parts.append(f"BMI {patient_data['BMI']}")
    
    query = " ".join(query_parts)
    logger.info(f"🔍 Searching PubMed for: {query}")

    pubmed_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmax=5&retmode=json"
    response = requests.get(pubmed_url).json()
    pubmed_ids = response.get("esearchresult", {}).get("idlist", [])

    evidence = []
    for pmid in pubmed_ids:
        detail_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={pmid}&retmode=json"
        detail_response = requests.get(detail_url).json()
        title = detail_response.get("result", {}).get(pmid, {}).get("title", "No title found")
        evidence.append(title)

    logger.info(f"📄 Extracted Biomedical Evidence: {evidence}")
    return evidence



# Create Patient Context for LLM
def create_dynamic_context(patient_data, evidence, risk_result):
    context = (
        f"**Patient Details:**\n"
        f"- Age: {patient_data.get('Age', 'Unknown')}\n"
        f"- BMI: {patient_data.get('BMI', 'Unknown')}\n"
        f"- Glucose: {patient_data.get('Glucose', 'Unknown')}\n"
        f"- Diabetes Prediction: {risk_result.get('predictedRisk', 'Unknown')} "
        f"({risk_result.get('riskProbability', 'N/A')})\n\n"
        "**Relevant Biomedical Evidence:**\n" +
        "\n".join(f"- {e}" for e in evidence)
    )
    return context


# Generate Expert Recommendations
def get_expert_recommendations(patient_data, risk_result):
    evidence = get_biomedical_evidence(patient_data)
    context = create_dynamic_context(patient_data, evidence, risk_result)

    expert_prompts = {
        "Endocrinologist": PromptTemplate(
            input_variables=['patient', 'context', 'risk_result'],
            template=(
                "As an endocrinologist, provide a diabetes treatment plan.\n"
                "Patient Data: {patient}\n\n"
                "Risk Result: {risk_result}\n\n"
                "Based on the following biomedical evidence:\n{context}\n\n"
                "Provide a structured treatment plan."
            )
        ),
        "Dietitian": PromptTemplate(
            input_variables=['patient', 'context', 'risk_result'],
            template=(
                "As a dietitian, create a meal plan for the following patient:\n"
                "Patient Data: {patient}\n\n"
                "Risk Result: {risk_result}\n\n"
                "Based on the following biomedical evidence:\n{context}\n\n"
                "Provide structured dietary recommendations."
            )
        ),
        "Fitness Expert": PromptTemplate(
            input_variables=['patient', 'context', 'risk_result'],
            template=(
                "As a fitness expert, create a weekly exercise plan:\n"
                "Patient Data: {patient}\n\n"
                "Risk Result: {risk_result}\n\n"
                "Based on the following biomedical evidence:\n{context}\n\n"
                "Provide structured exercise recommendations."
            )
        )
    }

    expert_recommendations = {}
    for expert, prompt in expert_prompts.items():
        expert_chain = LLMChain(llm=llm, prompt=prompt)
        expert_recommendations[expert] = expert_chain.run(
            patient=str(patient_data), context=context, risk_result=str(risk_result)
        )
    
    return expert_recommendations
              
# Generate Final Consolidated Recommendation
def get_final_recommendation(patient_data, expert_recommendations, risk_result):
    meta_agent_prompt = PromptTemplate(
        input_variables=['endocrinologist', 'dietitian', 'fitness', 'patient', 'risk_result'],
        template=(
            "You are a healthcare consultant consolidating expert recommendations.\n"
            "Patient Data: {patient}\n\n"
            "Risk Result: {risk_result}\n\n"
            "**Expert Recommendations:**\n\n"
            "**Endocrinologist Recommendation:**\n{endocrinologist}\n\n"
            "**Dietitian Recommendation:**\n{dietitian}\n\n"
            "**Fitness Expert Recommendation:**\n{fitness}\n\n"
            "Create a final health plan integrating all recommendations."
        )
    )

    meta_agent_chain = LLMChain(llm=llm, prompt=meta_agent_prompt)

    final_recommendation = meta_agent_chain.run(
        endocrinologist=expert_recommendations["Endocrinologist"],
        dietitian=expert_recommendations["Dietitian"],
        fitness=expert_recommendations["Fitness Expert"],
        patient=str(patient_data),
        risk_result=str(risk_result)
    )

    return final_recommendation

# FastAPI Route for Recommendations
@app.post("/recommendations")
async def get_recommendations(patient: PatientData):
    try:
        patient_data = {
            key: float(value) if isinstance(value, (int, float)) or value.strip() else 0.0
            for key, value in patient.dict().items()
        }
        logger.info(f"Received patient data for recommendations: {patient_data}")

        # Use existing prediction function to get risk result
        risk_result = predict_diabetes_risk(patient_data)
        logger.info(f"Risk Prediction: {risk_result}")

        # Generate expert recommendations
        expert_recommendations = get_expert_recommendations(patient_data, risk_result)
        logger.info(f"Expert Recommendations: {expert_recommendations}")

        # Generate final consolidated recommendation
        final_recommendation = get_final_recommendation(patient_data, expert_recommendations, risk_result)

        return {
            "endocrinologistRecommendation": expert_recommendations["Endocrinologist"],
            "dietitianRecommendation": expert_recommendations["Dietitian"],
            "fitnessRecommendation": expert_recommendations["Fitness Expert"],
            "finalRecommendation": final_recommendation
        }

    except Exception as e:
        logger.error(f"Error processing recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    try:
        # ✅ Clean `patient_data`: Convert empty strings to `0.0` and remove invalid characters
        cleaned_patient_data = {}
        for key, value in chat_request.patient_data.items():
            try:
                cleaned_value = str(value).strip().replace("`", "").replace("'", "")
                cleaned_patient_data[key] = float(cleaned_value) if cleaned_value else 0.0
            except ValueError:
                logger.error(f"Invalid patient data input for {key}: {value}")
                raise HTTPException(status_code=400, detail=f"Invalid input for {key}: {value}")

        # ✅ Ensure `recommendations` are valid strings
        cleaned_recommendations = {k: str(v) if isinstance(v, str) else "" for k, v in chat_request.recommendations.items()}

        # ✅ Validate `history`: Ensure every message contains `role` & `content`
        validated_history = []
        for msg in chat_request.history:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                validated_history.append(msg)
            else:
                logger.error(f"Invalid chat history entry: {msg}")
                raise HTTPException(status_code=400, detail="Invalid chat history format.")

        # ✅ Fix `risk_probability`: Convert from `"69.23%"` to `69.23`
        try:
            risk_probability = float(chat_request.risk_probability.strip().replace("%", ""))
        except ValueError:
            logger.error(f"Invalid risk probability: {chat_request.risk_probability}")
            raise HTTPException(status_code=400, detail=f"Invalid risk probability: {chat_request.risk_probability}")

        # ✅ Format history, patient data, and recommendations for LLM
        formatted_history = "\n".join(
            [f"**{msg['role'].capitalize()}**: {msg['content']}" for msg in validated_history]
        )
        formatted_patient_data = "\n".join([f"- {key}: {value}" for key, value in cleaned_patient_data.items()])
        formatted_recommendations = "\n".join([f"- {key}: {value}" for key, value in cleaned_recommendations.items()])

        # ✅ Generate response from LLM
        response = chat_chain.run(
            history=formatted_history,
            user_input=chat_request.user_input,
            patient_data=formatted_patient_data,
            recommendations=formatted_recommendations,
            predicted_risk=chat_request.predicted_risk,
            risk_probability=str(risk_probability)  # ✅ Ensure it's passed as a string, but cleaned
        )

        # ✅ Append assistant's response to chat history
        chat_request.history.append({"role": "assistant", "content": response})

        return {
            "response": response,
            "updated_history": chat_request.history
        }

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
        
        
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Ensure compatibility with Render
    uvicorn.run(app, host="0.0.0.0", port=port, timeout_keep_alive=300)
