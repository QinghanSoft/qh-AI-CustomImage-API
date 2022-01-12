import logging
import json

import azure.functions as func
from azure.cognitiveservices.vision.customvision.training import CustomVisionTrainingClient
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from azure.cognitiveservices.vision.customvision.training.models import ImageFileCreateBatch, ImageFileCreateEntry, Region
from msrest.authentication import ApiKeyCredentials
from azure.cognitiveservices.vision.customvision.training.models import ImageUrlCreateEntry
import os, time, uuid



def main(req: func.HttpRequest) -> func.HttpResponse:

    # 接收前端数据
    img_list = json.loads(req.params.get("img_list"))
    new_tag = req.params.get("new_tag")

    # 密钥相关
    ENDPOINT = "https://qhcustomvision.cognitiveservices.azure.com/"
    training_key = "797c7b85242149339eb9c55d0583daf9"
    
    # 创建对象
    credentials = ApiKeyCredentials(in_headers={"Training-key": training_key})
    trainer = CustomVisionTrainingClient(ENDPOINT, credentials)

    # 生成project对象（已创建）
    projects = trainer.get_projects()
    project_name = "qh-car-model"
    project = [project for project in projects if project.name == project_name][0]

    # 生成tag对象（若有则创建，若没有则添加）
    tags = trainer.get_tags(project.id)
    
    isNewTag = True
    for tag in tags:
        if tag.name == new_tag:
            tag = [tag for tag in tags if tag.name == new_tag][0]
            isNewTag = False
            break

    if isNewTag:
        tag = trainer.create_tag(project.id, new_tag)

    # 上传图片（对应tag）
    image_lst = []
    for img in img_list:
        image_lst.append(ImageUrlCreateEntry(url=img,tag_ids=[tag.id]))

    result = trainer.create_images_from_urls(project.id, ImageFileCreateBatch(images=image_lst))

    # 训练迭代器（时间稍长）
    iteration = trainer.train_project(project.id)
    
    while (iteration.status != "Completed"):
        iteration = trainer.get_iteration(project.id, iteration.id)
        logging.info("Training status: " + iteration.status)
        logging.info("Waiting 10 seconds...")
        time.sleep(10)

    return func.HttpResponse("custom vision train successfully!",
              status_code=200
    )
