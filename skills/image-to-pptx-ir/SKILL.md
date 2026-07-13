---
name: image-to-pptx-ir
description: 从 PPT 截图/设计图中解析出高保真 PPTX-IR / Render JSON，并指导生成可编辑 PPTX。适用于“图片 → JSON → PPTX”的高保真复刻工作流，重点控制虚线、箭头方向、复杂 AI 图标透明素材、文本不换行、父子边界和 PowerPoint 原生渲染差异。
---

# Image to PPTX-IR Skill

## 1. 目标

当用户提供一张 PPT 页面截图、设计稿图片或视觉参考图，并希望生成高保真、可编辑 PPTX 时，使用本 Skill。

本 Skill 的核心目标不是“描述图片”，而是将图片解析为可执行的 PPT 绘图中间表示：

```text
图片 / 视觉参考图
  → semantic.json
  → render.json / PPTX-IR
  → 可编辑 PPTX
  → 渲染截图回归检查
  → 修正 render.json
```

## 2. 核心原则

### 2.1 不直接从图片生成 PPTX

禁止直接跳过结构化步骤生成 PPTX。必须先得到 Render JSON / PPTX-IR。

错误流程：

```text
图片 → PPTX
图片 → HTML → PPTX
```

推荐流程：

```text
图片 → semantic.json → render.json → PPTX
                         ↓
                      HTML/PNG 预览
```

### 2.2 区分两类 JSON

#### semantic.json

用于表达页面语义，不直接生成 PPTX。

包含：

- 页面标题
- 主要区域
- 业务逻辑
- 模块关系
- 文案内容

#### render.json / PPTX-IR

用于生成 PPTX。必须包含：

- 精确坐标
- 基础图元
- 图层顺序
- 文本框规则
- 虚线/实线
- 箭头方向
- 图标库绑定
- 父子边界约束
- PowerPoint 渲染安全规则

## 3. 图片解析流程

### 3.1 固定画布

先读取图片尺寸，使用原图像素坐标作为基准。

示例：

```json
{
  "canvas": {
    "width": 1304,
    "height": 706,
    "unit": "px"
  }
}
```

如需映射到 PPT 16:9：

```text
ppt_x = image_x / image_width  * 13.333
ppt_y = image_y / image_height * 7.5
ppt_w = image_w / image_width  * 13.333
ppt_h = image_h / image_height * 7.5
```

### 3.2 按区域分割

不要整图一次性粗略描述。必须先拆区：

1. 页面标题区
2. 顶部标签区
3. 左侧主体模块
4. 中间通道/连接区
5. 右侧主体模块
6. 底部配置/说明区
7. 图例区
8. 装饰元素区

每个区域单独解析，再合并为 render.json。

### 3.3 只允许基础图元

Render JSON 中不允许使用模糊组件。

禁止：

```json
{ "type": "card" }
{ "type": "icon" }
{ "type": "flow" }
{ "type": "channelRow" }
{ "type": "smartArt" }
```

必须展开为：

```text
text
rect
roundRect
line
connector
path
svgIcon
image
group
```

## 4. Render JSON 元素规范

### 4.1 通用字段

所有元素必须包含：

```json
{
  "id": "unique_element_id",
  "type": "rect",
  "x": 100,
  "y": 100,
  "w": 200,
  "h": 80,
  "zIndex": 10
}
```

### 4.2 形状字段

```json
{
  "type": "rect",
  "fill": "#FFFFFF",
  "stroke": "#667078",
  "strokeWidth": 1,
  "radius": 0,
  "dash": "solid"
}
```

形状规则：

- 外层大框如果源图是直角，必须 `type: rect` 且 `radius: 0`
- 内部卡片可以 `type: roundRect`
- 虚线框必须写 `dash: "dash"`
- 不能用圆角卡片替代直角外框

### 4.3 文本字段

所有文本必须包含 PowerPoint 安全控制：

```json
{
  "type": "text",
  "text": "高可用、高可靠",
  "x": 867,
  "y": 100,
  "w": 136,
  "h": 24,
  "fontFamily": "Microsoft YaHei",
  "fontSize": 16,
  "fontWeight": 700,
  "color": "#222222",
  "align": "center",
  "valign": "middle",
  "wrap": false,
  "fit": "shrink",
  "margin": 0,
  "zIndex": 50
}
```

