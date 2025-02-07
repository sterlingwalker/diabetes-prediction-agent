Setup python environment
python3 -m venv diabetesAgent
source diabetesAgent/bin/activate   
pip3 install imbalanced-learn
pip3 install langchain-community
pip3 install openai pandas scikit-learn shap
pip3 install "fastapi[standard]"
pip3 install pydantic

python3 train.py 

python3 main.py


openapi key