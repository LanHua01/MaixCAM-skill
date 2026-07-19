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
4. 题目陌生时先按年份、题号、题名或视觉模式检索 `references/nuedc-topic-coverage.md`；没有适配历史模式时，基于题面约束提出候选方案并询问用户，而不是强套旧题。
5. 用户提供已有工程、接线、协议或下位机代码时，先阅读并提取已确认决策；优先局部修复和最小验证，不平行重写。只有改动影响识别路线、协议、引脚、坐标、安全或验收时，才回到方案选择门禁。

## 快速验证与 API 问答模式

用户仅请求低风险、范围明确的 API 解释、语法核对或独立最小测试时，使用 `templates/quick-check-intake.md`，不触发完整项目门禁和方案矩阵。典型请求包括最小相机显示、单项 `find_blobs()` 验证、已知端口的 UART 收发测试，或 MaixPy API 问答。

- 只询问完成该测试所必需的板卡/固件、端口/引脚、相机或显示信息；无法确认的 API 必须标注假设。
- 只输出自包含的验证代码、预期现象、失败排查和下一步；不擅自定义完整协议、心跳、UI、执行机构动作或工程架构。
- 请求涉及新项目、闭环控制、协议设计、引脚更改、模型选择或多模块工程时，立即转入首次使用门禁和方案选择门禁。

## 条件自动检索与来源分级

当题目陌生、题面规则/硬件/API/版本需要核验、需要外部案例，或候选路线存在明显不确定性时，先检索本地题库，再按 `references/research-guidance.md` 进行在线检索。用户明确“禁止联网”时跳过在线检索；浏览能力不可用时，给出可复用的检索关键词和待确认假设，不得伪造来源或检索结论。

在线检索只用于补足证据和候选思路：官方 MaixPy/硬件资料与原始题面才可确定 API、版本、硬件、规则和评分事实；公开项目、演示和教程只可补充路线、调参范围、失败模式与验证思路。检索结果在方案矩阵前以简短研究卡呈现，列出链接、支持的事实、仅作参考的经验、对方案的影响和未证实项。不得用搜索结果覆盖用户已确认的接线、协议或安全约束，不直接复制社区代码，不下载或声称拥有未获授权的模型、数据集或资源。

## 首次使用门禁

采用“核心后分支”门禁：先读取用户材料，只收集会决定视觉路线和工程规模的核心配置；随后确认模块存在性，再只追问实际存在模块的细节。此时不得直接生成最终工程代码或固定协议。

- 核心配置：题型/评分、识别目标与输出、精度/时限/失效动作、MaixCAM Pro/相机/安装方式、场地光照与目标条件、以及允许/禁止的硬件或算法。
- 模块存在性：是否需要外发数据或下位机、执行机构或安全联锁、独立屏幕 UI、现场调参输入、模型语义识别。用户答“无”即为已确认，不继续追问该分支。
- 仅当 UI 存在时，询问屏幕像素、方向、显示内容和输入；仅当通信/下位机存在时，询问引脚、电平、协议、心跳/ACK；仅当执行机构存在时，询问供电、急停、限幅；仅当模型存在时，询问版本、数据与模型资源。

题面、接线表、现有协议或模型已上传时，先提取已知项，仅追问会改变方案的缺项，不重复索要已有信息。

## 方案选择门禁

### 1. 先给候选方案

在关键配置足够、且触发检索时已给出研究卡后，按 `templates/solution-options.md` 先淘汰不满足题面、时限、安全、精度或板端性能预算的路线。只有存在真实取舍时才给 2–3 套可行方案；否则只给一套推荐方案，并简述被排除路线及原因。每套保留的方案必须同时说明：

- 识别方式和降级路线：颜色/几何/标定/编码标记/YOLO/融合。
- 通信接口、候选帧格式、信息字段、坐标单位与可靠性策略（仅在外发数据存在时）。
- 屏幕 UI 显示内容、错误状态和现场调参入口（仅在独立 UI 存在时）。
- 主循环、配置、任务、通信、显示、测试模块边界；明确哪些能力不需要，以及替代观测方式。
- 性能、精度、时延、风险、调试顺序与安全措施。

在满足约束的方案中，优先传统视觉、最少外部依赖、最少标定负担、最少跨模块接口和最大目标板性能余量。YOLO 仅在颜色、几何或编码标记无法稳定满足语义识别要求时进入候选；不能因网上有现成案例而提高方案复杂度。

### 2. 等待选择

用户确认方案及高影响项前，只能给出比较、问询和最小验证建议；不得把候选协议、UI、引脚映射、模型或代码结构当成最终实现。

