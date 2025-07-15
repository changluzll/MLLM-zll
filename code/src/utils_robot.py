# utils_robot.py
# 同济子豪兄 2024-05-22  2025-07-14 适配 MyCobot280 官方 API
# 启动并连接机械臂，封装常用动作

print('导入机械臂连接模块')

import os
import cv2
import numpy as np
import time
from pymycobot import MyCobot280
from pymycobot import PI_PORT, PI_BAUD

# ---------- 连接机械臂 ----------
mc = MyCobot280(PI_PORT, PI_BAUD)

# ---------- 官方 GPIO ----------
mc.gpio_init()          # 初始化 BCM 模式
PUMP_PIN  = 20          # 吸泵电磁阀
VALVE_PIN = 21          # 泄气阀门

# 设置引脚为输出（官方接口）
mc.set_gpio_out(PUMP_PIN,  "out")
mc.set_gpio_out(VALVE_PIN, "out")
mc.gpio_output(PUMP_PIN,  1)   # 默认关闭
mc.gpio_output(VALVE_PIN, 1)

# ---------- 常用动作 ----------
def back_zero():
    print('机械臂归零')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)

def relax_arms():
    print('放松机械臂关节')
    mc.release_all_servos()

def head_shake():
    mc.send_angles([0.87, -50.44, 47.28, 0.35, -0.43, -0.26], 70)
    time.sleep(1)
    for _ in range(2):
        mc.send_angle(5,  30, 80)
        time.sleep(0.5)
        mc.send_angle(5, -30, 80)
        time.sleep(0.5)
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(2)

def head_dance():
    mc.send_angles([0.87, -50.44, 47.28, 0.35, -0.43, -0.26], 70)
    time.sleep(1)
    angles_list = [
        [-0.17, -94.3, 118.91, -39.9, 59.32, -0.52],
        [67.85, -3.42, -116.98, 106.52, 23.11, -0.52],
        [-38.14, -115.04, 116.63, 69.69, 3.25, -11.6],
        [2.72, -26.19, 140.27, -110.74, -6.15, -11.25]
    ]
    for ang in angles_list:
        mc.send_angles(ang, 80)
        time.sleep(1.7)
    mc.send_angles([0, 0, 0, 0, 0, 0], 80)

def head_nod():
    mc.send_angles([0.87, -50.44, 47.28, 0.35, -0.43, -0.26], 70)
    for _ in range(2):
        mc.send_angle(4,  13, 70)
        time.sleep(0.5)
        mc.send_angle(4, -20, 70)
        time.sleep(1)
        mc.send_angle(4, 13, 70)
        time.sleep(0.5)
    mc.send_angles([0.87, -50.44, 47.28, 0.35, -0.43, -0.26], 70)

def move_to_coords(X=150, Y=-130, HEIGHT_SAFE=230):
    print(f'移动至指定坐标：X {X} Y {Y}')
    mc.send_coords([X, Y, HEIGHT_SAFE, 0, 180, 90], 20, 0)
    time.sleep(4)

def single_joint_move(joint_index, angle):
    print(f'关节 {joint_index} 旋转至 {angle} 度')
    mc.send_angle(joint_index, angle, 40)
    time.sleep(2)

def move_to_top_view():
    print('移动至俯视姿态')
    mc.send_angles([-62.13, 8.96, -87.71, -14.41, 2.54, -16.34], 10)
    time.sleep(3)

# ---------- 俯视图拍照 ----------
def top_view_shot(check=False):
    print('    移动至俯视姿态')
    move_to_top_view()

    cap = cv2.VideoCapture(0)
    cap.open(0)
    time.sleep(0.3)
    ret, img = cap.read()
    if not ret:
        raise RuntimeError("摄像头读取失败")
    os.makedirs("temp", exist_ok=True)
    cv2.imwrite('temp/vl_now.jpg', img)
    print('    保存至 temp/vl_now.jpg')

    cv2.imshow('top_view', img)
    if check:
        print('请确认拍照成功，按 c 继续，按 q 退出')
        while True:
            key = cv2.waitKey(10) & 0xFF
            if key == ord('c'):
                break
            if key == ord('q'):
                cv2.destroyAllWindows()
                raise KeyboardInterrupt("用户取消")
    else:
        cv2.waitKey(1)
    cap.release()
    cv2.destroyAllWindows()

# ---------- 手眼标定 ----------
def eye2hand(px, py):
    cali_1_im = [130, 290]
    cali_1_mc = [-21.8, -197.4]
    cali_2_im = [640, 0]
    cali_2_mc = [215, -59.1]

    x_mc = np.interp(px, [cali_1_im[0], cali_2_im[0]], [cali_1_mc[0], cali_2_mc[0]])
    y_mc = np.interp(py, [cali_2_im[1], cali_1_im[1]], [cali_2_mc[1], cali_1_mc[1]])
    return int(x_mc), int(y_mc)

# ---------- 吸泵搬运 ----------
def pump_move(xy_start, xy_end, z_safe=220, z_pick=90, z_place=90, speed=20):
    """
    使用官方吸泵接口 + GPIO 控制搬运
    xy_start / xy_end : [x, y] mm
    """
    # 设置队列模式
    mc.set_fresh_mode(0)

    # 起点上方
    mc.send_coords([*xy_start, z_safe, 0, 180, 90], speed, 0)
    time.sleep(4)

    # 官方 GPIO 控制吸泵
    mc.gpio_output(PUMP_PIN, 0)   # 吸泵 ON
    mc.gpio_output(VALVE_PIN, 1)  # 阀门 OFF
    time.sleep(0.2)

    # 下降吸取
    mc.send_coords([*xy_start, z_pick, 0, 180, 90], speed, 0)
    time.sleep(2)

    # 抬起
    mc.send_coords([*xy_start, z_safe, 0, 180, 90], speed, 0)
    time.sleep(2)

    # 搬运
    mc.send_coords([*xy_end,   z_safe, 0, 180, 90], speed, 0)
    time.sleep(3)
    mc.send_coords([*xy_end,   z_place, 0, 180, 90], speed, 0)
    time.sleep(2)

    # 放物
    mc.gpio_output(PUMP_PIN, 1)   # 吸泵 OFF
    mc.gpio_output(VALVE_PIN, 0)  # 阀门 ON
    time.sleep(0.3)
    mc.gpio_output(VALVE_PIN, 1)  # 阀门 OFF

    # 安全抬升
    mc.send_coords([*xy_end, z_safe, 0, 180, 90], speed, 0)
    time.sleep(2)