# Project Architecture Template

用于新 MaixCAM Pro 电赛视觉项目立项或重构时填写。

## 题目摘要

- 题目名称：
- 识别目标：
- 输出目标：
- 控制对象：
- 评分指标：
- 现场环境：

## 设备和接口

- MaixCAM Pro 镜头/相机：
- 补光/滤光：
- 下位机：
- 执行机构：
- 通信方式：
- 电源和接线约束：

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
models/
```

## 状态结构草案

```python
state = {
    "task_name": "",
    "task_label": "",
    "targets": [],
    "primary_target": None,
    "vision_status": "",
    "debug": {},
    "errors": [],
}
```

每个目标建议包含：

```python
target = {
    "type": "",
    "visible": False,
    "cached": False,
    "cx": 0,
    "cy": 0,
    "world": None,
    "confidence": None,
    "time_ms": 0,
}
```

## 主循环职责

- 初始化。
- 读取串口/触摸/按键事件。
- 读取相机帧。
- 调用当前 task。
- 根据 state 派生通信输出。
- 渲染显示。
- 性能统计和异常兜底。

## 不确定项

- 协议：
- 坐标单位：
- 发送频率：
- 是否需要心跳/ACK：
- 是否需要模型：
- 是否需要现场参数调节：
