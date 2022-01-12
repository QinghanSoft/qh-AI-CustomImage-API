import json
import logging

import azure.functions as func
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
import os, time, uuid

import requests


def main(req: func.HttpRequest) -> func.HttpResponse:
    
    imgUrl = req.params.get("imgUrl")

    data = { "Url" : imgUrl}

    res = requests.post("https://qhcustomvision-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/c220a5a0-a9a4-4b88-95f9-20cb5890b36d/classify/iterations/Iteration3/url",
        headers = {
            "Prediction-Key" : "1b732bcbe7444a5cadbcec8a99e19fc4",
            "Content-Type" : "application/json"
        },
        data = json.dumps(data)
    )

    return func.HttpResponse(res.text,
              status_code=200
    )
