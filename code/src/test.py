import os
import requests
from alibabacloud_imageseg20191230.client import Client
from alibabacloud_imageseg20191230.models import SegmentCommonImageAdvanceRequest
from alibabacloud_tea_openapi.models import Config
from alibabacloud_tea_util.models import RuntimeOptions

# 硬编码AccessKey (根据您的要求)
access_key_id = 'LTAI5t6RfEbFF2zDnkmkiq37'
access_key_secret = 'dBotl7zyIa0vNpf9DELQywANURC2rm'

config = Config(
    access_key_id=access_key_id,
    access_key_secret=access_key_secret,
    endpoint='imageseg.cn-shanghai.aliyuncs.com',
    region_id='cn-shanghai'
)

segment_common_image_request = SegmentCommonImageAdvanceRequest()

# 处理本地图片
image_path = 'crack.png'
if os.path.exists(image_path):
    stream = open(image_path, 'rb')
    segment_common_image_request.image_urlobject = stream
else:
    print(f"图片文件 {image_path} 不存在，请确保文件在同一目录下。")
    exit()

segment_common_image_request.return_form = ''

runtime = RuntimeOptions()

try:
    # 初始化Client
    client = Client(config)
    response = client.segment_common_image_advance(segment_common_image_request, runtime)

    # 关键修复：适应大驼峰命名字段
    result = response.body.to_map()
    print("返回的原始结果：")
    print(result)

    # 调试信息 - 显示实际字段结构
    print("\n返回结果字段分析：")
    print(f"- 顶级字段: {list(result.keys())}")
    if 'Data' in result:
        print(f"- Data字段包含: {list(result['Data'].keys())}")

    # 修复后的字段访问逻辑 - 使用大驼峰命名
    if isinstance(result, dict) and 'Data' in result and 'ImageURL' in result['Data']:
        image_url = result['Data']['ImageURL']
        print(f"获取到图片URL: {image_url[:80]}...")  # 显示部分URL避免过长输出

        # 检查URL是否临时链接
        if '?Expires=' in image_url:
            print("检测到临时URL(2小时内有效)，立即下载...")

        # 下载图片
        try:
            print("正在下载分割结果图片...")
            download_response = requests.get(image_url, timeout=15)

            if download_response.status_code == 200:
                with open('segmented_image.png', 'wb') as f:
                    f.write(download_response.content)
                print("图片已成功保存到: segmented_image.png")
            else:
                print(f"下载失败! HTTP状态码: {download_response.status_code}")

        except requests.Timeout:
            print("下载超时！请检查网络或重试")
        except Exception as download_error:
            print(f"下载过程中发生错误: {str(download_error)}")

    else:
        print("\nERROR: 返回结果结构异常")
        print("实际返回键值:", list(result.keys()))
        if 'Data' in result:
            print("Data字段中的键:", list(result['Data'].keys()))

except Exception as api_error:
    print("\nAPI调用发生错误:")
    print(api_error)

    # 提取详细错误信息
    error_details = []
    for attr in ['code', 'message', 'data']:
        if hasattr(api_error, attr):
            error_details.append(f"{attr}: {getattr(api_error, attr)}")

    if error_details:
        print("错误详情:\n" + "\n".join(error_details))

finally:
    # 确保关闭文件流
    if 'stream' in locals() and stream and not stream.closed:
        stream.close()
        print("已关闭图片文件流")