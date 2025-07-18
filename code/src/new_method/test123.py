from utils_robot import eye2hand, mc

# 机械臂移动到拍照位姿
mc.send_angles([39.19, -4.39, -69.43, -10.63, 1.75, 80.77], 40)
import time; time.sleep(3)

# 拍照并识别
x_im = 390   # 图像中目标的像素x
y_im = 102  # 图像中目标的像素y
X_mc, Y_mc = eye2hand(x_im, y_im)

if X_mc is None:
    print("❌ 未识别到ArUco码")
else:
    print(f"🎯 机械臂目标坐标：X={X_mc}  Y={Y_mc}")
    # 移动到目标上方
    mc.send_coords([X_mc, Y_mc, 200, 0, 180, 90], 20, 0)