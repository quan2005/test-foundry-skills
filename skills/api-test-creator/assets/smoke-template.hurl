# Smoke: 核心 API 可用性验证

# 1. 健康检查
GET {{base_url}}/health
HTTP 200

# 2. 登录
POST {{base_url}}/auth/login
Content-Type: application/json
{
  "username": "{{username}}",
  "password": "{{password}}"
}
HTTP 200
[Captures]
token: jsonpath "$.token"

# 3. 关键主路径
# TODO: 按业务替换 endpoint、body、断言
GET {{base_url}}/todo
Authorization: Bearer {{token}}
HTTP 200
