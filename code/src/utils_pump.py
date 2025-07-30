# utils_pump.py
print('导入吸泵控制模块')

from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import Device, LED
import time

# 显式指定 GPIO 设备（必须使用lgpio驱动）
Device.pin_factory = LGPIOFactory(chip=0)

pump = LED(46)   # 气泵
valve = LED(37)  # 默认关闭（高电平）
def pump_on():
    '''
    开启吸泵（关闭泄气阀门）
    '''
    print('    开启吸泵')
    pump.off()
    valve.on()
    # 低电平关闭泄气阀门

def pump_off():
    '''
    关闭吸泵（打开泄气阀门，释放物体）
    '''
    print('    关闭吸泵')
    pump.on()
    valve.off()
    time.sleep(0.5)# 保持泄气时间（官方示例为0.3秒）

# 初始化状态：关闭泄气阀门（吸泵准备状态）