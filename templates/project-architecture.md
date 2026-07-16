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
- 补光/滤光：
- 下位机、执行机构、急停：
- 通信接口、引脚、逻辑电平、端口、波特率：
- 电源、共地和接线约束：

## 推荐模块

```text
main.py
config.py
communication.py
display_status.py
tasks/
  __init__.py
  task_<name>.py
tests/
  camera_test.py
  vision_test.py
  uart_test.py
  protocol_test.py
  actuator_safe_test.py
models/
app.yaml
README.md
```

- `main`：初始化、调度、性能统计和异常兜底。
- `config`：相机、阈值、ROI、模型、端口、频率、UI 和调试开关。
- `tasks`：输入图像/时间，输出可解释状态；不直接写串口或显示。
- `communication`：字节流、分包、协议和连接快照；不写视觉算法。
- `display`：只读状态，显示 UI 和调参事件；不篡改识别结果。
- `tests`：每个高风险模块的最小验证，不依赖完整闭环。

## 状态结构草案

```python
state = {
    "task_name": "",
    "vision_status": "visible",  # visible / cached / lost
    "targets": [],
    "primary_target": None,
    "debug": {},
    "errors": [],
    "time_ms": 0,
}
```

每个目标至少包含 `type`、`cx`、`cy`、`world`、`confidence`、`source`、`visible` 和 `time_ms`。

## 方案确认记录

- 用户选择的方案：
- 放弃的方案及原因：
- 允许的降级模式：
- 最终协议与坐标单位：
- 最终 UI 内容：
- 已确认配置来源（题面/接线图/用户说明）：
