---
name: ui-test-creator
description: Create Midscene-based UI automation assets from reviewed test cases and live pages. Use when Codex needs to read a requirements document, approved test cases, and a website URL, then generate Midscene functional cases plus human-like visual and layout review notes based on the requirements and the current UI.
---

# UI Test Creator

将已评审通过的测试用例转换成 Midscene 可消费的 UI 自动化资产。默认输出双层结果：功能路径用例，以及更像人工评审的视觉风格与布局验收清单。

## Dependency

- 强依赖官方的 [`playwright-interactive`](https://github.com/openai/skills/tree/main/skills/.curated/playwright-interactive) 来观察真实页面、复用登录态并读取内部站点。
- 在 Codex 中优先安装到 `~/.codex/skills/playwright-interactive`；在 Claude Code 中安装到 `~/.claude/skills/playwright-interactive` 或 `.claude/skills/playwright-interactive`。
- 如果运行环境没有 `playwright-interactive`，不要把 UI 测试生成退化成纯静态猜测；遇到真实页面和登录态依赖时应先提示安装依赖。

## Workflow

1. 确认测试用例评审已通过；如果未通过，先返回缺口，不生成 UI 资产。
2. 阅读需求文档、测试用例和网站 URL。
3. 抽取关键用户路径、关键页面、关键状态切换点。
4. 观察页面现状，包括布局、信息层级、视觉风格、文案呈现、反馈状态。
5. 生成 Midscene 功能路径用例。
6. 生成视觉风格与布局验收清单。
7. 标记需要人工确认的账号、数据、环境状态和页面前置条件。

## Source Access Rules

- 如果需求文档或内部页面需要登录，优先使用 Playwright 复用当前浏览器登录态读取，不要把外部搜索当成默认方案。
- 对网站页面现状的观察，优先来自真实页面上下文，而不是搜索结果页或公开缓存。
- 如果当前账号只能看到部分页面或部分正文，先记录“可见事实”和“权限缺口”，不要脑补缺失内容。
- 如果内部页面无法稳定访问，再要求用户补截图、导出文档或可访问环境。

## Output Contract

默认输出到 `output/automation-factory/{yyMMdd}_{requirement_slug}/ui_tests/`。

- `yyMMdd`
  使用当前本地日期，例如 `260309`
- `requirement_slug`
  优先复用 `test-case-creator` 已使用的需求标识；没有现成标识时，从需求标题、版本短名或用户给定标识生成小写 snake_case
- 示例
  `output/automation-factory/260309_sandbox_v2_1/ui_tests/`

- `midscene-functional-cases.md`
  Midscene 自然语言步骤，聚焦关键用户路径和关键页面状态。
- `midscene-visual-review.md`
  像人工评审一样的视觉风格、布局、信息层级、交互反馈观察点。

如果页面较多，允许按模块拆小节，但仍保留统一的评审语义。
如果同一需求已经存在 `test_cases/`，默认写入同级 `ui_tests/`，不要另起一个新的需求目录。

## Functional Rules

- Midscene 是主力 UI 自动化表达层。
- 输出不是 Playwright locator 脚本，不写 DOM 选择器优先级策略。
- 功能路径优先覆盖：
  - 登录
  - 关键导航
  - 核心表单提交
  - 核心查询或审批
  - 关键结果反馈
- 每条用例都写清：
  - 前置条件
  - 入口页面
  - 用户动作
  - 预期页面反馈
  - 失败时的观察点

## Visual Review Rules

视觉验收固定以“需求文档 + 页面现状”为基准，不做像素级回归。

必须覆盖：

- 页面整体风格是否符合需求语义
- 信息层级是否清晰
- 版式和布局是否自然
- 关键区域是否像人工评审那样“看起来对”
- 文案、按钮、表单、反馈区域是否协调

优先写人类评审语言，例如：

- “主 CTA 是否足够突出”
- “首屏信息密度是否过高”
- “表单标签与输入框的对应关系是否自然”
- “成功/失败反馈是否足够明确”

避免只写空泛形容词，例如“页面更美观一些”“感觉不够高级”。

## Boundaries

- UI 层不负责接口边界和压测。
- 如果问题明显属于接口行为或数据规则，记录为依赖问题，不把它伪装成 UI 视觉问题。
- 如果页面现状与需求明显不一致，要在视觉评审和功能用例里同时记录差异。

## Resources

- 读取 `references/midscene-case-patterns.md`，统一 Midscene 自然语言动作风格。
- 读取 `references/ui-path-design.md`，按关键用户路径组织页面和用例。
- 读取 `references/visual-review-criteria.md`，统一视觉与布局观察点。
- 读取 `references/test-data-preconditions.md`，收集账号、数据、环境前置条件。
- 使用 `assets/midscene-functional-template.md`、`assets/midscene-visual-review-template.md` 和 `assets/ui-review-checklist.md` 作为默认骨架。
