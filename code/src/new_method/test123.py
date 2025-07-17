from camera_detect import camera_detect
import numpy as np
from utils_robot import mc  # 复用你已有的机械臂连接

# 1. 加载相机参数
camera_params = np.load("camera_params.npz")
mtx, dist = camera_params["mtx"], camera_params["dist"]

# 2. 初始化检测器（把 camera_id 换成你在第2步得到的编号）
cd = camera_detect(camera_id=20, marker_size=27, mtx=mtx, dist=dist)

# 3. 开始标定
print("🔧 开始手眼标定，请按终端提示操作！")
cd.Eyes_in_hand_calibration(mc)
print("✅ 标定完成，已保存 EyesInHand_matrix.json")