# Architecture Patterns

本文件描述 MaixCAM Pro 电赛视觉项目的可复用架构。它是推荐模式，不是强制文件名；实际项目可按规模裁剪。

## 核心分层

### 主循环层

职责：

- 初始化配置、相机、显示、通信、任务管理器。
- 读取图像。
- 调用当前任务。
- 调用通信发送或接收。
- 调用显示渲染。
- 记录性能和异常。

禁止：

- 在主循环里堆大量识别细节。
- 在主循环里写复杂协议解析。
- 在主循环里直接嵌控制算法分支。

### 配置层

职责：

- 相机尺寸、帧率、曝光、白平衡。
- 颜色阈值、ROI、面积阈值。
- 模型路径、置信度、IOU。
- 通信端口、波特率、发送周期。
- 调试开关、显示开关、缓存时间。

建议：

- 所有赛场可调参数集中在配置层。
- 可用环境变量覆盖设备路径、波特率、模型路径。
- 关键默认值旁边写单位。

### 任务层

职责：

- 一个任务模块解决一种赛题模式或视觉目标。
- 输入：`img` 和 `now_ms`。
- 输出：统一 `state` 字典或等价结构。

推荐 `state` 包含：

- `task_name`
- `task_label`
- `targets`
- `primary_target`
- `debug`
- `errors`
- `visible/lost/cached` 状态

禁止：

- 任务层直接操作串口。
- 任务层直接依赖显示控件。
- 任务层输出无法解释的裸数值。

### 通信层

职责：

- 打开和关闭通信设备。
- 编码发送 payload。
- 接收字节流。
- 按用户确认的协议分包和解析。
- 保存连接状态、最后错误、最后收发内容。

注意：

- 协议格式不是 skill 默认项，必须按题目询问。
- 串口是流，不是消息队列；必须考虑粘包、拆包、丢字节。
- 如果用回调接收，不要再轮询 `read()`。

### 显示层

职责：

- 绘制图像、目标框、十字、状态栏。
- 显示任务名、通信状态、坐标、错误。
- 提供简单触摸交互时，只产生事件，不写算法状态。

禁止：

- 显示层修改识别结果。
- 显示层决定协议或控制动作。

### 独立测试层

每个高风险链路都应有最小测试：

- `camera_test`: 只显示画面和 FPS。
- `blob_test`: 只识别目标并画框。
- `model_test`: 只加载模型并显示检测结果。
- `uart_tx_test`: 只发送固定文本或字节。
- `uart_rx_test`: 只打印原始字节。
- `protocol_test`: 用模拟输入验证分包解析。

## 推荐数据流

```text
camera.read()
  -> task.process(img, now_ms)
  -> state
  -> communication.send(state-derived payload)
  -> display.draw(img, state, comm_snapshot)
```

通信接收的数据流：

```text
communication.poll_receive()
  -> parsed command/event
  -> task manager or app state
```

## 状态设计

视觉输出不要只有坐标。推荐同时输出：

- `visible`: 当前帧真实看到。
- `cached`: 当前值来自短时间缓存。
- `lost`: 当前目标不可用。
- `confidence`: 模型或规则置信度。
- `time_ms`: 更新时间。
- `source`: 颜色、几何、YOLO、融合等来源。

## 现场可调设计

电赛现场时间紧，工程应支持：

- 一键切换任务。
- 屏幕显示关键状态。
- 串口日志可开关。
- 阈值和模型参数集中修改。
- 识别失败时不崩溃。
- 下位机不在线时视觉仍能单独跑。

## 交付结构示例

```text
project/
  main.py
  config.py
  communication.py
  display_status.py
  tasks/
    __init__.py
    task_x.py
  tests/
    uart_text_test.py
    color_debug.py
  models/
    target.mud
  app.yaml
  README.md
```

文件名可变，但职责边界应保持。
