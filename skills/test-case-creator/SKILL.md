---
name: test-case-creator
description: "TestFoundry Stage 1 - Requirements Review: turn PRD/spec inputs into review-ready test maps, module matrices, and clarification issues. Use when Codex needs structured test review assets before API, UI, or performance asset generation."
---

# Test Case Creator

作为 TestFoundry Stage 1，该 skill 将需求文档转换成评审可用的测试用例资产。默认先完成需求理解、覆盖拆解、问题标注和评审材料整理，不要直接生成 API、UI 或性能测试脚本。

## Dependency

- 强依赖官方的 [`playwright-interactive`](https://github.com/openai/skills/tree/main/skills/.curated/playwright-interactive) 来读取登录后页面、内部文档和真实浏览器上下文。
- 在 Codex 中优先安装到 `~/.codex/skills/playwright-interactive`；在 Claude Code 中安装到 `~/.claude/skills/playwright-interactive` 或 `.claude/skills/playwright-interactive`。
- 如果任务涉及飞书、Confluence、内部 wiki 或任何需要登录的需求来源，而运行环境没有 `playwright-interactive`，不要退化到外部搜索，直接提示先安装依赖。

## Workflow

1. 阅读需求文档，先建立功能、角色、状态、异常、边界五类覆盖视角。
2. 先产出 1 张总览 Mermaid，再按业务模块拆成若干张模块 Mermaid；模块数量由需求实际结构决定，模块较少时按实际数量输出，模块较大时继续按二级业务域拆分。
3. 将需求中的待澄清项、矛盾项、依赖前提单独列出，不要混入正常用例节点。
4. 产出 Mermaid/Markdown 总览图、模块图（每个模块文档内自带测试矩阵）和评审问题清单。
5. 给出评审建议，明确哪些内容已满足进入 API/UI/Performance 生成阶段，哪些内容仍需补充。

## Source Access Rules

- 如果需求文档位于飞书、Confluence、内部 wiki 或其他需要登录认证的系统，优先使用 Playwright 复用当前浏览器登录态读取正文。
- 对内部文档，不要默认尝试外部搜索、公开索引页、转译镜像或公共抓取服务作为兜底。
- 如果页面能部分读取，先提取当前账号可见正文，并把缺失部分记录进评审问题清单。
- 如果在浏览器已登录的前提下仍无法访问完整内容，再要求用户提供可访问版本或导出副本，不要用猜测补内容。

## Output Contract

默认输出到 `./tests/{yyMMdd}_{requirement_slug}/test_cases/`。

- `yyMMdd`
  使用当前本地日期，例如 `260309`
- `requirement_slug`
  从需求标题、版本短名或用户给定标识生成，统一转成小写 snake_case，例如 `sandbox_v2_1`
- 示例
  `./tests/260309_sandbox_v2_1/test_cases/`

- `mindmap.md`
  使用 `assets/mindmap-template.md`，输出 1 张总览 Mermaid、模块拆分索引、覆盖概览、评审结论。
- `module-{nn}-<module_slug>.md`
  使用 `assets/module-map-template.md`，按实际模块数量连续编号输出；每个文件只覆盖一个业务模块，文档标题直接使用真实模块名称，输出模块级 Mermaid 图、场景覆盖说明、关键前置条件，以及该模块的测试矩阵表。
- `review-issues.md`
  使用 `assets/review-issues-template.md`，输出待澄清项、矛盾项、评审动作。

不要默认把所有内容塞进一张 Mermaid 里；只有需求极小、模块不超过 2 个时，才允许减少模块图数量。
同一需求的下游 API/UI/Performance Creator skill 必须复用同一个 `{yyMMdd}_{requirement_slug}` 根目录，只切换到各自子目录。

## Rendering Strategy

- Mermaid 默认使用 `flowchart`，不是 `mindmap`。总览图优先 `flowchart LR`，模块图优先 `flowchart TB`。
- 总览图只保留主题、模块、关键场景簇、待澄清/有冲突入口，不展开全部用例细节。
- 模块图才承载主路径、异常、边界、权限、依赖人工确认等具体用例。
- 超过单图可读阈值时继续拆分，不要为了“只出一张图”牺牲评审体验。
- 完整覆盖关系放在各模块文档内的测试矩阵表中，不要试图用一张图表达所有信息。

## Coverage Rules

- 优先按用户价值和业务主路径拆模块，不先按接口或页面拆。
- 模块标题必须使用真实业务模块名称，例如“订单创建”“审批流配置”，不要写成泛化标题如“模块测试图”。
- 每个场景至少检查：
  - 入口条件
  - 角色差异
  - 状态变化
  - 异常路径
  - 边界条件
- 对无法从需求直接确认的内容，显式标成“待澄清”，不要自己补业务规则。
- 对相互冲突的描述，显式标成“有冲突”，同时引用冲突来源。
- 评审未通过前，不生成下游 API/UI/Performance 资产。

## Review Heuristics

- 如果总览图已经把所有细节铺满，说明拆分策略失败。
- 如果脑图只有 happy path，没有异常、边界、权限、状态变化，说明覆盖不足。
- 如果需求中存在隐含依赖，例如外部系统、账号、测试数据、定时任务，要单独列出。
- 如果一段需求无法映射到任何可验证用例，要在评审清单里说明原因。
- 如果多个模块共享同一条业务规则，既要在公共规则区体现，也要在各模块场景中引用。
- 如果图能看懂但无法追踪到具体用例，说明模块文档内的测试矩阵不完整。

## Resources

- 读取 `references/requirements-analysis.md`，建立需求拆解顺序和问题识别方式。
- 读取 `references/mindmap-structure.md`，统一 Mermaid 总览图、模块图、矩阵表的结构和标记风格。
- 读取 `references/review-criteria.md`，判断是否具备进入自动化生成阶段的条件。
- 使用 `assets/mindmap-template.md`、`assets/module-map-template.md` 和 `assets/review-issues-template.md` 作为默认产物骨架。
