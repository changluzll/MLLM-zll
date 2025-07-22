import cv2
import numpy as np

# 读取图像
image = cv2.imread('crack_image.png')

# 转换为灰度图像
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 使用高斯模糊减少噪声
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# 使用Canny边缘检测找到裂缝
edges = cv2.Canny(blurred, 50, 150)

# 找到裂缝的像素坐标
crack_pixels = np.column_stack(np.where(edges > 0))

# 打印裂缝的像素坐标
print("Crack Pixels Coordinates:")
print(crack_pixels)

# 可视化裂缝
crack_image = image.copy()
for pixel in crack_pixels:
    cv2.circle(crack_image, (pixel[1], pixel[0]), 1, (0, 0, 255), -1)

# 显示结果图像
cv2.imshow('Crack Detection', crack_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
