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