用户选择后，将未定项明确写为“待确认假设”，再使用 `templates/project-architecture.md` 和 `templates/serial-protocol-decision.md` 输出工程方案。

最终通信设计前，必须单独确认是否需要心跳、ACK、序号、重发和超时；其触发条件、周期、超时动作和下位机处理方式均以题面或用户选择为准。不得因“常见做法”而自动加入心跳包或 ACK。

### 3. 选择视觉路线

- 颜色/激光：优先 `img.find_blobs()`、ROI、曝光/白平衡和时序过滤。
- 黑线、边框、靶纸和尺寸：优先几何、标定、单应性或物理坐标映射。
- 棋盘/格点：先定位棋盘坐标系，再做占用状态差分和落子映射。
- 二维码/AprilTag 等编码标记：先确认需要的是载荷内容、固定 ID、角点/姿态还是测距；比较 QR 与 AprilTag 的可读距离、光照、打印尺寸、ROI 和坐标映射，不把二者视为可无条件互换。仅使用官方 MaixPy `find_qrcodes()` 或 `find_apriltags()` 等已核验 API。
- 类别语义或复杂外观：先确认 MaixPy/固件版本与模型可用性，再选择 YOLOv5、YOLOv8、YOLO11 或 YOLO26；无数据集时使用 `templates/yolo-data-and-training.md` 先做采集、标注、训练和验证计划。
- 混合方案：传统视觉提供几何/ROI 约束，模型输出类别或复杂目标。

需要按电赛视觉模式细化识别、标定、状态和安全策略时，读取 `references/nuedc-vision-archetypes.md` 中与题面匹配的章节；不要把不相干题型的做法塞进当前工程。

用户确认需要板端现场观测或调参时，读取 `references/on-device-tuning-profile.md`。它只提供可选的显示/输入/参数边界和验证规则：无屏、无输入或用户不需要调参时，继续使用现有无 UI 或替代观测方案，不生成伪造的触摸/按键逻辑。

## 已有工程与运行期联调

- 已有工程的调试、增量功能或下位机联调，读取 `references/existing-project-integration.md`；保留已验证的端口、引脚、波特率、协议和安全联锁，只追问本次改动所需的信息。
- MaixVision 仅是工程、部署、下载和调试环境；板端运行时实现仍使用 MaixPy，不得把 IDE 操作写成 Python API。
- 用户遇到 MaixVision 的设备连接、在线运行、项目运行、实时预览、文件/模型上传、代码补全、打包安装或日志报错时，先读取 `references/maixvision-debugging.md`，收集版本、连接方式、完整错误和最小复现，再区分 IDE、设备、工程资源和板端代码问题。
- 遇到多文件、资源、打包或“电脑能看见但板端不一致”的问题时，使用 `templates/maixvision-debug-evidence.md` 建立一次调试证据记录：从源码快照、工程清单、运行/部署方式、设备运行身份、接口契约、资源到现象逐项关联。未完成该链路前，不得把编辑器提示、电脑端文件或单次现象当作板端最终事实。
- 视觉输出先经过候选、确认、缓存、丢失等状态处理，再按用户确认的协议发送。多帧数、目标选择、离群抑制和丢失策略必须可配置，并以题目时限和闭环需求为准。
- 闭环联调按“固定测试包和下位机解析 → 相机 → 最小识别 → 稳定状态 → 低速安全控制”推进；每轮只变更一个因素。

## 工程化输出

按 `templates/project-architecture.md` 选择工程规模：最小验证只交付单一硬件/API验证；紧凑工程默认只有唯一 `main.py`，仅在参数独立调节/多处复用、拆分能降低复杂度或存在独立风险时增加 `config.py`、任务文件或测试；完整闭环工程才使用通信、显示、模型、执行安全和多模块分层。每个文件都必须有生成理由和不生成同类模块的理由；没有通信、UI、模型、闭环或独立风险时，不得为统一目录生成空模块。模块只承担一个职责；状态有来源、有效性、时间戳和错误信息；代码以可维护、可调和可降级为目标，不以堆叠冗余分支代替结构。

详细架构见 `references/architecture-patterns.md`，调试顺序见 `references/debugging-playbook.md`。

### 完整工程目录交付

用户确认方案后，按已选工程规模生成可打开的 MaixVision 工程目录，而不是只输出零散代码片段。紧凑或完整工程必须有唯一 `main.py` 入口，以及被入口实际导入的必要模块、配置、测试和已提供的模型/资源；先展示仅含必要文件的目录树，再生成所有文件内容。

