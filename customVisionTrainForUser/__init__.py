import logging
import json
from sys import set_coroutine_origin_tracking_depth
import requests
from lxml import etree
import re
import time

import azure.functions as func
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry
import os, time, uuid

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }

def main(req: func.HttpRequest) -> func.HttpResponse:

    img_list = json.loads(req.params.get("img_list"))
    imgCount = len(img_list)
    tagname = req.params.get("tagname")
    openid = req.params.get("openid")
    logging.info(openid)
    userInfo = json.loads(req.params.get("userInfo"))
    timestamp = req.params.get("timestamp")

    ENDPOINT = "https://qhvolleycustomimage.cognitiveservices.azure.com/"
    # ENDPOINT = os.environ["customvisionEndpoint"]
    logging.info(ENDPOINT)
    training_key = "61f871af9e754215a3a5e40532d48b9e"
    # training_key = os.environ["customvisiontrainkey"]
    logging.info(training_key)

    # 创建对象
    credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
    trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

    # 生成project对象（已创建）
    projects = trainer.get_projects()
    project_name = "qhVolleyEvent"
    project = [project for project in projects if project.name == project_name][0]

    # 生成tag对象（若有则创建，若没有则添加）
    remote_tags = trainer.get_tags(project.id)
    
    tagId_lst = []
    isNewTag = True
    for remote_tag in remote_tags:
        if remote_tag.name == tagname:
            tagId = remote_tag.id
            isNewTag = False
            break
    if isNewTag:
        tag = trainer.create_tag(project.id, tagname)
        tagId = tag.id

    # 上传图片（对应tag）
    image_lst = []
    for img in img_list:
        image_lst.append(ImageUrlCreateEntry( url=img, tag_ids = tagId))

    logging.info(len(image_lst))

    result = trainer.create_images_from_urls(project.id, ImageFileCreateBatch(images=image_lst))

    # 存入db
    DBpwd = os.environ["DBpwd"]
    cnx = mysql.connector.connect(user="qinghan123", password=DBpwd, host="qh-mysql-flex-1.mysql.database.azure.com", port=3306, database='qhvolley',  ssl_verify_cert=False)
    cursor = get_cursor(cnx)

    cursor.execute(
                    'INSERT INTO qhvolleytraining (openid, tagname, imgList, userInfo, timestamp, imgCount,)'
                    ' VALUES (%s, %s, %s, %s, %s, %s)',
                    (openid, tagname, json.dumps(imgList), json.dumps(userInfo), timestamp, imgCount)
    )
    cnx.commit()
    cursor.close()
    cnx.close()

    return func.HttpResponse( "上传成功", status_code=200)