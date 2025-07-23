import cv2
import numpy as np
import json

def extract_ordered_line_coordinates(image_path, output_json_path, num_points=25):
    # 读取带有透明通道的图像
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ValueError("无法读取图像，请检查路径是否正确！")

    # 分离透明通道
    alpha_channel = image[:, :, 3]

    # 将透明通道转换为二值图像
    _, binary = cv2.threshold(alpha_channel, 1, 255, cv2.THRESH_BINARY)

    # 查找轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 假设最长的轮廓是目标线条
    if len(contours) == 0:
        raise ValueError("未检测到任何轮廓！")
    max_contour = max(contours, key=cv2.contourArea)

    # 提取轮廓上的点
    points = max_contour.reshape(-1, 2).tolist()

    # 如果点的数量超过指定数量，进行采样
    if len(points) > num_points:
        step = len(points) // num_points
        points = points[::step]
        # 确保最终有指定数量的点
        if len(points) < num_points:
            points.extend(points[-(num_points - len(points)):])
    # 如果点的数量不足指定数量，重复最后一个点直到达到指定数量
    while len(points) < num_points:
        points.append(points[-1])

    # 转换为 [x, y] 格式
    points = [[point[0], point[1]] for point in points]

    # 保存为JSON文件
    with open(output_json_path, 'w') as f:
        json.dump(points, f, indent=4)

    print(f"坐标已保存到 {output_json_path}")

# 示例用法
image_path = "pic2.png"  # 替换为你的图像路径
output_json_path = "line_coordinates.json"  # 输出的JSON文件路径
extract_ordered_line_coordinates(image_path, output_json_path)