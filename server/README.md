#  Diabetes Prediction Agent - Server

This is the backend server for the **Diabetes Prediction Agent**, responsible for handling machine learning model predictions.

##  Setup & Installation


```sh
python3 -m venv diabetesAgent
source diabetesAgent/bin/activate

pip3 install imbalanced-learn
pip3 install langchain-community
pip3 install openai pandas scikit-learn shap
pip3 install "fastapi[standard]"
pip3 install pydantic
```

Make sure to set your OpenAI API key in the environment variables
```sh
export OPENAI_API_KEY="your-api-key-here"
```

### Model Training
```sh
python3 train.py
```

### Start the server

```sh
python3 main.py
```

### MCP Endpoint

The server exposes `/mcp` for Model Control Protocol operations. Example:

```sh
curl -X POST http://localhost:8080/mcp -H "Content-Type: application/json" \
    -d '{"action": "list_models"}'
```

Supported actions:

- `list_models` – return available model names.
- `switch_model` – set the active model using `{"model": "lightgbm"}` or `{"model": "random_forest"}`.
- `current_model` – display the currently active model.
- `metadata` – return both available models and current selection.
