# utils_robot.py
# 同济子豪兄 2025-7-15
# 启动并连接机械臂，导入各种工具包

print('导入机械臂连接模块')

from pymycobot import MyCobot280
from pymycobot import PI_PORT, PI_BAUD
import cv2
import numpy as np
import time
from utils_pump import *

# 连接机械臂
mc = MyCobot280(PI_PORT, PI_BAUD)
# 设置运动模式为队列模式(0)
mc.set_fresh_mode(0)

def back_zero():
    '''
    机械臂归零
    '''
    print('机械臂归零')
    mc.send_angles([0, 0, 0, 0, 0, 0], 40)
    time.sleep(3)


def relax_arms():
    print('放松机械臂关节')
    mc.release_all_servos()







def move_to_top_view():
    print('移动至俯视姿态')
    mc.send_angles([39.19, -4.39, -69.43, -10.63, 1.75, 80.77], 10)
    time.sleep(3)


def top_view_shot(check=False):
    '''
    拍摄一张图片并保存
    check：是否需要人工看屏幕确认拍照成功，再在键盘上按q键确认继续
    '''
    print('    移动至俯视姿态')
    move_to_top_view()
    time.sleep(1.5)
    # 获取摄像头，传入0表示获取系统默认摄像头
    cap = cv2.VideoCapture(20)
    # 打开cap
    cap.open(20)
    time.sleep(1)
    success, img_bgr = cap.read()

    # 保存图像
    print('    保存至temp/vl_now.jpg')
    cv2.imwrite('temp/vl_now.jpg', img_bgr)

    # 屏幕上展示图像
    cv2.destroyAllWindows()  # 关闭所有opencv窗口
    cv2.imshow('waiic_vlm', img_bgr)

    # 关闭摄像头
    cap.release()


def eye2hand(X_im=160, Y_im=120):
    '''
    输入目标点在图像中的像素坐标，转换为机械臂坐标
    '''

    # 整理两个标定点的坐标
    cali_1_im = [138,339]  # 左下角，第一个标定点的像素坐标，要手动填！
    cali_1_mc = [135.5,20.6]  # 左下角，第一个标定点的机械臂坐标，要手动填！
    cali_2_im = [369,72]  # 右上角，第二个标定点的像素坐标   `
    cali_2_mc = [231.7,167.2]  # 右上角，第二个标定点的机械臂坐标，要手动填！

    X_cali_im = [cali_1_im[0], cali_2_im[0]]  # 像素坐标
    X_cali_mc = [cali_1_mc[0], cali_2_mc[0]]  # 机械臂坐标
    Y_cali_im = [cali_2_im[1], cali_1_im[1]]  # 像素坐标，先小后大
    Y_cali_mc = [cali_2_mc[1], cali_1_mc[1]]  # 机械臂坐标，先大后小

    # X差值
    X_mc = int(np.interp(X_im, X_cali_im, X_cali_mc))

    # Y差值
    Y_mc = int(np.interp(Y_im, Y_cali_im, Y_cali_mc))

    return X_mc, Y_mc

