# WAF 登录功能设计方案

## 1. 认证架构

### 1.1 认证方式
- 使用 **JWT (JSON Web Token)** 作为无状态认证方案
- 优势：无需服务器存储会话状态，便于水平扩展

### 1.2 认证流程
1. 用户输入用户名和密码登录
2. 后端验证凭据，生成 JWT token
3. 前端存储 token（localStorage）
4. 后续请求在请求头中携带 token
5. 后端验证 token 有效性
6. 用户登出时清除 token

## 2. 后端设计

### 2.1 依赖添加
需要添加以下依赖：
- `python-jose[cryptography]` - JWT 库
- `passlib[bcrypt]` - 密码加密
- `python-multipart` - 表单数据处理

### 2.2 数据结构

#### 用户模型
```python
# 简化版用户模型（内存存储）
users = [
    {
        "id": 1,
        "username": "admin",
        "password_hash": "$2b$12$...",  # bcrypt 加密的密码
        "role": "admin"
    }
]
```

#### JWT Token 结构
```json
{
  "sub": "1",  # 用户 ID
  "username": "admin",
  "role": "admin",
  "exp": 1678900000  # 过期时间
}
```

### 2.3 API 接口

#### POST /api/auth/login
- **功能**：用户登录
- **请求体**：
  ```json
  {
    "username": "admin",
    "password": "password"
  }
  ```
- **响应**：
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin"
    }
  }
  ```

#### POST /api/auth/logout
- **功能**：用户登出
- **响应**：
  ```json
  {
    "message": "Successfully logged out"
  }
  ```

#### GET /api/auth/me
- **功能**：获取当前用户信息
- **响应**：
  ```json
  {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
  ```

#### POST /api/auth/refresh
- **功能**：刷新 token
- **响应**：
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
  ```

### 2.4 中间件
- **AuthMiddleware**：验证请求头中的 token 有效性
- **保护范围**：所有需要认证的 API 接口

## 3. 前端设计

### 3.1 页面设计

#### 登录页面 (`/login`)
- 用户名输入框
- 密码输入框
- 登录按钮
- 错误提示

### 3.2 状态管理
- 使用 `localStorage` 存储 token
- 登录状态检查函数
- token 过期处理

### 3.3 路由守卫
- 保护需要认证的页面：
  - `/dashboard`
  - `/access-logs`
  - `/attack-logs`
  - `/ipv6-stats`
- 未登录用户重定向到 `/login`

### 3.4 API 服务改造
- 在所有 API 请求中添加 `Authorization` 头
- token 过期时自动跳转到登录页

## 4. 安全考虑

### 4.1 密码安全
- 使用 **bcrypt** 算法加密存储密码
- 禁止明文存储密码

### 4.2 Token 安全
- 设置合理的 token 过期时间（如 24 小时）
- 使用安全的签名算法（HS256）
- 存储密钥在环境变量中

### 4.3 其他安全措施
- 添加 CSRF 保护
- 实现请求速率限制，防止暴力破解
- 记录登录失败尝试

## 5. 实现步骤

### 5.1 后端实现
1. 添加依赖包
2. 实现认证工具函数
3. 添加认证 API 接口
4. 实现认证中间件
5. 保护需要认证的 API

### 5.2 前端实现
1. 添加登录页面
2. 实现登录状态管理
3. 添加路由守卫
4. 改造 API 服务
5. 测试登录流程

## 6. 测试计划

### 6.1 功能测试
- 正确用户名密码登录
- 错误用户名密码登录
- 登录后访问受保护页面
- 未登录访问受保护页面
- 登出功能
- Token 过期处理

### 6.2 安全测试
- 密码加密验证
- Token 签名验证
- CSRF 保护测试
- 暴力破解防护测试

## 7. 部署考虑

### 7.1 环境变量
需要设置以下环境变量：
- `SECRET_KEY` - JWT 签名密钥
- `ALGORITHM` - JWT 算法
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token 过期时间

### 7.2 默认用户
- 初始默认用户：`admin` / `admin123`
- 生产环境应修改默认密码

## 8. 代码结构

### 8.1 后端文件结构
```
backend/
├── main.py              # 主应用
├── auth/                # 认证模块
│   ├── __init__.py
│   ├── jwt.py           # JWT 工具函数
│   ├── password.py      # 密码工具函数
│   └── routes.py        # 认证路由
└── middleware/          # 中间件
    ├── __init__.py
    └── auth.py          # 认证中间件
```

### 8.2 前端文件结构
```
frontend/src/
├── views/
│   ├── Login.vue        # 登录页面
│   └── ...
├── services/
│   ├── api.js           # API 服务（添加认证头）
│   └── auth.js          # 认证服务
├── router/
│   └── index.js         # 路由配置（添加守卫）
└── store/
    └── auth.js          # 认证状态管理
```

## 9. 兼容性

### 9.1 向后兼容
- 保留现有的 API 接口
- 对需要保护的接口添加认证要求
- 确保未登录用户可以访问登录页面

### 9.2 前端兼容性
- 使用 localStorage 存储 token，兼容现代浏览器
- 支持 token 过期自动跳转到登录页

## 10. 性能考虑

### 10.1 后端优化
- JWT 验证缓存，减少重复验证开销
- 密码验证使用异步 bcrypt

### 10.2 前端优化
- 减少不必要的 token 验证请求
- 合理使用 localStorage，避免频繁读写

## 总结

本设计方案采用 JWT 无状态认证机制，实现了完整的登录功能，包括后端 API、前端页面和安全措施。方案兼顾了安全性、性能和用户体验，适合 WAF 项目的认证需求。
