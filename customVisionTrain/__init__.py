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

    # 接收前端数据
    new_tags = json.loads(req.params.get("new_tag"))
    query = req.params.get("query")

    img_list = set_img_list(query)

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
    remote_tags = trainer.get_tags(project.id)
    
    tagId_lst = []
    for new_tag in new_tags:
        isNewTag = True
        for remote_tag in remote_tags:
            if remote_tag.name == new_tag:
                tag = remote_tag
                tagId_lst.append(tag.id)
                isNewTag = False
                break
        if isNewTag:
            tag = trainer.create_tag(project.id, new_tag)
            tagId_lst.append(tag.id)

    # 上传图片（对应tag）
    image_lst = []
    for img in img_list:
        image_lst.append(ImageUrlCreateEntry(url=img,tag_ids = tagId_lst))

    result = trainer.create_images_from_urls(project.id, ImageFileCreateBatch(images=image_lst))

    # 训练迭代器（时间稍长） 不提交训练
    # iteration = trainer.train_project(project.id)
    
    # while (iteration.status != "Completed"):
    #     iteration = trainer.get_iteration(project.id, iteration.id)
    #     logging.info("Training status: " + iteration.status)
    #     logging.info("Waiting 10 seconds...")
    #     time.sleep(10)

    return func.HttpResponse("custom vision train successfully!",
              status_code=200
    )

def set_img_list(query):
    url = 'https://cn.bing.com/images/async?q='+query+'&first=1&count=35&relp=50&scenario=ImageBasicHover&datsrc=N_I&layout=RowBased&mmasync=1'
    img_list = parse_img(url)
    url = 'https://cn.bing.com/images/async?q='+query+'&first=2&count=15&relp=50&scenario=ImageBasicHover&datsrc=N_I&layout=RowBased&mmasync=1'
    img_list = img_list + parse_img(url)
    logging.info(len(img_list))
    return img_list

def parse_img(url):
    response = requests.get(url, headers=headers)
    response.encoding = response.apparent_encoding
    data = response.content.decode('utf-8', 'ignore')
    html = etree.HTML(data)
    conda_list = html.xpath('//a[@class="iusc"]/@m')
    all_url = []    # 用来保存全部的url
    for i in conda_list:
        img_url = re.search('"murl":"(.*?)"', i).group(1)
        all_url.append(img_url)
    return all_url