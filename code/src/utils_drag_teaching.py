# utils_drag_teaching.py
# 同济子豪兄 2025-07-14 更新适配 MyCobot280 官方 API
print('导入拖动示教模块')

import time
import os
import sys
import termios
import tty
import threading
import json

from pymycobot import MyCobot280, PI_PORT, PI_BAUD

# 连接机械臂
mc = MyCobot280(PI_PORT, PI_BAUD, debug=False)

class Raw(object):
    """Set raw input mode for device"""
    def __init__(self, stream):
        self.stream = stream
        self.fd = self.stream.fileno()
    def __enter__(self):
        self.original_stty = termios.tcgetattr(self.stream)
        tty.setcbreak(self.stream)
    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.stream, termios.TCSANOW, self.original_stty)

class Helper(object):
    def __init__(self) -> None:
        self.w, self.h = os.get_terminal_size()
    def echo(self, msg):
        print("\r{}".format(" " * self.w), end="")
        print("\r{}".format(msg), end="")

class TeachingTest(Helper):
    def __init__(self, mycobot) -> None:
        super().__init__()
        self.mc = mycobot
        self.recording = False
        self.playing = False
        self.record_list = []
        self.record_t = None
        self.play_t = None

    def record(self):
        self.record_list = []
        self.recording = True
        self.mc.set_fresh_mode(0)          # 队列模式
        def _record():
            start_t = time.time()
            while self.recording:
                encs = self.mc.get_encoders()
                if encs:
                    self.record_list.append(encs)
                    time.sleep(0.1)
                    print("\r {}".format(time.time() - start_t), end="")
        self.echo("开始录制动作")
        self.record_t = threading.Thread(target=_record, daemon=True)
        self.record_t.start()

    def stop_record(self):
        if self.recording:
            self.recording = False
            self.record_t.join()
            self.echo("停止录制动作")

    def play(self):
        self.echo("开始回放动作")
        for encs in self.record_list:
            self.mc.set_encoders(encs, 80)
            time.sleep(0.1)
        self.echo("回放结束\n")

    def loop_play(self):
        self.playing = True
        def _loop():
            len_ = len(self.record_list)
            i = 0
            while self.playing:
                idx_ = i % len_
                i += 1
                self.mc.set_encoders(self.record_list[idx_], 80)
                time.sleep(0.1)
        self.echo("开始循环回放")
        self.play_t = threading.Thread(target=_loop, daemon=True)
        self.play_t.start()

    def stop_loop_play(self):
        if self.playing:
            self.playing = False
            self.play_t.join()
            self.echo("停止循环回放")

    def save_to_local(self):
        if not self.record_list:
            self.echo("No data should save.")
            return
        save_path = os.path.join(os.path.dirname(__file__), "temp", "record.txt")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w") as f:
            json.dump(self.record_list, f, indent=2)
            self.echo("回放动作导出至: {}".format(save_path))

    def load_from_local(self):
        load_path = os.path.join(os.path.dirname(__file__), "temp", "record.txt")
        if not os.path.exists(load_path):
            self.echo("本地文件不存在")
            return
        with open(load_path, "r") as f:
            try:
                data = json.load(f)
                self.record_list = data
                self.echo("载入本地动作数据成功")
            except Exception:
                self.echo("Error: invalid data.")

    def print_menu(self):
        print(
            """\
        \r 拖动示教 中科多模态六轴机械臂
        \r q: 退出
        \r r: 开始录制动作
        \r c: 停止录制动作
        \r p: 回放动作
        \r P: 循环回放/停止循环回放
        \r s: 将录制的动作保存到本地
        \r l: 从本地读取录制好的动作
        \r f: 放松机械臂
        \r----------------------------------
            """
        )

    def start(self):
        self.print_menu()
        while True:
            with Raw(sys.stdin):
                key = sys.stdin


    def drag_teach():
        print('机械臂归零')
        mc.send_angles([0, 0, 0, 0, 0, 0], 40)
        time.sleep(3)

        recorder = TeachingTest(mc)
        recorder.start()

        print('机械臂归零')
        mc.send_angles([0, 0, 0, 0, 0, 0], 40)
        time.sleep(3)