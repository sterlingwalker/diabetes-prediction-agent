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


# Define Chat Request Model
class ChatRequest(BaseModel):
    history: List[Dict[str, str]]  # Ensure a valid chat history structure
    user_input: str
    patient_data: Dict[str, Union[str, float]]
    recommendations: Dict[str, str]
    predicted_risk: str
    risk_probability: str  # Expecting a stringified float (e.g., "69.23")



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

def predict_diabetes_risk(patient_data: dict, compute_shap: bool = True):
    try:
        # Convert patient data to DataFrame
        patient_df = pd.DataFrame([patient_data])

        # Ensure all expected features exist in DataFrame
        patient_df = patient_df.reindex(columns=all_features, fill_value=np.nan)

        # **Count non-null user-provided values (Before Imputation)**
        num_provided_features = patient_df.notna().sum(axis=1).iloc[0]
        logger.info(f"User-provided features count: {num_provided_features}")

        # **Model Selection (Based on User-Provided Data Only)**
        if num_provided_features <= 4:
            selected_model = lgbm_model
            model_used = "LightGBM"
            logger.info("Using LightGBM (≤4 Provided Features)")
        else:
            selected_model = tuned_rf_model
            model_used = "Tuned Random Forest"
            logger.info("Using Tuned Random Forest (≥5 Provided Features)")

        # **Handle Missing Values (AFTER Model Selection)**
        for feature in all_features:
            if patient_df[feature].isnull().all():  # If an entire column is missing
                if feature in numerical_features:
                    logger.info(f"Warning: {feature} is missing. Assigning default median: {default_medians[feature]}")
                    patient_df[feature] = default_medians[feature]
                elif feature in categorical_features:
                    logger.info(f"Warning: {feature} is missing. Assigning default mode: {default_modes[feature]}")
                    patient_df[feature] = default_modes[feature]

        # **Perform Median Imputation for Missing Numerical Features**
        num_imputer = SimpleImputer(strategy='median')
        cat_imputer = SimpleImputer(strategy='most_frequent')

        if patient_df[numerical_features].isnull().any().any():
            patient_df[numerical_features] = num_imputer.fit_transform(patient_df[numerical_features])
        if patient_df[categorical_features].isnull().any().any():
            patient_df[categorical_features] = cat_imputer.fit_transform(patient_df[categorical_features])

        # **Ensure feature order matches model training**
        patient_df = patient_df[all_features]

        # **Prediction**
        risk = selected_model.predict(patient_df)[0]
        risk_probability = selected_model.predict_proba(patient_df)[:, 1][0] * 100

        result = {
            "predictedRisk": "Diabetes" if risk == 1 else "No Diabetes",
            "riskProbability": f"{risk_probability:.2f}%",
            "modelUsed": model_used
        }

        # **Compute SHAP Values ONLY if requested (i.e., from /predict API)**
        if compute_shap:
            shap_values, shap_base_value = compute_shap_values(selected_model, patient_df)
            shap_plot_base64 = compute_shap_plot(list(shap_values.values()), patient_df)

            result.update({
                "shapValues": shap_values,
                "shapBaseValue": shap_base_value,
                "shapPlot": shap_plot_base64
            })
        else:
            # Do not include SHAP values in /recommendations response
            result.update({
                "shapValues": {},
                "shapBaseValue": None,
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
        patient_data = {}
        for key, value in patient.model_dump().items():
            try:
                cleaned_value = str(value).strip().replace("`", "").replace("'", "")

                # Handle empty strings by setting them to NaN (Not 0.0)
                if cleaned_value == "":
                    patient_data[key] = np.nan  # Keeps missing values as NaN
                else:
                    patient_data[key] = float(cleaned_value)

            except ValueError:
                logger.error(f"Invalid input for {key}: {value}")
                raise HTTPException(status_code=400, detail=f"Invalid input for {key}: {value}")

        logger.info(f"Received patient data with defaults: {patient_data}")

        # **SHAP Computation Enabled (Default)**
        result = predict_diabetes_risk(patient_data, compute_shap=True)
        logger.info(f"Prediction result: {result}")

        return jsonable_encoder(result)  # Ensure JSON-serializable output

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
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


def compute_shap_plot(shap_values, patient_df):
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
            base_values=shap_values[0],   # Base value for individual prediction
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

@app.post("/recommendations")
async def get_recommendations(patient: PatientData):
    try:
        patient_data = {}
        for key, value in patient.model_dump().items():
            try:
                cleaned_value = str(value).strip().replace("`", "").replace("'", "")

                # Handle empty strings by setting them to NaN (Not 0.0)
                if cleaned_value == "":
                    patient_data[key] = np.nan  # Keeps missing values as NaN
                else:
                    patient_data[key] = float(cleaned_value)

            except ValueError:
                logger.error(f"Invalid input for {key}: {value}")
                raise HTTPException(status_code=400, detail=f"Invalid input for {key}: {value}")

        logger.info(f"Received patient data for recommendations: {patient_data}")

        # **SHAP Computation Disabled**
        risk_result = predict_diabetes_risk(patient_data, compute_shap=False)
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
        # Validate and Clean `patient_data`
        cleaned_patient_data = {}
        for key, value in chat_request.patient_data.items():
            try:
                cleaned_value = str(value).strip().replace("`", "").replace("'", "")
                cleaned_patient_data[key] = float(cleaned_value) if cleaned_value else 0.0
            except ValueError:
                logger.error(f"Invalid patient data input for {key}: {value}")
                raise HTTPException(status_code=400, detail=f"Invalid input for {key}: {value}")


        #  Ensure `recommendations` are strings
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
       # Format history, patient data, and recommendations for LLM
        formatted_history = "\n".join(
            [f"**{msg['role'].capitalize()}**: {msg['content']}" for msg in validated_history]
        )
        formatted_patient_data = "\n".join([f"- {key}: {value}" for key, value in cleaned_patient_data.items()])
        formatted_recommendations = "\n".join([f"- {key}: {value}" for key, value in cleaned_recommendations.items()])

        # Generate response from LLM
        response = chat_chain.run(
            history=formatted_history,
            user_input=chat_request.user_input,
            patient_data=formatted_patient_data,
            recommendations=formatted_recommendations,
            predicted_risk=chat_request.predicted_risk,
            risk_probability=risk_probability  #  Ensuring it's a valid number as a string
        )

        #  Append assistant's response to chat history
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
    port = int(os.environ.get("PORT", 8000))  # Ensure compatibility with Render
    uvicorn.run(app, host="0.0.0.0", port=port, timeout_keep_alive=300)