硬规则：

- 短标签必须 `wrap: false`
- 标题必须 `wrap: false`
- 表格/配置内容建议拆成多行独立 text
- 不要把多行长文本塞进一个文本框
- 文本框宽度必须比视觉宽度多留 20%-30% 安全余量
- PowerPoint 打开后不能自动换行

### 4.4 箭头字段

所有箭头必须使用 connector，不要用普通 line 模糊表达。

```json
{
  "id": "channel_1_send_left_to_right",
  "type": "connector",
  "x1": 548,
  "y1": 186,
  "x2": 604,
  "y2": 186,
  "stroke": "#F04A23",
  "strokeWidth": 1.8,
  "dash": "solid",
  "beginArrow": "none",
  "endArrow": "triangle",
  "direction": "left_to_right",
  "semantic": "发送方向",
  "mustNotBeSegmented": true,
  "zIndex": 20
}
```

虚线箭头：

```json
{
  "id": "channel_1_receive_right_to_left",
  "type": "connector",
  "x1": 606,
  "y1": 209,
  "x2": 549,
  "y2": 209,
  "stroke": "#F04A23",
  "strokeWidth": 1.8,
  "dash": "dash",
  "beginArrow": "none",
  "endArrow": "triangle",
  "direction": "right_to_left",
  "semantic": "接收方向",
  "mustNotBeSegmented": true,
  "zIndex": 20
}
```

箭头硬规则：

- 必须明确 `solid / dash`
- 必须明确方向
- 必须明确箭头在哪一端
- 必须明确语义：发送方向 / 接收方向 / 加载配置
- 一根线就必须是一根线，不能拆段
- 黄色配置箭头通常应为“一侧一根完整虚线箭头”
- 箭头层级要高于可能遮挡它的白色框体

#### 箭头专项二次扫描

高密度 PPT 截图中，箭头头部经常只有 4-10px，容易被误判为普通线段。生成 render.json 前，必须对全图执行一次“连接线/箭头专项二次扫描”，不得只检查主流程区域。

必须逐区复核：

1. 框与框之间的短横线
2. 上下层之间的短竖线
3. 从虚线框、流程框、数据库框、容器框向外连接的短线
4. 虚线回流线、折线、L 形连接线
5. 红色、橙色、蓝色流程线末端的小三角/尖角
6. 图标周围 20px 内的短连接线，尤其是 `写入`、`KV`、`Region`、`数据库实例`、`路由/中间件` 等流程节点

判定规则：

- 线段末端如果存在同色三角形、尖角、楔形、短斜边收束，必须标为 `connector` 且设置 `endArrow: "triangle"`
- 线段起点如果存在箭头头部，必须设置 `beginArrow: "triangle"`
- 没有箭头头部时才允许 `beginArrow: "none"` / `endArrow: "none"`
- 竖向箭头必须明确 `direction: "top_to_bottom"` 或 `direction: "bottom_to_top"`
- 横向箭头必须明确 `direction: "left_to_right"` 或 `direction: "right_to_left"`
- 虚线箭头必须同时保留 `dash: "dash"` 和箭头头部，不能只画虚线
- L 形或折线箭头如果源图是一根连续箭头，应使用单个 connector/path 表达，并保留箭头端点

禁止把下列元素降级为普通 line：

```json
{
  "type": "line",
  "x1": 625,
  "y1": 235,
  "x2": 655,
  "y2": 235
}
```

如果源图在线尾有箭头，应改为：

```json
{
  "id": "write_to_kv",
  "type": "connector",
  "x1": 625,
  "y1": 235,
  "x2": 655,
  "y2": 235,
  "stroke": "#075FEA",
  "strokeWidth": 2,
  "dash": "solid",
  "beginArrow": "none",
  "endArrow": "triangle",
  "direction": "left_to_right",
  "semantic": "写入请求流向内容容器"
}
```

常见易漏区域：

- `业务系统/应用 → 路由/中间件层 → 数据集实例` 的竖向和分支箭头
- `写入请求 → KV → Region/节点集群` 的短横向箭头
- `Compaction/Merge → KV` 的向上箭头
- `Compaction/Merge → Region/节点集群` 的虚线回流箭头
- 底部指标条中圆点、半圆、星标之间的方向箭头
- 标题装饰线、说明带和流程框之间的小方向箭头

