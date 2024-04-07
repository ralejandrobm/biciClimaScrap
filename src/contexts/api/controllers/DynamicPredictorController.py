import pandas as pd
from datetime import datetime
import pytz
import pickle

import src.contexts.utils.config as config
from src.contexts.api.models import DynamicPredictorRequest


class DynamicPredictorController:
    def execute(self, request: DynamicPredictorRequest):
        
        sepal_length=request.sepal_length
        sepal_width=request.sepal_width
       
        petal_length=request.petal_length
        petal_width=request.petal_width
        
        
        #contenedor linux
        model_path = "/app/assets/iris.pkcls"
        #local win
        #model_path = "assets\iris.pkcls"
        with open(model_path, "rb") as file:
            model = pickle.load(file)

        input_values = [sepal_length, sepal_width, petal_length, petal_width]
               
        predictions = model.predict_proba(
            [input_values]
        )

        predictions = predictions.tolist()
       

        return {"status": "OK", "result": predictions}

    