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
from mcp import MCPRequest, MCPResponse, handle_mcp_action, current_model_override

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
    PatientName: str = "" 
    Glucose: Union[float, str] = 0.0
    BloodPressure: Union[float, str] = 0.0
    BMI: Union[float, str] = 0.0
    Age: Union[float, str] = 0.0
    Gender: Union[float, str] = 0.0
    Ethnicity: Union[float, str] = 0.0


# Define feature sets
all_features = ['Glucose', 'BMI', 'Age', 'Ethnicity', 'BloodPressure', 'Gender']
numerical_features = ['Glucose', 'BMI', 'Age', 'BloodPressure']
categorical_features = ['Ethnicity', 'Gender']

# Default Median Values (Replace with Dataset Medians)
default_medians = {
    'Glucose': 100,  
    'BMI': 20,
    'Age': 30,
    'BloodPressure': 70
}

# Default Most Frequent Values for Categorical Features (Replace with Dataset Modes)
default_modes = {
    'Ethnicity': 3,  
    'Gender': 1      
}

# Load FAISS Indexes with Enhanced Debugging
faiss_base_path = os.getcwd()  # Ensure FAISS index path is set correctly
openai_embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

vectorstores = {}

faiss_categories = ["Endocrinology", "Dietitian", "Exercise"]

for category in faiss_categories:
    index_path = os.path.join(faiss_base_path, f"faiss_{category.lower()}")
    
    try:
        logger.info(f"Loading FAISS index for {category} from {index_path} ...")
        vectorstores[category] = FAISS.load_local(index_path, openai_embeddings, allow_dangerous_deserialization=True)
        logger.info(f" Successfully loaded FAISS index for {category}.")
    except FileNotFoundError:
        logger.error(f" FAISS index not found for {category} at {index_path}. Ensure the index is correctly saved.")
    except Exception as e:
        logger.error(f" Failed to load FAISS index for {category}: {str(e)}")

def convert_categorical_values(patient_data):
    """
    Converts categorical numerical values (Gender, Ethnicity) into human-readable strings.
    This function should be used AFTER running `predict_diabetes_risk()`, where the categorical
    variables are initially used as numerical inputs for ML models.
    """
    gender_map = {
        0: "Female",
        1: "Male"
    }
    
    ethnicity_map = {
        1: "Mexican American",
        2: "Other Hispanic",
        3: "Non-Hispanic White",
        4: "Non-Hispanic Black",
        6: "Non-Hispanic Asian",
        7: "Other Race - Including Multi-Racial",
        8: "American Indian"
    }

    # Convert Gender
    if "Gender" in patient_data:
        patient_data["Gender"] = gender_map.get(int(patient_data["Gender"]), "Unknown")

    # Convert Ethnicity
    if "Ethnicity" in patient_data:
        patient_data["Ethnicity"] = ethnicity_map.get(int(patient_data["Ethnicity"]), "Unknown")

    return patient_data  # Return updated dictionary

def get_guideline_evidence(patient_data, risk_result, category):
    """
    Retrieves the most relevant guidelines based on whether the patient has diabetes (yes/no).
    Adds detailed logging to debug FAISS retrieval issues.
    """
    if category not in vectorstores:
        logger.warning(f"⚠FAISS index for {category} is missing. Skipping retrieval.")
        return "No specific guidelines found, but consider best practices in the field."

    diabetes_status = "diabetes" if risk_result["predictedRisk"] == "Diabetes" else "no diabetes"
    query = f"diabetes treatment guidelines {diabetes_status}"
    
    logger.info(f"Retrieving FAISS guidelines for {category} using query: '{query}'")

    try:
        retriever = vectorstores[category].as_retriever(search_type="similarity", search_kwargs={"k": 3})
        retrieved_docs = retriever.invoke(query)
        
        if not retrieved_docs:
            logger.warning(f" No FAISS guidelines found for {category} using query: '{query}'")
            return "No specific guidelines found, but consider best practices in the field."

        logger.info(f"Retrieved {len(retrieved_docs)} guideline(s) for {category}.")
        return "\n".join([doc.page_content for doc in retrieved_docs])

    except Exception as e:
        logger.error(f" FAISS retrieval error for {category}: {str(e)}")
        return "Error retrieving guidelines. Please consult a healthcare provider."
        

