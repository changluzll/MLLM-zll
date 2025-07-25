import json
import numpy as np
from utils_robot import *

# 从JSON文件中加载点的坐标
def load_points_from_json(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    points = data['seam_path']
    return points

# 将图像坐标转换为机械臂坐标
def image_to_robot_coords(points, calibration_points):
    # 标定两个点的图像坐标和机械臂坐标
    cali_1_im = calibration_points['cali_1_im']
    cali_1_mc = calibration_points['cali_1_mc']
    cali_2_im = calibration_points['cali_2_im']
    cali_2_mc = calibration_points['cali_2_mc']

    X_cali_im = [cali_1_im[0], cali_2_im[0]]
    X_cali_mc = [cali_1_mc[0], cali_2_mc[0]]
    Y_cali_im = [cali_2_im[1], cali_1_im[1]]
    Y_cali_mc = [cali_2_mc[1], cali_1_mc[1]]

    robot_points = []
    for point in points:
        X_im = point['x']
        Y_im = point['y']
        X_mc = int(np.interp(X_im, X_cali_im, X_cali_mc))
        Y_mc = int(np.interp(Y_im, Y_cali_im, Y_cali_mc))
        robot_points.append([X_mc, Y_mc])
    return robot_points

# 按距离排序点
def sort_points_by_distance(points, start_point):
    """
    按距离排序点，从起始点开始
    """
    sorted_points = []
    current_point = start_point
    remaining_points = points[:]

    while remaining_points:
        # 找到最近的点
        next_point = min(remaining_points, key=lambda p: np.linalg.norm(np.array(p) - np.array(current_point)))
        sorted_points.append(next_point)
        remaining_points.remove(next_point)
        current_point = next_point

    return sorted_points

# 机械臂按顺序移动到每个点
def move_along_path(robot_points, height_safe=230, height_work=90):
    for point in robot_points:
        X, Y = point
        print(f"移动到点: X={X}, Y={Y}")
        mc.send_coords([X, Y, height_safe, 0, 180, 90], 20, 0)  # 移动到安全高度
        time.sleep(4)
        mc.send_coords([X, Y, height_work, 0, 180, 90], 20, 0)  # 移动到工作高度
        time.sleep(4)
        mc.send_coords([X, Y, height_safe, 0, 180, 90], 20, 0)  # 返回安全高度
        time.sleep(4)

# 主函数
def main():
    # 加载点的坐标
    json_path = "line_coordinates.json"
    points = load_points_from_json(json_path)

    # 标定参数
    calibration_points = {
        'cali_1_im': [138, 339],  # 左下角，第一个标定点的像素坐标
        'cali_1_mc': [135.5, 20.6],  # 左下角，第一个标定点的机械臂坐标
        'cali_2_im': [369, 72],  # 右上角，第二个标定点的像素坐标
        'cali_2_mc': [231.7, 167.2]  # 右上角，第二个标定点的机械臂坐标
    }

    # 将图像坐标转换为机械臂坐标
    robot_points = image_to_robot_coords(points, calibration_points)

    # 按距离排序点
    start_point = [0, 0]  # 假设起始点是 [0, 0]
    sorted_robot_points = sort_points_by_distance(robot_points, start_point)

    # 机械臂按顺序移动到每个点
    move_along_path(sorted_robot_points)

if __name__ == "__main__":
    main()