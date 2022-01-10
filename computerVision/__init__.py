import logging

import azure.functions as func
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

from array import array
import os
from PIL import Image
import sys
import time


def main(req: func.HttpRequest) -> func.HttpResponse:

    subscription_key = "55de653fcce94447a48fc719e7aa313b"
    endpoint = "https://qh-vision-linxin.cognitiveservices.azure.com/"

    computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


    remote_image_url = req.params.get('remote_image_url')

    '''
    Describe an Image - remote
    This example describes the contents of an image with the confidence score.
    '''
    print("===== Describe an image - remote =====")
    # Call API
    description_results = computervision_client.describe_image(remote_image_url )

    # Get the captions (descriptions) from the response, with confidence level
    logging.info("Description of remote image: ")
    if (len(description_results.captions) == 0):
        logging.info("No description detected.")
    else:
        for caption in description_results.captions:
            logging.info("'{}' with confidence {:.2f}%".format(caption.text, caption.confidence * 100))

    '''
    Categorize an Image - remote
    This example extracts (general) categories from a remote image with a confidence score.
    '''
    print("===== Categorize an image - remote =====")
    # Select the visual feature(s) you want.
    remote_image_features = ["categories"]
    # Call API with URL and features
    categorize_results_remote = computervision_client.analyze_image(remote_image_url , remote_image_features)

    # Print results with confidence score
    print("Categories from remote image: ")
    if (len(categorize_results_remote.categories) == 0):
        print("No categories detected.")
    else:
        for category in categorize_results_remote.categories:
            print("'{}' with confidence {:.2f}%".format(category.name, category.score * 100))

    '''
    Tag an Image - remote
    This example returns a tag (key word) for each thing in the image.
    '''
    print("===== Tag an image - remote =====")
    # Call API with remote image
    tags_result_remote = computervision_client.tag_image(remote_image_url )

    # Print results with confidence score
    print("Tags in the remote image: ")
    if (len(tags_result_remote.tags) == 0):
        print("No tags detected.")
    else:
        for tag in tags_result_remote.tags:
            print("'{}' with confidence {:.2f}%".format(tag.name, tag.confidence * 100))


    


    return func.HttpResponse("computer vision predict successfully!",
              status_code=200
    )
