from typing import Optional, Dict, List, Union, Any
from pydantic import BaseModel

try:
    from . import main           # when imported as server.mcp
except ImportError:  # pragma: no cover - fallback for direct execution
    import main                  # when imported as top-level module

# Available models that can be controlled via MCP
AVAILABLE_MODELS: Dict[str, str] = {
    "lightgbm": "LightGBM",
    "random_forest": "Tuned Random Forest",
}

# Holds the key of the currently selected model if overridden via MCP
current_model_override: Optional[str] = None

class MCPRequest(BaseModel):
    action: str
    # Allow any parameter types for actions that require complex payloads
    parameters: Optional[Dict[str, Any]] = None

# --- New/Modified Response Data Models ---

class ModelListResponseData(BaseModel):
    """Data model for 'list_models' action."""
    models: List[str] # This correctly expects a list of strings

class CurrentModelResponseData(BaseModel):
    """Data model for 'switch_model' and 'current_model' actions."""
    current_model: Optional[str]

class MetadataResponseData(BaseModel):
    """Data model for 'metadata' action."""
    available_models: Dict[str, str]
    current_model: Optional[str]

# Main Response Model - data field now uses Union to accept different data structures
class MCPResponse(BaseModel):
    status: str
    # 'data' can now be any of the specific Pydantic models defined above,
    # or a generic dictionary for other potential cases.
    data: Optional[Union[ModelListResponseData, CurrentModelResponseData, MetadataResponseData, Dict[str, Any]]] = None
    error: Optional[str] = None

# --- Original helper functions (no changes needed here) ---

def list_models() -> List[str]:
    return list(AVAILABLE_MODELS.values())

def switch_model(model_key: str) -> str:
    global current_model_override
    if model_key not in AVAILABLE_MODELS:
        raise ValueError("Unknown model")
    current_model_override = model_key
    return AVAILABLE_MODELS[model_key]

def get_current_model() -> Optional[str]:
    if current_model_override:
        return AVAILABLE_MODELS[current_model_override]
    return None

def get_metadata() -> Dict[str, Optional[str]]:
    return {
        "available_models": AVAILABLE_MODELS,
        "current_model": get_current_model(),
    }

# --- Modified handle_mcp_action to return Pydantic data models directly ---
# The return type hint is updated to reflect the Pydantic data models being returned.
async def handle_mcp_action(action: str, parameters: Optional[Dict[str, Any]] = None) -> Union[ModelListResponseData, CurrentModelResponseData, MetadataResponseData, Dict[str, Any]]:
    """
    Handles different MCP actions and returns the appropriate data for the response.
    Returns Pydantic model instances for clarity and validation.
    """
    if action == "list_models":
        return ModelListResponseData(models=list_models())
    if action == "switch_model":
        if not parameters or "model" not in parameters:
            raise ValueError("'model' parameter required")
        model_name = switch_model(parameters["model"])
        return CurrentModelResponseData(current_model=model_name)
    if action == "current_model":
        return CurrentModelResponseData(current_model=get_current_model())
    if action == "metadata":
        # get_metadata returns a Dict[str, Optional[str]]
        # We need to explicitly pass it to the MetadataResponseData Pydantic model
        metadata = get_metadata()
        return MetadataResponseData(
            available_models=metadata["available_models"],
            current_model=metadata["current_model"]
        )
    if action == "predict":
        if not parameters:
            raise ValueError("patient parameters required for predict")
        import numpy as np
        import asyncio
        patient = main.PatientData(**parameters)
        patient_dict = {
            k: float(v) if k != "PatientName" and str(v).strip() else np.nan
            for k, v in patient.model_dump().items()
        }
        return main.predict_diabetes_risk(patient_dict, compute_shap=True)
    if action == "recommendations":
        if not parameters:
            raise ValueError("patient parameters required for recommendations")
        import numpy as np
        import asyncio
        patient = main.PatientData(**parameters)
        patient_dict = {
            k: float(v) if k != "PatientName" and str(v).strip() else np.nan
            for k, v in patient.model_dump().items()
        }
        risk_result = main.predict_diabetes_risk(patient_dict, compute_shap=False)
        cleaned_patient = main.convert_categorical_values(patient_dict.copy())
        expert = await main.get_expert_recommendations(cleaned_patient, risk_result)
        final_rec = await main.get_final_recommendation(patient_dict, expert, risk_result)
        return {
            "endocrinologistRecommendation": expert.get("Endocrinologist", "No data"),
            "dietitianRecommendation": expert.get("Dietitian", "No data"),
            "fitnessRecommendation": expert.get("Fitness Expert", "No data"),
            "finalRecommendation": final_rec
        }
    if action == "chat":
        if not parameters:
            raise ValueError("chat parameters required")
        import asyncio
        chat_request = main.ChatRequest(**parameters)
        return await main.chat(chat_request)
    raise ValueError("Unsupported MCP action")

# --- Example of how this would be used in a web framework endpoint (e.g., FastAPI) ---
# This part is for demonstration and not part of the original script,
# but shows how to build the final MCPResponse.
def create_full_mcp_response(request_action: str, request_parameters: Optional[Dict[str, str]] = None) -> MCPResponse:
    """
    Helper function to wrap the action handling and produce a complete MCPResponse.
    """
    try:
        # Call the action handler which now returns a Pydantic data model or a dict
        data_payload = handle_mcp_action(request_action, request_parameters)

        # If data_payload is already a BaseModel, Pydantic handles its serialization.
        # Otherwise, if it's a plain dict, it will be used as is.
        return MCPResponse(status="success", data=data_payload)
    except ValueError as e:
        return MCPResponse(status="error", error=str(e))
    except Exception as e:
        # Catch any other unexpected errors
        return MCPResponse(status="error", error=f"An unexpected error occurred: {type(e).__name__} - {str(e)}")

# Example usage of the helper function:
if __name__ == "__main__":
    # Test list_models
    print("--- Testing list_models ---")
    response_list_models = create_full_mcp_response(action="list_models")
    print(response_list_models.model_dump_json(indent=2)) # Use .model_dump_json() for Pydantic v2+

    # Test switch_model
    print("\n--- Testing switch_model ---")
    response_switch_model = create_full_mcp_response(action="switch_model", parameters={"model": "lightgbm"})
    print(response_switch_model.model_dump_json(indent=2))

    # Test current_model
    print("\n--- Testing current_model ---")
    response_current_model = create_full_mcp_response(action="current_model")
    print(response_current_model.model_dump_json(indent=2))

    # Test metadata
    print("\n--- Testing metadata ---")
    response_metadata = create_full_mcp_response(action="metadata")
    print(response_metadata.model_dump_json(indent=2))

    # Test unsupported action
    print("\n--- Testing unsupported action ---")
    response_unsupported = create_full_mcp_response(action="unsupported_action")
    print(response_unsupported.model_dump_json(indent=2))

    # Test switch_model with missing parameter
    print("\n--- Testing switch_model missing parameter ---")
    response_missing_param = create_full_mcp_response(action="switch_model")
    print(response_missing_param.model_dump_json(indent=2))

    # Test switch_model with unknown model
    print("\n--- Testing switch_model unknown model ---")
    response_unknown_model = create_full_mcp_response(action="switch_model", parameters={"model": "unknown"})
    print(response_unknown_model.model_dump_json(indent=2))
