import logging

import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
import os, uuid
from werkzeug.utils import secure_filename

def main(req: func.HttpRequest) -> func.HttpResponse:
    image = req.files.to_dict()['file']
    logging.info(type(image))
    logging.info(image)

    # image = req.files['image']
    # image.save(f"./static/{secure_filename(image.filename)}")
    # imageFilePath = f"./static/{secure_filename(image.filename)}"

    connect_str = 'DefaultEndpointsProtocol=https;AccountName=qhcustomvisionstorage;AccountKey=x6NgT9Z8yB+/UC93j5yUntldQy6IU6X61idFcCsSv45xsLqWLGPk9A4Unr3iXa9FriHOV2awfBlkvI6KoMqG2g==;EndpointSuffix=core.windows.net'
        

    try:
        logging.info("Azure Blob Storage v" + __version__ + " - Python quickstart sample")
            
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        container_name = str('testcontainer')


        # Create a blob client using the local file name as the name for the blob
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=image.filename)

        logging.info("\nUploading to Azure Storage as blob:\n\t" + image.filename)

        
        blob_client.upload_blob(image)


    except Exception as ex:
        print('Exception:')
        print(ex)

    baseURL = 'https://qhcustomvisionstorage.blob.core.windows.net/testcontainer/'
    url = baseURL+image.filename

    return func.HttpResponse(url,
              status_code=200
    )
