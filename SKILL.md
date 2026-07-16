---
name: maixcam-pro-nuedc
description: Use when designing, implementing, refactoring, or debugging MaixCAM Pro / MaixPy vision projects for NUEDC-style competitions, including task decomposition, camera/color/geometry/YOLO vision pipelines, UART or lower-controller integration, project architecture, field debugging, and acceptance testing. Ask task-specific questions before choosing protocols, heartbeat, frame format, coordinate units, task modes, model use, or control interfaces.
metadata:
  short-description: MaixCAM Pro 电赛视觉工程方法
---

# MaixCAM Pro NUEDC Skill

本 skill 面向 MaixCAM Pro + MaixPy 的电赛视觉工程。它固化稳定的工程思维、MaixCAM Pro 语法约束和调试流程，但不固定某一套题目协议、坐标格式、心跳、任务模式或模型方案。

## 使用原则

1. 先问约束，再定方案。
2. 固化工程分层，不固化题目策略。
3. 先让单模块可验证，再做闭环联调。
4. 所有 MaixCAM Pro 代码建议必须符合 MaixPy API，不混入 OpenMV、K210、树莓派或 PC OpenCV 的专属写法。
5. 当协议、坐标单位、发送周期、ACK、心跳、下位机命令格式、是否使用 YOLO 不明确时，必须先询问用户，不能擅自默认。

## 快速流程

### 1. 题目约束澄清

先收集这些信息，缺失时优先询问：

- 识别对象：激光点、色块、圆点、黑框、边线、棋盘、二维码、火焰、动物、车辆、棋子等。
- 输出对象：像素坐标、物理坐标、目标类别、状态机事件、控制误差、路径点等。
- 控制对象：仅 MaixCAM 显示/记录，还是要驱动 STM32/MSPM0/Arduino/电机/舵机/机械臂。
- 评分指标：精度、速度、稳定时间、误检次数、漏检次数、闭环成功率、赛场抗干扰。
- 环境条件：光照、背景、靶纸尺寸、镜头距离、相机固定方式、是否允许补光。
- 接口边界：串口/I2C/SPI/网络/文件；谁主动发，谁回包，是否需要 ACK 或在线状态。

详细问询模板见 `templates/task-intake-questions.md`。

### 2. 视觉路线选择

按题目约束选择最小可行路线：

- 颜色/激光：优先 `img.find_blobs()` + ROI + 曝光/白平衡控制 + 缓存/滤波。
- 黑线/边框/几何：优先灰度/阈值/线段/矩形/轮廓思路，必要时做透视或标定。
- 棋盘/格点：先定位棋盘坐标系，再映射格点，再识别占用状态。
- 目标检测：仅当颜色/几何规则不稳定或目标外观复杂时使用 YOLO。
- 混合方案：用传统视觉提供坐标和约束，用 YOLO 处理类别或复杂目标。

历年题型抽象见 `references/nuedc-vision-archetypes.md`。

### 3. 工程架构

默认推荐分层，但按项目规模裁剪：

- `main`：只做初始化、主循环调度、任务切换、性能统计和异常兜底。
- `config`：集中管理串口、相机、阈值、模型路径、发送周期、调试开关。
- `tasks`：每个赛题/模式一个任务模块，只接收图像和时间，输出统一 `state`。
- `communication`：只处理 I/O、协议编码/解码、连接状态，不写视觉算法。
- `display`：只读 `state` 和通信快照，不反向影响算法。
- `tests` 或独立脚本：单独验证相机、色块、模型、串口、协议。

架构细节见 `references/architecture-patterns.md`，架构模板见 `templates/project-architecture.md`。

### 4. 接口决策

不要默认固定协议。先确认：

- 通信方式和物理接线。
- 数据方向：MaixCAM 主发、下位机主发，还是双向。
- 帧格式：文本帧、二进制帧、JSON、CSV、Modbus、自定义。
- 分包规则：帧头、帧尾、长度、校验、转义、超时。
- 在线机制：无心跳、心跳、ACK、序号、超时重发。
- 坐标单位：像素、cm、mm、归一化、控制误差。
- 发送频率：固定周期、状态变化触发、下位机查询响应。

决策模板见 `templates/serial-protocol-decision.md`。

### 5. MaixCAM Pro 语法硬规则

常用导入：

```python
from maix import app, camera, display, image, time
```

UART 需要时：

```python
from maix import uart
```

触摸屏需要时：

```python
from maix import touchscreen
```

YOLO 需要时：

```python
from maix import nn
```

主循环使用：

```python
while not app.need_exit():
    img = cam.read()
```

常见 API：

- `camera.Camera(width, height)`
- `display.Display()`
- `disp.show(img)`
- `img.find_blobs(thresholds, ...)`
- `uart.UART(device, baud)`
- `serial.write_str(text)`
- `serial.read()`
- `nn.YOLOv5(model=path, dual_buff=True)`
- `detector.detect(img, conf_th=..., iou_th=...)`

轮询 `read()` 和 `set_received_callback()` 不要混用。更多 API 注意点见 `references/maixcam-pro-api-notes.md`。

## 调试工作流

1. 先确认相机画面稳定：分辨率、帧率、焦距、曝光、白平衡。
2. 再确认单目标识别：只画框/十字，不接控制。
3. 再确认坐标系：像素方向、物理方向、比例尺、原点。
4. 再确认通信链路：电脑直连或串口助手先看原始字节。
5. 再确认下位机解析：粘包、拆包、丢包、阻塞打印、缓冲区溢出。
6. 最后闭环联调：先低速、限幅、保护，再追求速度和精度。

详细排错清单见 `references/debugging-playbook.md`，验收模板见 `templates/acceptance-checklist.md`。

## 输出要求

当用户让你生成方案或代码时：

- 先说明已知约束和仍需确认的关键决策。
- 对高影响未知项先提问；低影响未知项可给推荐默认，但要标注为假设。
- 给代码时优先给可运行的 MaixPy 结构，而不是 PC 伪代码。
- 保持协议、心跳、坐标单位和任务模式可替换。
- 给调试建议时按“相机 -> 算法 -> 坐标 -> 通信 -> 下位机 -> 闭环”的顺序排查。

## 参考来源

- OpenAI Skills in API: https://developers.openai.com/cookbook/examples/skills_in_api
- Agent Skills Specification: https://agentskills.io/specification
- Claude Agent Skills overview: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- MaixPy 文档首页: https://wiki.sipeed.com/maixpy/doc/zh/index.html
- MaixPy UART: https://wiki.sipeed.com/maixpy/doc/zh/peripheral/uart.html
- MaixPy Camera: https://wiki.sipeed.com/maixpy/doc/zh/vision/camera.html
- MaixPy find_blobs: https://wiki.sipeed.com/maixpy/doc/zh/vision/find_blobs.html
- MaixPy YOLO: https://wiki.sipeed.com/maixpy/doc/zh/vision/yolov5.html
