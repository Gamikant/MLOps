import os
import numpy as np
import pickle
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from dense_neural_class import Dense_Neural_Diy  # Ensure proper import
import sys

sys.modules['__main__'].Dense_Neural_Diy = Dense_Neural_Diy

def load_model(filename: str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_dir, filename + '.pkl')
    
    with open(filepath, 'rb') as file:
        model_loaded = pickle.load(file)
    
    return model_loaded

model = load_model('model')

class Data(BaseModel):
    image_vector: List[float]

app = FastAPI()

@app.get('/')
def main():
    return {'message': 'Welcome to the Digit Prediction API!'}

@app.post('/predict')
def prediction(data: Data):
    image = np.array(data.image_vector).reshape(1, -1)
    result = model.predict(image)[0]
    return int(result)