交付前必须回答：

- 本页共有多少个 `connector`？
- 其中多少个带 `endArrow` 或 `beginArrow`？
- 是否存在“源图有箭头、render.json 只有 line”的降级项？
- 是否存在箭头头部被白色框、图片、图标遮挡的情况？

### 4.5 图标字段

先把图标分类，再选择渲染方式：

1. 用户提供的原始 SVG 或透明 PNG：直接绑定本地素材。
2. 与标准图标库完全匹配的简单扁平图标：使用 `svgIcon`。
3. GPT 生图产生的 3D、渐变、发光、阴影或复杂组合图标：使用带 Alpha 通道的 `image`，不得强制替换成近似图标库图标。

素材来源优先级：

```text
用户提供的透明素材
→ 用户指定素材目录中的对应文件
→ 从原图裁切并做确定性 Alpha 抠图
→ 使用原图裁片进行参考图编辑并生成透明高清素材
→ 图标库精确匹配
```

禁止仅凭文字描述重新生成复杂图标。需要生成时，必须使用原图裁片作为视觉参考，并完成回贴相似度验证。

遇到复杂 AI 图标、3D 视觉主体或无图标库精确匹配时，必须读取并执行 [复杂图标素材工作流](references/complex-icon-assets.md)。

简单图标示例：

```json
{
  "id": "node_a_recv_icon",
  "type": "svgIcon",
  "library": "fontawesome",
  "icon": "faGear",
  "x": 164,
  "y": 203,
  "w": 24,
  "h": 24,
  "fill": "#F04A23",
  "zIndex": 40
}
```

推荐图标库：

- FontAwesome
- Lucide
- Material Symbols
- 自有 SVG 资源

禁止：

```json
{ "type": "icon", "name": "gear" }
```

因为这会导致渲染器临时绘制，视觉质量不可控。

复杂图标示例：

```json
{
  "id": "agentic_database_visual",
  "type": "image",
  "assetId": "agentic_database_hd",
  "assetPath": "assets/agentic_database_hd.png",
  "sourceMode": "gpt_image_reference_edit",
  "visualRole": "complexGeneratedIcon",
  "sourceBBox": { "x": 1024, "y": 168, "w": 420, "h": 252 },
  "alphaBBox": { "x": 86, "y": 120, "w": 850, "h": 720 },
  "x": 1024,
  "y": 168,
  "w": 420,
  "h": 252,
  "fit": "alphaBounds",
  "preserveAspectRatio": true,
  "hasAlpha": true,
  "allowLibrarySubstitution": false,
  "allowGenerativeRedraw": false,
  "similarityScore": 0.94,
  "zIndex": 40
}
```

硬规则：

- 图标素材不得包含本应可编辑的标题、标签、箭头、虚线、卡片边框或说明文字。
- 复杂主体可以作为独立图片对象；文字、框、线和流程关系仍使用 PPT 原生元素。
- 回贴时以透明内容的 `alphaBBox` 对齐源图的 `sourceBBox`，不能按整张透明画布直接缩放。
- 素材必须验证真实 Alpha 通道，禁止把棋盘格背景当成透明背景。
- 保留半透明发光、阴影和柔边，并检查白边、灰边和颜色污染。
- 用户提供素材目录时，本地素材优先，禁止擅自改画或用近似图标替换。

### 4.6 父子约束

每个 group / container 必须有 constraints：

```json
{
  "id": "node_a_panel",
  "type": "group",
  "x": 142,
  "y": 142,
  "w": 310,
  "h": 344,
  "constraints": {
    "paddingLeft": 18,
    "paddingRight": 18,
    "paddingTop": 12,
    "paddingBottom": 12,
    "childrenMustStayInside": true,
    "clipChildren": false
  },
  "children": []
}
```

校验规则：

```text
child.x >= parent.x + paddingLeft
child.x + child.w <= parent.x + parent.w - paddingRight
child.y >= parent.y + paddingTop
child.y + child.h <= parent.y + parent.h - paddingBottom
```

如果不满足，必须调整子元素坐标或缩小子元素宽度。

## 5. 图层规则

推荐 zIndex：

