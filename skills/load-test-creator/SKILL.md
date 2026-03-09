---
name: load-test-creator
description: Create k6 performance test plans and starter scenarios from reviewed test cases, interface details, and explicit performance targets. Use when Codex needs load, stress, spike, and soak assets, threshold recommendations, or performance gap analysis before running API capacity tests.
---

# Load Test Creator

将已评审通过的测试用例转换成 k6 压测资产。默认输出压测方案和脚本骨架，重点补齐负载模型、阈值和性能目标缺口，不负责接口功能正确性本身。

## Dependency

- 强依赖官方的 [`playwright-interactive`](https://github.com/openai/skills/tree/main/skills/.curated/playwright-interactive) 来读取登录后的性能目标文档、内网说明页和补充约束。
- 在 Codex 中优先安装到 `~/.codex/skills/playwright-interactive`；在 Claude Code 中安装到 `~/.claude/skills/playwright-interactive` 或 `.claude/skills/playwright-interactive`。
- 如果性能目标和容量约束位于登录态页面而运行环境没有 `playwright-interactive`，不要用公开搜索或经验默认值替代真实来源，直接提示先安装依赖。

## Workflow

1. 确认测试用例评审已通过；如果未通过，先返回缺口，不生成压测资产。
2. 阅读需求文档、测试用例、接口信息和性能目标。
3. 从已确认业务流中选择适合作为压测入口的路径。
4. 将业务流转换成 k6 场景骨架。
5. 为不同目标分别设计 load / stress / spike / soak。
6. 输出阈值、阶段、并发建议和缺口清单。

## Source Access Rules

- 如果性能目标、容量约束或业务前提写在需要登录的内部文档里，优先使用 Playwright 复用浏览器会话读取，不要默认走外部搜索。
- 对内部文档，不使用公开搜索、公共镜像或转译服务作为主获取方式。
- 如果只能读取部分目标或约束，先把可见内容转成 k6 计划，再把缺失指标列入缺口清单。
- 如果关键性能目标仍不可见，明确阻塞项，不要凭经验填默认性能承诺值。

## Output Contract

默认输出到 `output/automation-factory/{yyMMdd}_{requirement_slug}/load_tests/`。

- `yyMMdd`
  使用当前本地日期，例如 `260309`
- `requirement_slug`
  优先复用 `test-case-creator` 已使用的需求标识；没有现成标识时，从需求标题、版本短名或用户给定标识生成小写 snake_case
- 示例
  `output/automation-factory/260309_sandbox_v2_1/load_tests/`

- `k6-plan.md`
  说明压测目标、场景选择、数据准备、阈值建议、缺口项。
- `k6-scenarios.js`
  提供基础 k6 场景骨架，便于继续细化。

如果同一需求已经存在 `test_cases/`，默认写入同级 `load_tests/`，不要另起一个新的需求目录。

## Load Model Rules

- `load`
  验证常规负载下是否稳定
- `stress`
  验证超过预期负载后的退化行为
- `spike`
  验证突发高峰的瞬时承载能力
- `soak`
  验证长时间运行的稳定性和资源泄漏风险

不要把这些模式混成一个模糊的“压测脚本”。

## Relationship With Hurl

- Hurl 业务流可以作为压测输入来源。
- 不能直接把 Hurl 当成压测脚本。
- 必须补充：
  - 并发模型
  - stages
  - arrival rate 或 VU
  - thresholds
  - 数据准备与清理策略

## Missing Target Rules

如果性能目标未明确，默认显式列出缺口，例如：

- 缺少 TPS 目标
- 缺少 P95 / P99 目标
- 缺少错误率上限
- 缺少并发用户规模
- 缺少测试时长

不要自行发明性能承诺值。

## Resources

- 读取 `references/k6-scenario-patterns.md`，统一 k6 场景设计方式。
- 读取 `references/perf-targets-checklist.md`，判断性能目标是否足够执行。
- 读取 `references/hurl-to-k6-mapping.md`，将业务回归流映射到压测入口。
- 使用 `assets/k6-plan-template.md` 和 `assets/k6-scenario-template.js` 作为默认骨架。
