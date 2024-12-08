import os
os.environ['GRPC_PYTHON_LOG_LEVEL'] = '5'  # Add this line before other imports
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./account.json"


import vertexai
import vertexai.generative_models


vertexai.init(project="learning-443314", location="us-central1")

model = vertexai.generative_models.GenerativeModel("gemini-1.5-flash")

response = model.generate_content("Hello, world!")
print(response.text)