- 板端文件一律使用项目内相对路径；不得依赖用户电脑绝对路径或未随工程部署的文件。
- 用户只需在 MaixVision 打开工程文件夹并运行**完整项目**，即可向 MaixCAM 部署并开始调试；多文件、模型或资源项目不得指导用户只运行当前文件。
- 首次运行必须至少给出可观察的相机/显示/状态输出或明确的安全错误，便于逐层调试。
- 多文件、资源或打包工程的首启日志必须可识别执行阶段、模块、运行身份、配置/资源状态和安全降级原因；调试字段不得含电脑绝对路径、账号、密码、令牌或私钥。
- 未提供 YOLO `.mud`、授权资源或必要硬件信息时，不得声称工程可完成最终任务；生成可运行的采集、相机、传统视觉或模型加载验证工程，并在入口显示缺失项和安全降级状态。
- 无通信需求时不创建 `communication.py`；无独立 UI 需求时不创建显示模块；无模型时不创建模型目录；无独立风险时不创建未执行的测试。可观察首启状态可保留在 `main.py`，不以拆分文件数量衡量工程化程度。
- 打包/安装配置仅在用户要求离线应用或已有明确规范时加入；在线项目调试不依赖臆造的打包配置。
- 最终工程必须在目标 MaixCAM 或 MaixCAM Pro 上执行性能验证，使用 `references/performance-validation.md` 和 `templates/performance-report.md` 记录帧率、端到端时延、稳定性、显示/串口负载和资源异常。未在目标板实测时，只能标记为“待实测”，不得声称性能达标。
- 性能记录必须区分相机采集速率、视觉处理/有效检测速率和实际控制发布频率；不得以相机标称 FPS 或单一瞬时 FPS 代替闭环性能。板端调参 UI 只可在其刷新预算内运行，不得抢占安全控制或掩盖性能瓶颈。
- 发现帧率低、时延超标、卡顿、内存增长、模型失败、通信积压或重启时，先输出问题、证据、可能瓶颈、优化选项、代价和回归测试；用户确认会改变精度、视觉路线或闭环时序的优化后再实施。

完整目录约束见 `templates/project-architecture.md`，MaixVision 打开、运行和资源问题见 `references/maixvision-debugging.md`，性能验证见 `references/performance-validation.md`。

## 发布前 Skill 回归自测

修改 Skill、模板或参考资料后，维护者必须使用 `references/validation-scenarios.md` 执行对应场景的可判定断言并记录通过/失败证据。任何“信息不足时直接生成最终协议/工程”“已有工程却未先阅读”“YOLO 无数据却声称可训练完成”的失败，都阻止发布。

## MaixCAM Pro 语法硬规则

生成的 MaixPy 工程代码注释默认使用中文；保留 Python 关键字、MaixPy API、文件名、标识符和协议字段的原有英文拼写。采用“工程级关键注释”：对模块职责和硬件假设、配置的单位/范围/影响、公共任务接口的输入输出与坐标/失效语义、状态转换与非直观时序、以及安全降级和性能取舍写清原因或契约；避免逐行重复代码含义。完整规则见 `references/api-syntax-guard.md`，工程落点见 `templates/project-architecture.md`。快速验证脚本只保留硬件假设、预期现象和关键失败条件等必要注释。用户明确要求其他语言时按用户要求执行。

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

输出任何 MaixPy 代码前，读取 `references/api-syntax-guard.md` 完成 API、运行时边界、字段和 Python 语法自检；无法从官方资料确认的版本敏感调用必须标注假设或改为更小的验证代码。

## 交付前自检

使用 `templates/acceptance-checklist.md` 自检：

- 工程是否职责清晰、可独立测试、可维护且避免无意义冗余。
- 工程规模与每个文件是否由题目风险和实际依赖证明必要；是否在满足约束后选择了最简路线。
- 协议、UI、坐标与失效策略是否已由用户确认。
- 触发在线检索时，官方事实、社区经验、未证实项和来源链接是否明确区分。
- 正向代码是否只使用官方 MaixPy API。
- 公开发布文本是否不含个人信息、令牌、本机路径、私钥或未经授权的数据集。

## 参考来源

- MaixPy 文档首页: https://wiki.sipeed.com/maixpy/doc/zh/index.html
- MaixPy UART: https://wiki.sipeed.com/maixpy/doc/zh/peripheral/uart.html
- MaixPy Camera: https://wiki.sipeed.com/maixpy/doc/zh/vision/camera.html
- MaixPy find_blobs: https://wiki.sipeed.com/maixpy/doc/zh/vision/find_blobs.html
- MaixPy YOLO: https://wiki.sipeed.com/maixpy/doc/zh/vision/yolov5.html
- MaixPy 二维码: https://wiki.sipeed.com/maixpy/doc/zh/vision/qrcode.html
- MaixPy AprilTag: https://wiki.sipeed.com/maixpy/doc/zh/vision/apriltag.html
