# image-to-pptx-ir Skill Pack

这个 Skill 用于把 PPT 截图/设计图解析为高保真 PPTX-IR / Render JSON，再生成可编辑 PPTX。

## 文件说明

- `SKILL.md`：核心技能说明
- `prompts/image_to_render_json_prompt.md`：图片转 Render JSON 提示词
- `prompts/render_json_to_pptx_prompt.md`：Render JSON 转 PPTX 提示词
- `templates/render.schema.json`：Render JSON Schema
- `templates/semantic.schema.json`：Semantic JSON Schema
- `checklists/pptx_visual_validation.md`：视觉检查清单
- `examples/cluster_communication.render.example.json`：示例片段

## 推荐使用方式

1. 先让 AI 读取图片并输出 semantic.json + render.json
2. 使用 render.json 生成 PPTX
3. 导出 PNG 预览
4. PowerPoint 原生打开检查
5. 修正问题并回写 render.json
