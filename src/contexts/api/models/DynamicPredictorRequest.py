from enum import Enum
from pydantic import BaseModel, validator


def es_convertible_a_float(cadena):
        try:
            float(cadena)
            return True
        except ValueError:
            return False

class DynamicPredictorRequest(BaseModel):
    petal_length: str
    petal_width: str
    sepal_length: str
    sepal_width: str

   

    @validator("petal_length")
    def validate_age(cls, petal_length):
        
        if not es_convertible_a_float(petal_length):
            raise ValueError("Invalid petal_length")
        return petal_length
    
    @validator("petal_width")
    def validate_age(cls, petal_width):
        
        if not es_convertible_a_float(petal_width):
            raise ValueError("Invalid petal_width")
        return petal_width
    
    @validator("sepal_length")
    def validate_age(cls, sepal_length):
        
        if not es_convertible_a_float(sepal_length):
            raise ValueError("Invalid sepal_length")
        return sepal_length
    
    @validator("sepal_width")
    def validate_age(cls, sepal_width):
        
        if not es_convertible_a_float(sepal_width):
            raise ValueError("Invalid sepal_width")
        return sepal_width

  