# Define Chat Request Model
class ChatRequest(BaseModel):
    history: List[Dict[str, str]]
    user_input: str
    patient_data: Dict[str, Union[str, float]] 
    recommendations: Dict[str, str]
    predicted_risk: str
    risk_probability: str

# Load the LightGBM and Random Forest models
try:
    lgbm_model = joblib.load("lightgbm_model.pkl")
    tuned_rf_model = joblib.load("tuned_rf_model.pkl")
except Exception as e:
    logger.error("Error loading models: %s", str(e))
    raise Exception("Error loading LightGBM or Random Forest models.") from e


llm = ChatOpenAI(temperature=0.4, openai_api_key=openai_api_key) 


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

import joblib

# Load the scaler used during training
scaler_path = "scaler.pkl"
if os.path.exists(scaler_path):
    scaler = joblib.load(scaler_path)
    logger.info("Loaded saved StandardScaler for inference.")
else:
    logger.error("Scaler file not found. Ensure 'scaler.pkl' is available.")
    raise FileNotFoundError("Scaler file not found!")
def predict_diabetes_risk(patient_data: dict, compute_shap: bool = True):
    try:
        # Convert patient data to DataFrame
        patient_df = pd.DataFrame([patient_data])

        # **Retrieve Trained Feature Order**
        trained_feature_order = getattr(tuned_rf_model, "feature_names_in_", all_features)
        logger.info(f"Expected feature order from trained model: {trained_feature_order}")

        # **Ensure 'Glucose_BMI_Ratio' Exists If Trained With It**
        if "Glucose_BMI_Ratio" in trained_feature_order:
            patient_df["Glucose_BMI_Ratio"] = patient_df["Glucose"] / (patient_df["BMI"] + 1e-6)
        else:
            patient_df = patient_df.drop(columns=["Glucose_BMI_Ratio"], errors="ignore")

        # **Ensure All Expected Features Exist & Maintain Order**
        patient_df = patient_df.reindex(columns=trained_feature_order, fill_value=0.0)

        # **Select Model Based on Provided Features or MCP override**
        num_provided_features = patient_df.notna().sum(axis=1).iloc[0]
        logger.info(f"User-provided features count: {num_provided_features}")

        if current_model_override == "lightgbm":
            selected_model = lgbm_model
            model_used = "LightGBM"
            apply_scaling = True
            logger.info("Using LightGBM (MCP override)")
        elif current_model_override == "random_forest":
            selected_model = tuned_rf_model
            model_used = "Tuned Random Forest"
            apply_scaling = False
            logger.info("Using Tuned Random Forest (MCP override)")
        else:
            if num_provided_features <= 4:
                selected_model = lgbm_model
                model_used = "LightGBM"
                apply_scaling = True  # LightGBM was trained on scaled data
                logger.info("Using LightGBM (≤4 Provided Features)")
            else:
                selected_model = tuned_rf_model
                model_used = "Tuned Random Forest"
                apply_scaling = False  # RF was trained on raw (unscaled) data
                logger.info("Using Tuned Random Forest (≥5 Provided Features)")

        # **Apply Scaling Only to Numerical Features When Needed**
        numerical_features_for_scaling = [
            feat for feat in trained_feature_order if feat in numerical_features
        ]

        if apply_scaling:
            patient_df[numerical_features_for_scaling] = scaler.transform(patient_df[numerical_features_for_scaling])
            logger.info("Applied scaling to numerical features")
        else:
            logger.info("Skipping feature scaling for Random Forest.")

        # **Ensure Categorical Features Remain Integers**
        patient_df["Gender"] = patient_df["Gender"].astype(int)
        patient_df["Ethnicity"] = patient_df["Ethnicity"].astype(int)

        # **Ensure Feature Order Matches Training**
        patient_df = patient_df.reindex(columns=trained_feature_order, fill_value=0.0)
        logger.info(f"Final input feature order for prediction: {patient_df.columns.tolist()}")

        # **Make Prediction**
        risk = selected_model.predict(patient_df)[0]
        risk_probability = selected_model.predict_proba(patient_df)[:, 1][0] * 100

        result = {
            "predictedRisk": "Diabetes" if risk == 1 else "No Diabetes",
            "riskProbability": f"{risk_probability:.2f}%",
            "modelUsed": model_used
        }

        # **Compute SHAP Values ONLY if requested**
        shap_values, shap_base_value = compute_shap_values(selected_model, patient_df)
        if compute_shap:
            shap_plot_base64 = compute_shap_plot(list(shap_values.values()), shap_base_value, patient_df)

            result.update({
                "shapValues": shap_values,
                "shapBaseValue": shap_base_value,
                "shapPlot": shap_plot_base64
            })
        else:
            result.update({
                "shapValues": shap_values,
                "shapBaseValue": shap_base_value,
                "shapPlot": None
            })

        return result

    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        return {
            "predictedRisk": "Error",
            "riskProbability": "N/A",
            "modelUsed": "N/A",
            "shapValues": {},
            "shapBaseValue": None,
            "shapPlot": None,
            "error": str(e)
        }


