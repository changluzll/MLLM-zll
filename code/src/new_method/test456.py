from camera_detect import camera_detect
import numpy as np
from utils_robot import mc

# 1. 相机参数
camera_params = np.load("camera_params.npz")
mtx, dist = camera_params["mtx"], camera_params["dist"]

# 2. 初始化检测器（相机编号、ArUco边长 mm）
cd = camera_detect(20, 100, mtx, dist)

# 3. 开始手眼标定（完成后自动生成 EyesInHand_matrix.json）
print("🔧 开始手眼标定，请按提示操作！")
cd.Eyes_in_hand_calibration(mc)