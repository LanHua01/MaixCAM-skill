# MaixPy Vision Capabilities

本表用于在方案阶段按任务能力选型，不是要求每个项目都启用全部能力。支持板卡统一按官方 MaixPy 页面所面向的 MaixCAM / MaixCAM Pro 核验；若官方没有明确最低版本，必须写“官方未注明，目标板核验”，不得猜测。

核验日期：2026-07-22。

| 能力 | 典型电赛用途 | 官方 API / 模型 | 支持板卡 | 官方最低版本 | 输入与输出 | 主要性能风险 | 最小降级路线 | 官方来源 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Blob / LAB | 色块、激光、灯光状态、粗目标定位 | `Image.find_blobs()` | MaixCAM / MaixCAM Pro | 官方未注明，目标板核验 | LAB 阈值、ROI → blob 位置/面积等 | 全帧多阈值、反复颜色转换、自动曝光漂移 | 缩小 ROI、固定曝光、只保留必要阈值 | [find_blobs](https://wiki.sipeed.com/maixpy/doc/zh/vision/find_blobs.html) |
| Line / Edge | 巡线、边框、轨迹、停止线 | `Image.get_regression()`、线段/边缘相关 API | MaixCAM / MaixCAM Pro | 官方未注明，目标板核验 | 灰度/二值图 → 直线、角度、偏差 | 全图边缘、复杂交叉、坡面曝光变化 | 底部 ROI + 阈值/回归；必要时多 ROI 预判 | [巡线](https://wiki.sipeed.com/maixpy/doc/zh/vision/line_tracking.html) |
| Geometry | 矩形、圆、角点、靶框、单目测量 | `find_rects()`、`find_circles()` 等 Image API | MaixCAM / MaixCAM Pro | 官方未注明，目标板核验 | 图像/ROI → 几何候选与像素坐标 | 高分辨率、多候选、透视和畸变 | 已知尺寸 + ROI；标定/单应性后只算必要量 | [Image API](https://wiki.sipeed.com/maixpy/api/maix/image.html) |
| QR / AprilTag | 编号、任务载荷、固定地标、姿态 | `find_qrcodes()`、`find_apriltags()` | MaixCAM / MaixCAM Pro | 官方未注明，目标板核验 | 图像 → 内容/ID、角点，部分场景可求姿态 | 远距像素不足、倾角、缩放回映误差 | 放大印刷、限制 ROI；只输出题目需要的 ID/角点 | [QR](https://wiki.sipeed.com/maixpy/doc/zh/vision/qrcode.html)、[AprilTag](https://wiki.sipeed.com/maixpy/doc/zh/vision/apriltag.html) |
| Detection | 目标类别、位置、多目标巡查 | `nn.YOLOv5` / YOLOv8 / YOLO11 / YOLO26 | MaixCAM / MaixCAM Pro | YOLOv8 ≥ 4.3.0；YOLO11 ≥ 4.7.0；YOLO26 ≥ 4.12.5；YOLOv5 页面未给最低值 | 图像 → 类别、置信度、框 | 模型尺寸、输入分辨率、双缓冲时序、后处理 | 先降输入/类别；若颜色几何足够则回退传统视觉 | [YOLO](https://wiki.sipeed.com/maixpy/doc/zh/vision/yolov5.html) |
| OBB | 旋转物体、方向、倾斜目标框 | YOLO11 / YOLOv8 OBB | MaixCAM / MaixCAM Pro | 官方未注明，目标板核验 | 图像 → 旋转框、角度、类别 | 比普通检测后处理更重，角度抖动 | 普通框 + 几何主轴；没有方向评分项时不用 OBB | [旋转目标检测](https://wiki.sipeed.com/maixpy/doc/zh/vision/detect_obb.html) |
| Segmentation | 不规则区域、道路、轮廓、像素级禁区 | YOLOv8-Seg / YOLO11-Seg | MaixCAM / MaixCAM Pro | YOLOv8 ≥ 4.4.0；YOLO11 ≥ 4.7.0 | 图像 → 类别、框、掩膜 | 掩膜内存、渲染和后处理成本 | Detection + 传统轮廓；没有像素级评分项时不用分割 | [图像分割](https://wiki.sipeed.com/maixpy/doc/zh/vision/segmentation.html) |
| Tracking | 运动目标、跨帧身份、计数去重、连续控制 | `maix.tracker.ByteTracker` | MaixCAM / MaixCAM Pro | 官方未注明，目标板核验 | 连续检测框 → track ID 与轨迹状态 | 检测间隔、遮挡、ID 切换、陈旧结果 | 最近邻 + 门限 + 短时缓存；无需身份时只做时序滤波 | [目标追踪](https://wiki.sipeed.com/maixpy/doc/zh/vision/object_track.html) |

## 选型约束

1. 先淘汰不满足题面、时限、安全、精度和目标板预算的能力，再在合格路线中选择计算量最小、标定负担最低者。
2. OBB 只在方向是评分对象时进入候选；Segmentation 只在像素级不规则区域不可替代时进入候选；Tracking 只在跨帧身份、计数去重或连续控制确有需要时进入候选。
3. 模型能力必须先确认 MaixPy 版本、模型格式、数据来源和板端基准；文档支持不等于当前固件、模型和输入尺寸已经达到题目性能。
4. 所有正向代码仍须逐项核对 [MaixPy API](https://wiki.sipeed.com/maixpy/api/)；社区项目只能补充调试经验。
