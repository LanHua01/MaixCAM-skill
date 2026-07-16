# MaixCAM Pro API Notes

本文件记录 MaixCAM Pro 电赛项目中最常用、最容易混淆的 MaixPy 写法。使用时以官方文档为准；如果现场版本差异导致 API 不兼容，优先写兼容分支或先做最小验证脚本。

## 基础导入

```python
from maix import app, camera, display, image, time
```

按需导入：

```python
from maix import uart
from maix import touchscreen
from maix import nn
```

不要把 OpenMV 写法直接搬到 MaixCAM Pro，例如 `sensor.reset()`、`pyb.UART()`、`img.find_rects()` 等是否存在必须以 MaixPy 文档或本机实测为准。

## 主循环

```python
while not app.need_exit():
    img = cam.read()
```

需要释放 CPU 时使用：

```python
time.sleep_ms(1)
```

## Camera

基础写法：

```python
cam = camera.Camera(480, 320)
img = cam.read()
```

兼容格式参数：

```python
try:
    cam = camera.Camera(width, height)
except TypeError:
    cam = camera.Camera(width, height, image.Format.FMT_RGB888)
```

电赛建议：

- 分辨率不是越高越好；闭环和实时识别优先选择足够低但可识别的分辨率。
- 颜色识别前先稳定曝光、白平衡、补光和镜头焦距。
- 高帧率与低帧率可能有像素偏移，严格坐标题要重新标定。
- 开机前几帧可能不稳定，正式算法前跳过或丢弃若干帧。

## Display

```python
disp = display.Display()
disp.show(img)
```

建议：

- 显示层只读算法输出的 `state`。
- 现场调试时屏幕显示：任务名、通信状态、坐标、目标可见性、错误信息。
- 不要让显示绘制逻辑反向改变视觉算法状态。

## Image / find_blobs

基础写法：

```python
thresholds = [[0, 80, 40, 80, 10, 80]]
blobs = img.find_blobs(thresholds, pixels_threshold=500)
for blob in blobs:
    x, y, w, h = blob.rect()
    cx = blob.cx()
    cy = blob.cy()
```

电赛建议：

- 颜色阈值、面积阈值、像素阈值、宽高范围、长宽比、ROI 都放到配置层。
- 激光点通常需要小 ROI、低曝光或特定颜色阈值来抗杂光。
- 色块/圆点可用面积、长宽比、填充率过滤误检。
- 识别不到时不要立刻输出无效控制量，可按题目决定是否缓存、保持或上报 lost。

## UART

MaixCAM Pro 常用默认串口：

- A16: UART0 TX
- A17: UART0 RX
- 设备路径常用 `/dev/ttyS0`
- 推荐波特率优先 `115200`

基础写法：

```python
from maix import uart

serial = uart.UART("/dev/ttyS0", 115200)
serial.write_str("hello")
data = serial.read()
```

注意：

- GND 必须共地。
- RX/TX 交叉连接。
- Type-C 转接板方向可能导致 RX/TX 交换。
- UART0 开机可能输出系统日志；下位机解析要能丢弃无关字节。
- 轮询 `read()` 和 `set_received_callback()` 不要混用。
- 协议格式、心跳、ACK、校验和重发策略必须按题目询问后决定。

## TouchScreen

```python
from maix import touchscreen

ts = touchscreen.TouchScreen()
x, y, pressed = ts.read()
```

建议：

- 用于现场模式切换、阈值调试、开始/停止，不要成为唯一控制入口。
- 触摸坐标和显示图像坐标可能比例不同，需要映射。
- 按钮需要消抖和“按下锁定”，避免一次触摸触发多次。

## YOLO

```python
from maix import nn

detector = nn.YOLOv5(model="model.mud", dual_buff=True)
objs = detector.detect(img, conf_th=0.5, iou_th=0.45)
for obj in objs:
    x, y, w, h = int(obj.x), int(obj.y), int(obj.w), int(obj.h)
    score = float(obj.score)
```

建议：

- 只有传统颜色/几何方法不稳或目标外观复杂时再上 YOLO。
- 模型输入尺寸、相机尺寸和显示尺寸要统一或明确映射。
- YOLO 结果应结合几何/ROI/状态机过滤，避免单帧误检直接触发动作。
- 模型加载失败必须可降级显示错误，而不是让主循环崩溃。

## 官方参考

- MaixPy 首页: https://wiki.sipeed.com/maixpy/doc/zh/index.html
- Camera: https://wiki.sipeed.com/maixpy/doc/zh/vision/camera.html
- find_blobs: https://wiki.sipeed.com/maixpy/doc/zh/vision/find_blobs.html
- UART: https://wiki.sipeed.com/maixpy/doc/zh/peripheral/uart.html
- YOLO: https://wiki.sipeed.com/maixpy/doc/zh/vision/yolov5.html
- TouchScreen: https://wiki.sipeed.com/maixpy/doc/zh/vision/touchscreen.html
