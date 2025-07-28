# -*- coding: utf-8 -*-
# 引入依赖包
# pip install alibabacloud_imageseg20191230

import os
import io
from urllib.request import urlopen
from alibabacloud_imageseg20191230.client import Client
from alibabacloud_imageseg20191230.models import SegmentCommonImageAdvanceRequest
from alibabacloud_tea_openapi.models import Config
from alibabacloud_tea_util.models import RuntimeOptions

# 在程序内定义AccessKey ID和AccessKey Secret
access_key_id = 'LTAI5t6RfEbFF2zDnkmkiq37'  # 替换为你的AccessKey ID
access_key_secret = 'dBotl7zyIa0vNpf9DELQywANURC2rm'  # 替换为你的AccessKey Secret

config = Config(
    access_key_id=access_key_id,
    access_key_secret=access_key_secret,
    # 访问的域名。
    endpoint='imageseg.cn-shanghai.aliyuncs.com',
    # 访问的域名对应的region
    region_id='cn-shanghai'
)

segment_common_image_request = SegmentCommonImageAdvanceRequest()

# 场景一：文件在本地，与程序在同一目录下
image_path = 'SegmentCommonImage.png'  # 替换为你的图片文件名
if os.path.exists(image_path):
    stream = open(image_path, 'rb')
    segment_common_image_request.image_urlobject = stream
else:
    print(f"图片文件 {image_path} 不存在，请确保文件在同一目录下。")
    exit()

segment_common_image_request.return_form = 'crop'

runtime = RuntimeOptions()
try:
    # 初始化Client
    client = Client(config)
    response = client.segment_common_image_advance(segment_common_image_request, runtime)
    # 获取整体结果
    print(response.body)
except Exception as error:
    # 获取整体报错信息
    print(error)
    # 获取单个字段
    print(error.code)
    # tips: 可通过error.__dict__查看属性名称
finally:
    # 关闭流
    if 'stream' in locals() and not stream.closed:
        stream.close()