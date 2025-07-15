import time
from pymycobot import MyCobot280
from pymycobot import PI_PORT, PI_BAUD

# 连接机械臂
mc = MyCobot280(PI_PORT, PI_BAUD)

# 设置为自由模式（可手拖动）
mc.set_free_mode(1)
print("🔓 机械臂已设为自由模式，可以手动拖动")
print("📊 每秒打印一次角度和坐标（Ctrl+C 退出）\n")

try:
    while True:
        # 获取关节角度（度）
        angles = mc.get_angles()
        # 获取末端坐标（x,y,z,rx,ry,rz）
        coords = mc.get_coords()

        # 格式化打印
        print(
            f"⏰ {time.strftime('%H:%M:%S')} | "
            f"角度: [{', '.join(f'{a:7.2f}°' for a in angles)}] | "
            f"坐标: [x={coords[0]:6.1f} y={coords[1]:6.1f} z={coords[2]:6.1f} "
            f"rx={coords[3]:6.1f}° ry={coords[4]:6.1f}° rz={coords[5]:6.1f}°]"
        )
        time.sleep(1)

except KeyboardInterrupt:
    print("\n👋 用户中断，程序退出")
    # 可选：恢复非自由模式
    mc.set_free_mode(0)
    mc.close()