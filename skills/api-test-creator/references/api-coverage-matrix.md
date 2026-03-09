# API 覆盖矩阵

将业务场景映射到接口和工具。

| 业务场景 | 接口 | Method | 主工具 | 备注 |
| --- | --- | --- | --- | --- |
| 登录获取 token | `/auth/login` | POST | Hurl | smoke 必选 |
| 主对象创建 | `/objects` | POST | Hurl | 主流程 |
| 对象查询 | `/objects/{id}` | GET | Hurl | 回查副作用 |
| 参数边界 | 任意 schema 明确接口 | 任意 | Schemathesis | 边界补测 |
| 响应结构合法性 | 任意 schema 明确接口 | 任意 | Schemathesis | 非主流程 |

## 决策规则

- 只要是主业务流，先落 Hurl
- 只要是 schema 边界，优先落 Schemathesis
- 如果两者都需要，Hurl 保业务语义，Schemathesis 保边界探索
