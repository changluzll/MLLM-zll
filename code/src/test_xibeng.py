from pymycobot import MyCobot280,PI_PORT,PI_BAUD
import time
from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import Device
from gpiozero import LED

# 显式指定 GPIO 设备文件
Device.pin_factory = LGPIOFactory(chip=0)  # 使用 /dev/gpiochip0

# 初始化 GPIO 控制的设备
value = LED(46)  # 使用 LED 类控制 GPIO 46（泄气阀门）

# 打开吸泵, 关闭泄气阀门
value.off()
print("吸泵已打开")

# 等待 3 秒
time.sleep(3)

# 关闭吸泵, 打开泄气阀门
value.on()
print("吸泵已关闭")
time.sleep(0.05)