from fastapi.encoders import jsonable_encoder


@app.post("/predict")
async def predict(patient: PatientData):
    try:
        # Exclude PatientName from numeric conversion
        patient_data = {
            k: float(v) if k != "PatientName" and str(v).strip() else np.nan 
            for k, v in patient.model_dump().items()
        }

        logger.info(f"Received prediction request for patient: {patient.PatientName}")

        result = predict_diabetes_risk(patient_data, compute_shap=True)
        logger.info(f"Prediction result for {patient.PatientName}: {result}")

        return result

    except Exception as e:
        logger.error(f"Error processing request for {patient.PatientName}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))  
        
def compute_shap_values(model, patient_df):
    try:
        # Extract model from pipeline if needed
        if isinstance(model, Pipeline):
            logger.info("Extracting classifier from pipeline for SHAP analysis...")
            model = model.named_steps['clf']

        # Initialize SHAP Explainer
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(patient_df)

        #  Debugging Logs
        logger.info(f"Raw SHAP values type: {type(shap_values)}")
        logger.info(f"SHAP values shape (before processing): {np.array(shap_values).shape}")
        logger.info(f"SHAP expected value type: {type(explainer.expected_value)}")

        # Handle Multi-Class Output (Fix for Random Forest)
        if isinstance(shap_values, list) and len(shap_values) == 2:  
            logger.info("Detected binary classification model with two SHAP value outputs.")
            shap_value_for_class_1 = shap_values[1]  # Extract SHAP values for Class 1 (Diabetes)
            shap_base_value = explainer.expected_value[1]  # Extract base value for Class 1
        else:
            logger.info("Detected model returning a single SHAP value array.")
            shap_value_for_class_1 = shap_values
            shap_base_value = explainer.expected_value

        #  Handle Multi-Output SHAP (Fix for RF)
        if isinstance(shap_value_for_class_1, np.ndarray) and len(shap_value_for_class_1.shape) > 2:
            logger.info("Multi-output detected! Selecting second class (diabetes).")
            shap_value_for_class_1 = shap_value_for_class_1[:, :, 1]  # Select **Class 1 contributions**

        #  Extract Correct SHAP Base Value
        if isinstance(shap_base_value, np.ndarray):  
            logger.info(f"SHAP Base Value Array Detected: {shap_base_value}")
            shap_base_value = float(shap_base_value[1])  # Use **second index for Class 1**

        # Convert SHAP values to dictionary mapping feature names
        shap_values_dict = {feature: float(value) for feature, value in zip(patient_df.columns, shap_value_for_class_1[0])}

        #  Debugging: Log final values
        logger.info(f"Processed SHAP values mapping: {shap_values_dict}")
        logger.info(f"Final SHAP Base Value: {shap_base_value}")

        return shap_values_dict, shap_base_value
    except Exception as e:
        logger.error(f" Error computing SHAP values: {str(e)}")
        return {}, None  # Prevents pipeline failure        


def compute_shap_plot(shap_values, shap_base_value, patient_df):
    """
    Generates a SHAP Waterfall plot and returns it as a base64 string.
    Ensures compatibility with LightGBM & Random Forest models.
    """
    try:
        # **Convert list of shap values to NumPy array**
        shap_values_array = np.array(shap_values).reshape(1, -1)

        # **Initialize Figure**
        fig, ax = plt.subplots(figsize=(8, 6))

        # **Create SHAP Waterfall Plot**
        shap.waterfall_plot(shap.Explanation(
            values=shap_values_array[0],  # Use the first row
            base_values=shap_base_value,   # Base value for individual prediction
            data=patient_df.iloc[0],      # Feature values
            feature_names=patient_df.columns
        ))

        # **Save the plot to a Bytes buffer**
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close(fig)  # **Close the figure to free memory**
        buf.seek(0)

        # **Encode the image as a base64 string**
        shap_plot_base64 = base64.b64encode(buf.read()).decode("utf-8")

        return shap_plot_base64
    except Exception as e:
        logger.error(f"Error generating SHAP plot: {str(e)}")
        return None  # Return None instead of breaking the pipeline
       


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

llm = ChatOpenAI(temperature=0.4, openai_api_key=openai_api_key)


# Biomedical Evidence Fetching Function
def get_biomedical_evidence(patient_data):
    query_parts = ["diabetes treatment"]
    if patient_data.get("Glucose"):
        query_parts.append(f"glucose {patient_data['Glucose']}")
    if patient_data.get("BMI"):
        query_parts.append(f"BMI {patient_data['BMI']}")
    
    query = " ".join(query_parts)
    logger.info(f" Searching PubMed for: {query}")

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




def create_dynamic_context(patient_data, risk_result, guideline_evidence):
    return (
        f"**Patient Details:**\n"
        f"- Age: {patient_data.get('Age', 'Unknown')}\n"
        f"- BMI: {patient_data.get('BMI', 'Unknown')}\n"
        f"- Glucose: {patient_data.get('Glucose', 'Unknown')}\n"
        f"- Diabetes Prediction: {risk_result.get('predictedRisk', 'Unknown')} "
        f"({risk_result.get('riskProbability', 'N/A')})\n\n"
        "**Relevant Clinical Guidelines (FAISS Retrieval):**\n" + guideline_evidence
    )

async def get_expert_recommendations(patient_data, risk_result):
    guideline_evidence = {
        "Endocrinology": get_guideline_evidence(patient_data, risk_result, "Endocrinology"),
        "Dietitian": get_guideline_evidence(patient_data, risk_result, "Dietitian"),
        "Exercise": get_guideline_evidence(patient_data, risk_result, "Exercise")
    }

    context = create_dynamic_context(patient_data, risk_result, "\n".join(guideline_evidence.values()))

    expert_prompts = {
        "Endocrinologist": PromptTemplate(
            input_variables=['patient', 'context', 'risk_result'],
            template=(
                "As an endocrinologist, provide a diabetes treatment plan.\n"
                "Patient Data: {patient}\n\n"
                "Risk Result: {risk_result}\n\n"
                "Based on the following clinical guidelines:\n{context}\n\n"
                "Provide a structured treatment plan."
                "Respond in markup format"
            )
        ),
        "Dietitian": PromptTemplate(
            input_variables=['patient', 'context', 'risk_result'],
            template=(
                "As a dietitian, create a meal plan for the following patient:\n"
                "Patient Data: {patient}\n\n"
                "Risk Result: {risk_result}\n\n"
                "Based on the following dietitian guidelines:\n{context}\n\n"
                "Provide structured dietary recommendations."
                "Respond in markup format"
            )
        ),
        "Fitness Expert": PromptTemplate(
            input_variables=['patient', 'context', 'risk_result'],
            template=(
                "As a fitness expert, create a weekly exercise plan:\n"
                "Patient Data: {patient}\n\n"
                "Risk Result: {risk_result}\n\n"
                "Based on the following exercise guidelines:\n{context}\n\n"
                "Provide structured exercise recommendations."
                "Respond in markup format"                
            )
        )
    }

    llm = ChatOpenAI(model_name="gpt-4", temperature=0.3)

    async def fetch_recommendation(expert, prompt):
        try:
            expert_chain = LLMChain(llm=llm, prompt=prompt)
            return expert, await expert_chain.arun(
                patient=str(patient_data),
                context=context,
                risk_result=str(risk_result)
            )
        except Exception as e:
            logger.error(f" Error in LLM chain for {expert}: {str(e)}")
            return expert, "Error generating recommendation."

    results = await asyncio.gather(*[fetch_recommendation(expert, prompt) for expert, prompt in expert_prompts.items()])
    
    expert_recommendations = {expert: recommendation for expert, recommendation in results}
    logger.info(f" Expert Recommendations: {expert_recommendations}")
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
            "First explain the patients SHAP values and meaning and then create integrated final health plan summarizing all recommendations."
            "Respond in markup format"            
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


@app.post("/recommendations")
async def get_recommendations(patient: PatientData):
    try:
        # Exclude PatientName from numerical conversion
        patient_data = {
            k: float(v) if k != "PatientName" and str(v).strip() else np.nan 
            for k, v in patient.model_dump().items()
        }

        logger.info(f"Received recommendation request for patient: {patient.PatientName}")

        risk_result = predict_diabetes_risk(patient_data, compute_shap=False)
        logger.info(f"Risk Prediction for {patient.PatientName}: {risk_result}")

        # **Convert Categorical Variables to Strings AFTER Prediction**
        cleaned_patient_data = convert_categorical_values(patient_data)

        expert_recommendations = await get_expert_recommendations(cleaned_patient_data, risk_result)

        # Log FAISS retrieval issues explicitly
        if not expert_recommendations:
            logger.warning("Expert recommendations returned None or empty.")
            expert_recommendations = {
                "Endocrinologist": "No recommendations available.",
                "Dietitian": "No recommendations available.",
                "Fitness Expert": "No recommendations available."
            }

        final_recommendation = get_final_recommendation(patient_data, expert_recommendations, risk_result)

        return {
            "endocrinologistRecommendation": expert_recommendations.get("Endocrinologist", "No data"),
            "dietitianRecommendation": expert_recommendations.get("Dietitian", "No data"),
            "fitnessRecommendation": expert_recommendations.get("Fitness Expert", "No data"),
            "finalRecommendation": final_recommendation
        }

    except Exception as e:
        logger.error(f"Error processing recommendations for {patient.PatientName}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mcp", response_model=MCPResponse)
async def mcp_endpoint(request: MCPRequest):
    try:
        data = handle_mcp_action(request.action, request.parameters)
        return MCPResponse(status="ok", data=data)
    except Exception as e:
        return MCPResponse(status="error", error=str(e))


@app.post("/chat")
async def chat(chat_request: ChatRequest):
    try:
        # Exclude PatientName from numerical conversion
        cleaned_patient_data = {}
        for key, value in chat_request.patient_data.items():
            try:
                if key == "PatientName":
                    cleaned_patient_data[key] = str(value).strip()
                else:
                    cleaned_value = str(value).strip().replace("`", "").replace("'", "")
                    cleaned_patient_data[key] = float(cleaned_value) if cleaned_value else 0.0
            except ValueError:
                logger.error(f"Invalid patient data input for {key}: {value}")
                raise HTTPException(status_code=400, detail=f"Invalid input for {key}: {value}")

        # Ensure `recommendations` are strings
        cleaned_recommendations = {k: str(v) if isinstance(v, str) else "" for k, v in chat_request.recommendations.items()}

        # Validate `history`
        validated_history = []
        for msg in chat_request.history:
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                validated_history.append(msg)
            else:
                logger.error(f"Invalid chat history entry: {msg}")
                raise HTTPException(status_code=400, detail="Invalid chat history format.")

        # Convert `risk_probability` to a float and back to a string
        try:
            risk_probability = str(float(chat_request.risk_probability.strip().replace("%", "")))
        except ValueError:
            logger.error(f"Invalid risk probability: {chat_request.risk_probability}")
            raise HTTPException(status_code=400, detail=f"Invalid risk probability: {chat_request.risk_probability}")

        # Enforcing System Prompt to Restrict Responses to Diabetes
        system_prompt = (
            "SYSTEM: You are a medical AI assistant strictly focused on Diabetes. "
            "Do not answer questions unrelated to Diabetes, even if asked. "
            "If a question is outside this scope, politely refuse to answer.\n\n"
        )

        # Format history, patient data, and recommendations for LLM
        formatted_history = "\n".join(
            [f"**{msg['role'].capitalize()}**: {msg['content']}" for msg in validated_history]
        )
        formatted_patient_data = "\n".join([f"- {key}: {value}" for key, value in cleaned_patient_data.items()])
        formatted_recommendations = "\n".join([f"- {key}: {value}" for key, value in cleaned_recommendations.items()])

        # Pass System Prompt as Context in LLM Response Generation
        response = chat_chain.run(
            history=f"{system_prompt}\n{formatted_history}",
            user_input=chat_request.user_input,
            patient_data=formatted_patient_data,
            recommendations=formatted_recommendations,
            predicted_risk=chat_request.predicted_risk,
            risk_probability=risk_probability
        )

        #  Append AI Response to Chat History
        chat_request.history.append({"role": "assistant", "content": response})

        return {
            "response": response,
            "updated_history": chat_request.history
        }

    except HTTPException as http_error:
        raise http_error
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Ensure compatibility with Render
    uvicorn.run(app, host="0.0.0.0", port=port, timeout_keep_alive=300)
