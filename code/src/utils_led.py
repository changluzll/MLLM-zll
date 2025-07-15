import re
import json
from utils_llm import llm_qianfan, llm_yi
from utils_robot import mc

def extract_rgb(text):
    """从文本中提取RGB元组，兼容多种格式"""
    # 匹配 (r, g, b) 或 [r, g, b] 或 {"r": r, "g": g, "b": b}
    patterns = [
        r'\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)',  # (255, 100, 50)
        r'\[(\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\]',  # [255, 100, 50]
        r'"r":\s*(\d{1,3}).*"g":\s*(\d{1,3}).*"b":\s*(\d{1,3})'  # JSON对象
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return tuple(int(x) for x in match.groups())
    raise ValueError("未找到有效RGB值")


def llm_led(PROMPT_LED='帮我把LED灯的颜色改为贝加尔湖的颜色'):
    SYS_PROMPT = '我即将说的这句话中包含一个目标物体，帮我把这个物体的一种可能的颜色，以0-255的RGB像素值形式返回给我，整理成元组格式，例如(255, 30, 60)，直接回复元组本身，以括号开头，不要回复任何中文内容，下面是这句话：'

    PROMPT = SYS_PROMPT + PROMPT_LED

    for n in range(5):
        try:
            response = llm_qianfan(PROMPT)
            print(response)
            rgb_tuple = extract_rgb(response)
            mc.set_color(*rgb_tuple)
            print('LED灯颜色修改成功', rgb_tuple)
            return
        except Exception as e:
            print(f'第{n + 1}次尝试失败:', e)
    print('所有尝试均失败，使用默认颜色(255,255,255)')
    mc.set_color(255, 255, 255)