```json
{
  "layerRules": {
    "background": 0,
    "containerFrames": 10,
    "communicationArrows": 20,
    "innerBoxes": 30,
    "icons": 40,
    "texts": 50,
    "yellowConfigArrows": 60,
    "debugMarks": 999
  }
}
```

注意：

- 箭头如果被白色框遮住，需要提高 zIndex
- 文本通常在最上层
- 调试红框不能出现在最终稿
- yellow config arrows 不应被配置文件框或节点框遮挡

## 6. 校验清单

生成 PPTX 前必须检查：

### 6.1 形状

- 左右节点大框是否为直角矩形
- 内部线程框是否为圆角矩形
- 内部虚线框是否为虚线圆角矩形
- 通道框是否为虚线圆角矩形
- UDP 框是否为圆角矩形
- 配置文件框是否为圆角矩形

### 6.2 箭头

- 发送方向是否为实线
- 接收方向是否为虚线
- 箭头方向是否与源图一致
- 箭头头部是否在正确端
- 一根完整箭头是否被误拆成多段
- 黄色加载配置箭头是否一侧一根完整虚线箭头
- 箭头是否被其他元素遮挡

### 6.3 文本

- 标题是否换行
- 顶部标签是否换行
- 通道文字是否换行
- 配置文件内容是否自动换行
- 文本是否被压缩过度
- 字体是否被 PowerPoint 替换

### 6.4 边界

- 子元素是否超出父容器
- 小方块是否超出消息池
- M1/M2/M3/.../Mn 是否超出消息链表
- 竖向箭头是否压边或越界
- 左右镜像元素是否重新计算坐标，而不是机械复制

### 6.5 渲染

必须至少检查：

```text
1. PPTX 导出 PNG
2. PowerPoint 原生打开效果
```

LibreOffice / 服务端渲染正常，不代表 Microsoft PowerPoint 正常。

## 7. 输出要求

当用户要求“图片转 JSON”时，输出：

1. semantic.json
2. render.json
3. validationRules
4. potentialRisks

当用户要求“生成 PPTX”时：

1. 使用 render.json 生成 PPTX
2. 导出预览 PNG
3. 执行边界与重叠检查
4. 说明已修复项和剩余风险
5. 所有修改回写 render.json，不直接手工改 PPTX

## 8. 常见错误

### 错误一：把图片读成页面说明

错误：

```json
{
  "type": "diagram",
  "description": "左右两个节点通过 UDP 通信"
}
```

正确：

```json
{
  "type": "connector",
  "x1": 548,
  "y1": 186,
  "x2": 604,
  "y2": 186,
  "dash": "solid",
  "endArrow": "triangle"
}
```

### 错误二：图标临时绘制

错误：

```json
{ "type": "icon", "name": "send" }
```

正确：

```json
{
  "type": "svgIcon",
  "library": "fontawesome",
  "icon": "faPaperPlane"
}
```

### 错误三：没有 PowerPoint 文本安全宽度

错误：

```json
{
  "text": "高可用、高可靠",
  "w": 100
}
```

正确：

```json
{
  "text": "高可用、高可靠",
  "w": 136,
  "wrap": false,
  "fit": "shrink"
}
```

### 错误四：一根虚线箭头拆成多段

错误：

```json
[
  { "type": "line", "x1": 492, "y1": 548, "x2": 449, "y2": 529 },
  { "type": "line", "x1": 449, "y1": 529, "x2": 397, "y2": 505 },
  { "type": "connector", "x1": 397, "y1": 505, "x2": 354, "y2": 488 }
]
```

正确：

```json
{
  "type": "connector",
  "x1": 492,
  "y1": 548,
  "x2": 354,
  "y2": 488,
  "dash": "dash",
  "endArrow": "triangle",
  "mustNotBeSegmented": true
}
```

## 9. 交付标准

达到可接受效果必须满足：

- 页面整体结构与源图一致
- 所有文字可编辑
- 主要图形可编辑
- 虚线、实线、箭头方向正确
- 简单图标来自精确匹配的图标库或 SVG；复杂 AI 图标来自经过验证的透明高清素材
- 不出现明显超框
- PowerPoint 打开不自动换行
- 不依赖整页截图作为最终内容
- 复杂图标可作为 SVG 插入，但需要保持清晰
