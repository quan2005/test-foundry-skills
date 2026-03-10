---
name: api-test-creator
description: Generate API acceptance assets from reviewed test cases and OpenAPI or Swagger inputs. Use when Codex needs to turn a requirements document, approved test cases, and swagger.json into Hurl smoke/regression scripts, Schemathesis boundary plans, and API coverage or gap notes.
---

# API Test Creator

将已评审通过的测试用例转换成 API 验收测试资产。默认输出 Hurl 主回归脚本和 Schemathesis 边界测试计划，不负责 UI 验收，也不替代性能测试。

## Dependency

- 强依赖官方的 [`playwright-interactive`](https://github.com/openai/skills/tree/main/skills/.curated/playwright-interactive) 来读取登录后的需求文档、Swagger 页面和内网补充说明。
- 在 Codex 中优先安装到 `~/.codex/skills/playwright-interactive`；在 Claude Code 中安装到 `~/.claude/skills/playwright-interactive` 或 `.claude/skills/playwright-interactive`。
- 如果关键接口说明位于登录态页面而运行环境没有 `playwright-interactive`，不要用外部搜索代替真实文档，直接提示先安装依赖。

## Workflow

1. 确认测试用例评审已通过；如果未通过，先返回缺口，不生成脚本。
2. 阅读需求文档、测试用例和 `swagger.json`。
3. 用业务场景反推关键接口和调用链路。
4. 将稳定的主流程放进 Hurl。
5. 将 schema 边界、negative、fuzz 补充项放进 Schemathesis 计划。
6. 输出脚本骨架、覆盖矩阵和缺口说明。

## Source Access Rules

- 如果需求文档、接口说明或补充规则位于需要登录的内部系统，优先使用 Playwright 复用当前浏览器会话读取，不要先走外部搜索。
- 对内部链接，不要默认使用公开搜索、公共镜像或转译服务抓取内容。
- 如果 `swagger.json` 可直接访问，就以原始接口文档为准；如果接口说明分散在多个内网页面里，先用浏览器上下文补齐再生成资产。
- 如果关键信息仍被权限阻塞，把阻塞项列入缺口清单，不要把未知接口语义写进 Hurl 或 Schemathesis。

## Output Contract

默认输出到 `./test/{yyMMdd}_{requirement_slug}/api_tests/`。

- `yyMMdd`
  使用当前本地日期，例如 `260309`
- `requirement_slug`
  优先复用 `test-case-creator` 已使用的需求标识；没有现成标识时，从需求标题、版本短名或用户给定标识生成小写 snake_case
- 示例
  `./test/260309_sandbox_v2_1/api_tests/`

- `smoke.hurl`
  核心主路径、鉴权、健康检查、关键接口连通性。
- `regression.hurl`
  主要业务流、关键异常、典型权限与状态变化。
- `schemathesis-plan.md`
  说明哪些 operation 走边界补测、用什么模式、有哪些风险和待澄清接口。

必要时在 `schemathesis-plan.md` 中追加“swagger 缺口”和“接口待澄清项”章节，而不是把不明确内容直接写进 Hurl。
如果同一需求已经存在 `test_cases/`，默认写入同级 `api_tests/`，不要另起一个新的需求目录。

## Tool Split

- `Hurl`
  主力 API smoke / regression
- `Schemathesis`
  只补 schema 边界、negative、fuzz

不要反过来用 Schemathesis 代替业务主回归。

## Hurl Rules

- 每个 `.hurl` 文件表达一组明确业务意图，不要把所有接口塞进一个超长文件。
- 优先断言状态码、关键响应字段、关键副作用，不断言整包噪声字段。
- 通过 capture 复用动态 ID、token、trace id、业务对象主键。
- 通过变量文件或环境变量注入 base URL、账号、密钥，不在脚本中写死。
- 如果接口行为依赖前序请求，显式保留链路，而不是拆成无上下文的孤立请求。

## Schemathesis Rules

- 只针对 schema 完整、输入约束明确的 operation 规划自动边界测试。
- 优先覆盖：
  - 必填字段缺失
  - 类型错误
  - 枚举越界
  - 长度或范围边界
  - 响应结构与 schema 不匹配
- 如果 swagger.json 本身缺字段说明、枚举约束或响应 schema，不要伪造规则，直接列入缺口清单。

## Resources

- 读取 `references/hurl-authoring-guidelines.md`，统一 Hurl 文件结构和断言方式。
- 读取 `references/schemathesis-usage-patterns.md`，决定 positive、negative、all 的使用边界。
- 读取 `references/api-coverage-matrix.md`，将业务场景映射到 endpoint / method / tool。
- 使用 `assets/smoke-template.hurl`、`assets/regression-template.hurl` 和 `assets/schemathesis-plan-template.md` 作为默认骨架。
