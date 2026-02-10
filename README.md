# WAF for Feiniu NAS

Web Application Firewall with IPv6 monitoring for Feiniu NAS，用于防护飞牛 NAS 并集成 IPv6 地址访问监测和大屏面板展示。

## 项目功能

### 核心功能
- **WAF 防护**：拦截 SQL 注入、XSS、命令注入等常见攻击
- **IPv6 监测**：实时监测 IPv6 地址访问情况
- **大屏面板**：实时展示访问统计、攻击告警、IPv6 分布等数据
- **3D 攻击来源地图**：可视化展示全球攻击来源分布，支持 2D/3D 切换
- **日志管理**：详细的访问日志和攻击日志记录
- **Docker 部署**：支持容器化部署，适合在 NAS 上运行

### 技术栈
- **后端**：Python 3.11, FastAPI, Uvicorn
- **前端**：Vue 3, Vite, ECharts, Ant Design Vue
- **部署**：Docker, Docker Compose, Nginx

## 项目结构

```
waf/
├── backend/           # 后端代码
│   ├── api/           # API 接口
│   ├── rules/         # WAF 规则
│   ├── services/      # 业务服务
│   ├── models/        # 数据模型
│   ├── utils/         # 工具函数
│   ├── main.py        # 主应用入口
│   ├── requirements.txt  # 依赖文件
│   └── Dockerfile     # 后端 Dockerfile
├── frontend/          # 前端代码
│   ├── src/           # 源代码
│   │   ├── assets/    # 静态资源
│   │   ├── components/ # 组件
│   │   ├── views/     # 页面视图
│   │   ├── router/    # 路由
│   │   ├── services/  # API 服务
│   │   ├── App.vue    # 主应用
│   │   └── main.js    # 入口文件
│   ├── public/        # 公共文件
│   ├── index.html     # HTML 模板
│   ├── package.json   # 依赖文件
│   ├── vite.config.js # Vite 配置
│   ├── nginx.conf     # Nginx 配置
│   └── Dockerfile     # 前端 Dockerfile
├── docker-compose.yml # Docker Compose 配置
└── README.md          # 项目文档
```

## 快速开始

### 1. Docker 部署（推荐）

#### 前提条件
- Docker 和 Docker Compose 已安装
- 网络连接正常
- NAS 主机上的 8009 和 89 端口未被占用

#### 部署步骤

1. **克隆项目**
   ```bash
   git clone <repository-url> waf
   cd waf
   ```

2. **启动服务**
   ```bash
   docker-compose up -d
   ```

3. **访问应用**
   - 前端面板：`http://NAS_IP:89`
   - 后端 API：`http://NAS_IP:8009/docs`

#### 网络模式
- 使用 `host` 网络模式，直接监控 NAS 主机的网络活动
- 能够捕获到所有网络请求，包括 IPv6 流量

### 2. 本地开发

#### 后端开发

1. **安装依赖**
   ```bash
   cd backend
   python -m pip install -r requirements.txt
   ```

2. **启动后端服务**
   ```bash
   python main.py
   ```

#### 前端开发

1. **安装依赖**
   ```bash
   cd frontend
   npm install
   ```

2. **启动前端服务**
   ```bash
   npm run dev
   ```

3. **访问开发环境**
   - 前端：`http://localhost:3000`
   - 后端：`http://localhost:8000`

## 核心功能说明

### WAF 防护

- **SQL 注入防护**：拦截包含 SQL 注入特征的请求
- **XSS 防护**：拦截包含 XSS 攻击特征的请求
- **命令注入防护**：拦截包含命令注入特征的请求

### IPv6 监测

- **实时统计**：IPv6 访问次数、占比等数据
- **趋势分析**：IPv6 访问趋势图表
- **详细记录**：IPv6 访问的详细日志

### 大屏面板

- **实时状态**：总访问量、攻击次数、最近访问等
- **图表展示**：IP 版本分布、攻击类型分布等
- **3D 攻击来源地图**：可视化展示全球攻击来源分布，支持 2D/3D 切换
- **最近攻击**：实时展示最近的攻击记录

## API 接口

### 访问日志
- **GET /api/access-logs**：获取访问日志
- **参数**：`limit` - 返回日志数量

### 攻击日志
- **GET /api/attack-logs**：获取攻击日志
- **参数**：`limit` - 返回日志数量

### IPv6 统计
- **GET /api/ipv6-stats**：获取 IPv6 统计数据

### 实时状态
- **GET /api/status**：获取实时状态数据

### 健康检查
- **GET /health**：健康检查接口

## 配置说明

### 后端配置

- **端口**：默认 8000
- **CORS**：默认允许所有来源（生产环境应配置具体地址）
- **日志限制**：访问日志最多保留 1000 条，攻击日志最多保留 500 条

### 前端配置

- **开发端口**：默认 3000
- **API 代理**：默认代理到 `http://localhost:8000`

### Docker 配置

- **前端端口**：默认 80
- **后端端口**：默认 8000
- **网络**：使用 `waf-network` 桥接网络

## 安全建议

1. **生产环境配置**
   - 配置具体的 CORS 来源
   - 启用 HTTPS
   - 设置访问密码

2. **规则优化**
   - 根据实际情况调整 WAF 规则
   - 定期更新规则库

3. **监控告警**
   - 配置攻击告警通知
   - 定期检查日志

## 故障排查

### 常见问题

1. **服务无法启动**
   - 检查 Docker 服务是否运行
   - 检查端口是否被占用

2. **前端无法访问后端**
   - 检查后端服务是否正常运行
   - 检查网络配置是否正确

3. **WAF 规则误报**
   - 调整 WAF 规则阈值
   - 检查规则是否过于严格

### 日志查看

```bash
# 查看后端日志
docker logs waf-backend

# 查看前端日志
docker logs waf-frontend
```

## 性能优化

1. **日志存储**
   - 生产环境建议使用数据库存储日志
   - 定期清理旧日志

2. **缓存策略**
   - 启用 Redis 缓存（可选）
   - 优化静态资源加载

3. **资源限制**
   - 根据 NAS 性能调整容器资源限制
   - 配置适当的内存和 CPU 限制

## 版本更新

### 更新步骤

1. **拉取最新代码**
   ```bash
   git pull
   ```

2. **重新构建容器**
   ```bash
   docker-compose up -d --build
   ```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请联系项目维护者。
