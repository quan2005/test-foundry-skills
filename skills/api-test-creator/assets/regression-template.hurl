# Regression: 关键业务回归

# 场景：创建 -> 查询 -> 更新 -> 校验副作用

POST {{base_url}}/resource
Authorization: Bearer {{token}}
Content-Type: application/json
{
  "name": "demo"
}
HTTP 201
[Captures]
resource_id: jsonpath "$.id"

GET {{base_url}}/resource/{{resource_id}}
Authorization: Bearer {{token}}
HTTP 200
[Asserts]
jsonpath "$.id" == "{{resource_id}}"

# TODO: 补充异常、权限、状态流转断言
