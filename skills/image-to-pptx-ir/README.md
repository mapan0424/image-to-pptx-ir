# image-to-pptx-ir Skill Pack

这个 Skill 用于把 PPT 截图/设计图解析为高保真 PPTX-IR / Render JSON，再生成可编辑 PPTX。

它的重点不是“一步生成 PPTX”，而是把视觉理解、结构化 IR、PPTX 生成和回归检查拆开，让每次修复都能回写到 `render.json`，避免最后只得到一张不可维护的截图。

## 文件说明

- `SKILL.md`：核心技能说明
- `prompts/image_to_render_json_prompt.md`：图片转 Render JSON 提示词
- `prompts/render_json_to_pptx_prompt.md`：Render JSON 转 PPTX 提示词
- `templates/render.schema.json`：Render JSON Schema
- `templates/semantic.schema.json`：Semantic JSON Schema
- `checklists/pptx_visual_validation.md`：视觉检查清单
- `examples/cluster_communication.render.example.json`：示例片段
- `references/complex-icon-assets.md`：复杂图标透明素材工作流
- `references/spec.md`：PPTX-IR 规范说明
- `references/workflow.md`：完整执行流程
- `references/visual-validation.md`：视觉回归校验方法

## 推荐使用方式

1. 先让 AI 读取图片并输出 semantic.json + render.json
2. 使用 render.json 生成 PPTX
3. 导出 PNG 预览
4. PowerPoint 原生打开检查
5. 修正问题并回写 render.json

## 关键约束

- 不跳过 IR：不要直接从图片生成 PPTX 或 HTML。
- 文本、箭头、虚线、图层、图标和父子边界都必须显式写入 Render JSON。
- 复杂 AI 图标、渐变图标、3D 图标优先保留为带 Alpha 的独立图片素材，不强行替换成相似图标库图标。
- 每次视觉修正都先改 `render.json`，再重新生成和验证。
