---
name: maixcam-pro-nuedc
description: Use when designing, implementing, refactoring, or debugging MaixCAM Pro / MaixPy vision projects for NUEDC-style competitions, including task decomposition, camera/color/geometry/YOLO vision pipelines, UART or lower-controller integration, project architecture, field debugging, and acceptance testing.
metadata:
  short-description: MaixCAM Pro 电赛视觉工程方法
---

# MaixCAM Pro NUEDC Skill

本 skill 用于 MaixCAM Pro + MaixPy 电赛视觉工程的拆题、方案选择、实现、调试和验收。它固化工程方法与 MaixPy 约束，不绑定某一年赛题、固定串口协议、坐标单位、心跳、任务模式或模型。

## 硬规则

1. 所有正向代码示例必须符合 MaixPy 官方 API；不得混入 OpenMV、K210、树莓派或 PC OpenCV 专属写法。
2. 先让相机、视觉、通信、执行机构各自可测，再做闭环联调。
3. 协议、坐标、频率、ACK、心跳、UI、模型和任务模式均为待确认决策，不得擅自固定。
4. 题目陌生时先查 `references/nuedc-topic-coverage.md`；没有适配历史模式时，基于题面约束提出候选方案并询问用户，而不是强套旧题。

## 首次使用门禁

当用户的提示词和上传文件没有同时提供以下关键事实时，先使用 `templates/task-intake-questions.md` 收集信息；此时不得直接生成工程代码或固定协议。

- 题型、任务目标、评分指标、已知规则或题面。
- 识别对象、输出对象、精度/时限与失效后动作。
- MaixCAM Pro 型号、相机/镜头、安装方式、相机引脚或设备信息。
- 屏幕型号、像素尺寸、方向、是否需要触摸。
- 下位机、执行机构、引脚、逻辑电平、供电、急停与已有接线。
- 场地、光照、目标尺寸、允许/禁止使用的硬件或算法。

题面、接线表、现有协议或模型已上传时，先提取已知项，仅追问缺项，不重复索要已有信息。

## 方案选择门禁

### 1. 先给候选方案

在关键配置足够后，先按 `templates/solution-options.md` 给出 2–3 套可行方案。每套方案必须同时说明：

- 识别方式和降级路线：颜色/几何/标定/YOLO/融合。
- 通信接口、候选帧格式、信息字段、坐标单位与可靠性策略。
- 屏幕 UI 显示内容、错误状态和现场调参入口。
- 主循环、配置、任务、通信、显示、测试模块边界。
- 性能、精度、时延、风险、调试顺序与安全措施。

### 2. 等待选择

用户确认方案及高影响项前，只能给出比较、问询和最小验证建议；不得把候选协议、UI、引脚映射、模型或代码结构当成最终实现。

用户选择后，将未定项明确写为“待确认假设”，再使用 `templates/project-architecture.md` 和 `templates/serial-protocol-decision.md` 输出工程方案。

### 3. 选择视觉路线

- 颜色/激光：优先 `img.find_blobs()`、ROI、曝光/白平衡和时序过滤。
- 黑线、边框、靶纸和尺寸：优先几何、标定、单应性或物理坐标映射。
- 棋盘/格点：先定位棋盘坐标系，再做占用状态差分和落子映射。
- 类别语义或复杂外观：使用 YOLO；无数据集时使用 `templates/yolo-data-and-training.md` 先做采集、标注、训练和验证计划。
- 混合方案：传统视觉提供几何/ROI 约束，模型输出类别或复杂目标。

## 工程化输出

默认采用可裁剪分层：`main` 调度，`config` 参数，`tasks` 视觉任务，`communication` I/O，`display` UI，`tests` 独立验证。模块只承担一个职责；状态有来源、有效性、时间戳和错误信息；代码以可维护、可调和可降级为目标，不以堆叠冗余分支代替结构。

详细架构见 `references/architecture-patterns.md`，调试顺序见 `references/debugging-playbook.md`。

## MaixCAM Pro 语法硬规则

常用导入：

```python
from maix import app, camera, display, image, time
```

UART、触摸或模型按需导入：

```python
from maix import uart, touchscreen, nn
```

主循环：

```python
while not app.need_exit():
    img = cam.read()
```

常见 API：

- `camera.Camera(width, height)`
- `display.Display()` 与 `disp.show(img)`
- `img.find_blobs(thresholds, ...)`
- `uart.UART(device, baud)`
- `serial.write_str(text)` 与 `serial.read()`
- `nn.YOLOv5(model=path, dual_buff=True)`
- `detector.detect(img, conf_th=..., iou_th=...)`

轮询 `read()` 和 `set_received_callback()` 不要混用。严格同步的闭环任务必须处理 YOLO 双缓冲的一帧结果延迟。完整 API 说明见 `references/maixcam-pro-api-notes.md`。

## 交付前自检

使用 `templates/acceptance-checklist.md` 自检：

- 工程是否职责清晰、可独立测试、可维护且避免无意义冗余。
- 协议、UI、坐标与失效策略是否已由用户确认。
- 正向代码是否只使用官方 MaixPy API。
- 公开发布文本是否不含个人信息、令牌、本机路径、私钥或未经授权的数据集。

## 参考来源

- MaixPy 文档首页: https://wiki.sipeed.com/maixpy/doc/zh/index.html
- MaixPy UART: https://wiki.sipeed.com/maixpy/doc/zh/peripheral/uart.html
- MaixPy Camera: https://wiki.sipeed.com/maixpy/doc/zh/vision/camera.html
- MaixPy find_blobs: https://wiki.sipeed.com/maixpy/doc/zh/vision/find_blobs.html
- MaixPy YOLO: https://wiki.sipeed.com/maixpy/doc/zh/vision/yolov5.html
