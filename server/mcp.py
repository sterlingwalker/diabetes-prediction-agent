from typing import Optional, Dict, List
from pydantic import BaseModel

# Available models that can be controlled via MCP
AVAILABLE_MODELS: Dict[str, str] = {
    "lightgbm": "LightGBM",
    "random_forest": "Tuned Random Forest",
}

# Holds the key of the currently selected model if overridden via MCP
current_model_override: Optional[str] = None

class MCPRequest(BaseModel):
    action: str
    parameters: Optional[Dict[str, str]] = None

class MCPResponse(BaseModel):
    status: str
    data: Optional[Dict[str, str]] = None
    error: Optional[str] = None

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

def handle_mcp_action(action: str, parameters: Optional[Dict[str, str]] = None) -> Dict[str, Optional[str]]:
    if action == "list_models":
        return {"models": list_models()}
    if action == "switch_model":
        if not parameters or "model" not in parameters:
            raise ValueError("'model' parameter required")
        model_name = switch_model(parameters["model"])
        return {"current_model": model_name}
    if action == "current_model":
        return {"current_model": get_current_model()}
    if action == "metadata":
        return get_metadata()
    raise ValueError("Unsupported MCP action")
