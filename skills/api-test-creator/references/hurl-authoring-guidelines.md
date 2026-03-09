# Hurl 编写约定

## 文件划分

- `smoke.hurl`
  只保留健康检查、鉴权、核心主路径、关键可用性验证
- `regression.hurl`
  保留完整业务链路、典型异常、典型权限校验

## 请求组织

- 先写注释说明业务意图
- 再写请求
- 再写断言和 capture

示例骨架：

```hurl
# 创建订单主路径
POST {{base_url}}/orders
Content-Type: application/json
Authorization: Bearer {{token}}
{
  "customerId": "{{customer_id}}",
  "amount": 100
}
HTTP 201
[Captures]
order_id: jsonpath "$.id"
[Asserts]
jsonpath "$.status" == "CREATED"
```

## 断言优先级

1. 状态码
2. 关键响应字段
3. 关键业务状态
4. 必要的 header

不要默认断言所有字段。

## 变量与环境

- `base_url`
- `token`
- 业务对象 ID
- 测试用户账号

这些值优先来自变量文件或环境变量。
