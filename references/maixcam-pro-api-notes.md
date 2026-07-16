# MaixCAM Pro API Notes

本文件只记录 MaixCAM Pro 的 MaixPy 写法。语法、引脚和设备结论以链接的 MaixPy 官方文档为准；社区教程只能补充采集、阈值和赛场经验，不能替代 API 依据。

## 基础导入与主循环

```python
from maix import app, camera, display, image, time

cam = camera.Camera(width=640, height=480)
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    disp.show(img)
```

## Camera

```python
from maix import camera, image

cam = camera.Camera(640, 480, image.Format.FMT_RGB888, fps=60)
img = cam.read()
```

- 分辨率使用偶数；根据相机和任务选择，不以最高分辨率为默认。
- 严格坐标题要重新标定帧率切换造成的像素偏移。
- `cam.exposure(...)` 或 `cam.gain(...)` 会进入手动曝光；恢复自动模式使用 `cam.exp_mode(camera.AeMode.Auto)`。
- 色块、激光和测量题先确认焦距、曝光、白平衡和暖机帧，再调算法。

## Display 与 TouchScreen

```python
from maix import display, image, touchscreen

disp = display.Display()
ts = touchscreen.TouchScreen()
img = image.Image(disp.width(), disp.height())
x, y, pressed = ts.read()
disp.show(img)
```

- 屏幕像素尺寸、方向和触摸映射必须在项目配置中明确。
- 触摸只产生模式切换或调参事件；不要让显示层直接改写识别结果。
- 对按下/抬起做消抖和单次触发处理。

## Image / find_blobs

```python
from maix import image

thresholds = [[0, 80, 40, 80, 10, 80]]
blobs = img.find_blobs(thresholds, pixels_threshold=500)
for blob in blobs:
    x, y, w, h = blob[0], blob[1], blob[2], blob[3]
    img.draw_rect(x, y, w, h, image.COLOR_GREEN)
```

- 阈值为 LAB 颜色空间 `[L_MIN, L_MAX, A_MIN, A_MAX, B_MIN, B_MAX]`。
- 将 ROI、面积阈值、长宽比、曝光和过滤条件集中在配置层。
- 激光题优先用小 ROI、低曝光与时序确认，避免反光点触发闭环。

## UART

自定义下位机通信优先使用 UART1：A19 为 TX、A18 为 RX、设备为 `/dev/ttyS1`。

```python
from maix import err, pinmap, uart

err.check_raise(pinmap.set_pin_function("A19", "UART1_TX"), "set UART1 TX failed")
err.check_raise(pinmap.set_pin_function("A18", "UART1_RX"), "set UART1 RX failed")
serial = uart.UART("/dev/ttyS1", 115200)
serial.write_str("ready\r\n")
data = serial.read()
```

- 先用 `uart.list_devices()` 确认设备；115200 是可靠的起始波特率，但仍以用户的下位机约束为准。
- UART0 是 A16 TX、A17 RX、`/dev/ttyS0`，会输出启动日志，且 A16 上电被外部拉低可能导致无法启动；仅在用户已确认接线和启动风险时使用。
- GND 必须共地，RX/TX 交叉连接；MaixCAM Type-C 转接板方向可能交换 RX/TX。
- `write_str()` 发送 `str`，`write()` 发送 `bytes`。回调 `set_received_callback()` 与轮询 `read()` 不得混用。
- 串口是字节流，粘包、拆包、超时、日志限流和系统启动杂字节由协议层处理。

## YOLO

```python
from maix import app, camera, display, image, nn

detector = nn.YOLOv5(model="models/target.mud", dual_buff=True)
cam = camera.Camera(detector.input_width(), detector.input_height(), detector.input_format())
disp = display.Display()

while not app.need_exit():
    img = cam.read()
    objs = detector.detect(img, conf_th=0.5, iou_th=0.45)
    for obj in objs:
        img.draw_rect(obj.x, obj.y, obj.w, obj.h, color=image.COLOR_RED)
    disp.show(img)
```

- 先确认 `.mud` 模型、类别顺序、模型输入尺寸与图像格式。
- `dual_buff=True` 会提高吞吐，但 `detect()` 的结果对应上一帧输入；严格同步的瞄准、测量或闭环控制应使用 `dual_buff=False`，或显式保存时间戳并补偿一帧延迟。
- 置信度、IOU、ROI、尺寸和时序稳定性应结合使用；单帧模型结果不得直接触发危险动作。
- 模型加载或格式不匹配失败时，显示错误并进入安全降级，不让主循环崩溃。

## 官方参考

- MaixPy Camera: https://wiki.sipeed.com/maixpy/doc/zh/vision/camera.html
- MaixPy find_blobs: https://wiki.sipeed.com/maixpy/doc/zh/vision/find_blobs.html
- MaixPy UART: https://wiki.sipeed.com/maixpy/doc/zh/peripheral/uart.html
- MaixPy YOLO: https://wiki.sipeed.com/maixpy/doc/zh/vision/yolov5.html
- MaixPy 双缓冲: https://wiki.sipeed.com/maixpy/doc/zh/vision/dual_buff.html
- MaixPy TouchScreen: https://wiki.sipeed.com/maixpy/doc/zh/vision/touchscreen.html
