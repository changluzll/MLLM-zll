#utils_debug.py
import time
import threading
import sys
import tty
import termios
import cv2
from pymycobot import MyCobot280, PI_PORT, PI_BAUD

# -------------------- 初始化 --------------------
mc = MyCobot280(PI_PORT, PI_BAUD)
mc.release_all_servos()          # 真正自由模式
print("机械臂已释放电机（自由模式）")
print("实时打印中：按 r 复位 / 按 q 退出")
print("摄像头画面已开启（窗口：camera）\n")

# -------------------- 全局标志 --------------------
reset_flag = False
exit_flag  = False

# -------------------- 摄像头线程 --------------------
def camera_thread():
    cap = cv2.VideoCapture('/dev/video20', cv2.CAP_V4L2)
    if not cap.isOpened():
        print("无法打开摄像头 /dev/video20")
        return
    while not exit_flag:
        ret, frame = cap.read()
        if ret:
            cv2.imshow('camera', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

threading.Thread(target=camera_thread, daemon=True).start()

# -------------------- 键盘监听 --------------------
def kb_listener():
    global reset_flag, exit_flag
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        while not exit_flag:
            ch = sys.stdin.read(1)
            if ch.lower() == 'r':
                reset_flag = True
            elif ch.lower() == 'q':
                exit_flag = True
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

threading.Thread(target=kb_listener, daemon=True).start()

# -------------------- 主循环 --------------------
try:
    while not exit_flag:
        if reset_flag:
            print("\n正在复位...")
            mc.send_angles([0, 0, 0, 0, 0, 0], 30)
            time.sleep(3)
            mc.release_all_servos()
            reset_flag = False
            print("复位完成，已重新释放电机")
            continue

        angles = mc.get_angles()
        coords = mc.get_coords()
        print(
            f"\r{time.strftime('%H:%M:%S')} | "
            f"角度: [{', '.join(f'{a:7.2f}°' for a in angles)}] | "
            f"坐标: [x={coords[0]:6.1f} y={coords[1]:6.1f} z={coords[2]:6.1f} "
            f"rx={coords[3]:6.1f}° ry={coords[4]:6.1f}° rz={coords[5]:6.1f}°]",
            end='', flush=True
        )
        time.sleep(1)

except KeyboardInterrupt:
    pass

print("\n👋 程序退出")
mc.send_angles([0, 0, 0, 0, 0, 0], 30)
time.sleep(2)
mc.close()