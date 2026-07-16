# Project Architecture Template

用于用户选定方案后的 MaixCAM Pro 电赛视觉项目。每个模块只有一个职责，且高风险链路可独立测试。

## 题目摘要

- 题目名称与题面来源：
- 识别目标与输出：
- 控制对象与失效动作：
- 评分指标、时限和安全约束：
- 已确认项与待确认假设：

## 设备和接口

- MaixPy/固件版本：
- 相机、镜头、分辨率、帧率、安装方式：
- 屏幕型号、像素尺寸、方向、触摸：
- 是否需要 UI、UI 内容、刷新要求、调参入口与无 UI 时的替代观测方式：
- 补光/滤光：
- 下位机、执行机构、急停：
- 通信接口、引脚、逻辑电平、端口、波特率：
- 电源、共地和接线约束：

## 推荐模块

```text
<project-name>/
  main.py                  # 唯一运行入口
  config.py
  communication.py
  display_status.py
  tasks/
    __init__.py
    task_<name>.py
  tests/
    camera_test.py
    vision_test.py
    performance_test.py
    uart_test.py
    protocol_test.py
    actuator_safe_test.py
  models/                  # 仅放用户已提供或已获授权的模型
  assets/                  # 项目运行必需的图片、配置等资源
  app.yaml                 # 仅在用户要求打包/安装且规范已确认时加入
```

交付时列出实际生成的全部文件，不留“请自行新建”或未说明的外部依赖。用户在 MaixVision 打开 `<project-name>/` 后运行完整项目；多文件、模型或资源项目不应使用“运行当前文件”。

- `main`：初始化、调度、性能统计和异常兜底。
- `config`：相机、阈值、ROI、模型、端口、频率、UI 和调试开关。
- `tasks`：输入图像/时间，输出可解释状态；不直接写串口或显示。
- `communication`：字节流、分包、协议和连接快照；不写视觉算法。
- `display`：只读状态，显示 UI 和调参事件；不篡改识别结果。
- `tests`：每个高风险模块的最小验证，不依赖完整闭环。
- 工程代码注释：默认中文；只说明职责、硬件假设、单位/坐标、安全与时序，不翻译 API 或标识符。

## MaixVision 运行准备

- 工程根目录与入口文件名：
- 本次使用在线完整项目运行，还是已确认的打包/安装方式：
- 首次运行可观察项（画面、FPS、状态栏、串口快照、错误信息）：
- 已随项目提供的模型/资源，及缺失资源时的安全降级：
- 禁止使用的电脑绝对路径和未部署资源：
- 目标板性能预算、连续运行时长和性能报告位置：

## 状态结构草案

```python
state = {
    "task_name": "",
    "vision_status": "candidate",  # candidate / confirmed / cached / lost
    "targets": [],
    "primary_target": None,
    "debug": {},
    "errors": [],
    "time_ms": 0,
}
```

每个目标至少包含 `type`、`cx`、`cy`、`world`、`confidence`、`source`、`visible` 和 `time_ms`。

- 确认帧数、缓存时长、丢失条件、离群阈值和主目标选择规则：
- 已有工程中必须保持的引脚、协议、波特率或安全联锁：

## 方案确认记录

- 用户选择的方案：
- 放弃的方案及原因：
- 允许的降级模式：
- 最终协议与坐标单位：
- 心跳、ACK、序号、重发、超时与丢失策略：
- 最终 UI 内容：
- 已确认配置来源（题面/接线图/用户说明）：
