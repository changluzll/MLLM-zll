# utils_vlm_move.py
# 同济子豪兄 2024-05-22  2025-07-14 完整适配 MyCobot280 官方 API
# 多模态大模型识别图像 → 吸泵吸取并移动物体
# 直接运行：python utils_vlm_move.py

import os
import cv2
import numpy as np
import time
from pymycobot import MyCobot280, PI_PORT, PI_BAUD

# ---------- 连接机械臂 ----------
mc = MyCobot280(PI_PORT, PI_BAUD)

# ---------- 官方 GPIO ----------
PUMP_PIN  = 20   # 吸泵
VALVE_PIN = 21   # 泄气
mc.gpio_init()
mc.set_gpio_out(PUMP_PIN,  "out")
mc.set_gpio_out(VALVE_PIN, "out")
mc.gpio_output(PUMP_PIN,  1)  # 默认关闭
mc.gpio_output(VALVE_PIN, 1)

# ---------- 吸泵 ----------
def pump_on():
    mc.gpio_output(PUMP_PIN, 0)
    mc.gpio_output(VALVE_PIN, 1)

def pump_off():
    mc.gpio_output(PUMP_PIN, 1)
    mc.gpio_output(VALVE_PIN, 0)
    time.sleep(0.2)
    mc.gpio_output(VALVE_PIN, 1)

# ---------- 拍照 ----------
def top_view_shot(check=False):
    move_to_top_view()
    cap = cv2.VideoCapture(0)
    cap.open(0)
    time.sleep(0.3)
    ret, img = cap.read()
    if not ret:
        raise RuntimeError("摄像头读取失败")
    os.makedirs("temp", exist_ok=True)
    cv2.imwrite("temp/vl_now.jpg", img)
    cv2.imshow("top_view", img)
    if check:
        print("请确认拍照成功，按 c 继续，按 q 退出")
        while True:
            key = cv2.waitKey(10) & 0xFF
            if key == ord("c"):
                break
            if key == ord("q"):
                cv2.destroyAllWindows()
                raise KeyboardInterrupt("用户取消")
    else:
        cv2.waitKey(1)
    cap.release()
    cv2.destroyAllWindows()

# ---------- 常用姿态 ----------
def move_to_top_view():
    mc.send_angles([-62.13, 8.96, -87.71, -14.41, 2.54, -16.34], 10)
    time.sleep(3)

def back_zero():
    print("机械臂归零")
    mc.send_angles([0, 0, 0, 0, 0, 0], 50)
    time.sleep(3)

# ---------- 手眼标定 ----------
def eye2hand(px, py):
    # 示例线性映射，请根据实际标定替换
    cali_im = [[130, 290], [640, 0]]
    cali_mc = [[-21.8, -197.4], [215, -59.1]]
    x_mc = np.interp(px, [cali_im[0][0], cali_im[1][0]],
                        [cali_mc[0][0], cali_mc[1][0]])
    y_mc = np.interp(py, [cali_im[1][1], cali_im[0][1]],
                        [cali_mc[1][1], cali_mc[0][1]])
    return int(x_mc), int(y_mc)

# ---------- VLM 结果后处理 ----------
def post_processing_viz(result, img_path, check=True):
    """
    解析 VLM JSON -> 起点终点中心像素坐标
    示例 result = {"start": [sx, sy], "end": [ex, ey]}
    """
    sx, sy = result["start"]
    ex, ey = result["end"]
    if check:
        img = cv2.imread(img_path)
        cv2.circle(img, (sx, sy), 5, (0, 255, 0), -1)
        cv2.circle(img, (ex, ey), 5, (0, 0, 255), -1)
        cv2.imshow("viz", img)
        cv2.waitKey(1)
    return sx, sy, ex, ey

# ---------- 吸泵搬运 ----------
def pump_move(xy_start, xy_end, z_safe=220, z_pick=90, z_place=90, speed=20):
    mc.set_fresh_mode(0)
    # 起点上方
    mc.send_coords([*xy_start, z_safe, 0, 180, 90], speed, 0)
    time.sleep(4)
    # 吸取
    pump_on()
    mc.send_coords([*xy_start, z_pick, 0, 180, 90], speed, 0)
    time.sleep(2)
    # 抬起
    mc.send_coords([*xy_start, z_safe, 0, 180, 90], speed, 0)
    time.sleep(2)
    # 搬运
    mc.send_coords([*xy_end, z_safe, 0, 180, 90], speed, 0)
    time.sleep(3)
    mc.send_coords([*xy_end, z_place, 0, 180, 90], speed, 0)
    time.sleep(2)
    # 放下
    pump_off()
    time.sleep(1)
    mc.send_coords([*xy_end, z_safe, 0, 180, 90], speed, 0)
    time.sleep(2)

# ---------- 多模态大模型接口 ----------
def QwenVL_api(prompt, img_path="temp/vl_now.jpg", vlm_option=0):
    """
    实际部署请替换为真实 HTTP / 本地推理
    返回示例: {"start": [320, 240], "end": [480, 380]}
    """
    return {"start": [320, 240], "end": [480, 380]}

# ---------- 主流程 ----------
def vlm_move(prompt="帮我把绿色方块放在小猪佩奇上", input_way="keyboard"):
    print("多模态大模型识别图像，吸泵吸取并移动物体")
    back_zero()

    # 拍照
    top_view_shot(check=False)

    # 调用 VLM
    print("调用多模态大模型...")
    result = QwenVL_api(prompt)
    print("VLM 返回:", result)

    # 解析
    sx, sy, ex, ey = post_processing_viz(result, "temp/vl_now.jpg", check=True)

    # 手眼转换
    sx_mc, sy_mc = eye2hand(sx, sy)
    ex_mc, ey_mc = eye2hand(ex, ey)

    # 搬运
    pump_move([sx_mc, sy_mc], [ex_mc, ey_mc])

    print("任务完成")
    cv2.destroyAllWindows()

def vlm_vqa(prompt="请数一数图中有几个方块", input_way="keyboard"):
    back_zero()
    top_view_shot(check=False)
    result = QwenVL_api(prompt, vlm_option=1)
    print("VLM 回答:", result)
    cv2.destroyAllWindows()
    return result

# ---------- 直接运行 ----------
if __name__ == "__main__":
    vlm_move()