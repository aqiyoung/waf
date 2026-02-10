import os
import time
import ipaddress
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 创建 FastAPI 应用
app = FastAPI(
    title="应用防火墙",
    description="Web Application Firewall with IPv6 monitoring and security protection",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储访问日志和攻击记录
access_logs = []
attack_logs = []

# IP 黑名单
ip_blacklist = set()

# 请求频率限制（IP 地址 -> 请求时间列表）
request_rate_limit = {}

# 频率限制配置
RATE_LIMIT_WINDOW = 60  # 时间窗口（秒）
RATE_LIMIT_MAX_REQUESTS = 100  # 时间窗口内最大请求数

# 根路径
@app.get("/")
async def root():
    return {
        "message": "应用防火墙正在运行",
        "version": "1.0.0",
        "status": "active"
    }

# API 接口：获取访问日志
@app.get("/api/access-logs")
async def get_access_logs(limit: int = 100):
    return {
        "logs": access_logs[-limit:],
        "total": len(access_logs)
    }

# API 接口：获取攻击日志
@app.get("/api/attack-logs")
async def get_attack_logs(limit: int = 100):
    return {
        "logs": attack_logs[-limit:],
        "total": len(attack_logs)
    }

# API 接口：获取 IPv6 统计
@app.get("/api/ipv6-stats")
async def get_ipv6_stats():
    ipv6_count = sum(1 for log in access_logs if log.get("is_ipv6", False))
    total_count = len(access_logs)
    ipv6_percentage = (ipv6_count / total_count * 100) if total_count > 0 else 0
    
    return {
        "ipv6_count": ipv6_count,
        "total_count": total_count,
        "ipv6_percentage": round(ipv6_percentage, 2)
    }

# API 接口：获取实时状态
@app.get("/api/status")
async def get_status():
    recent_logs = access_logs[-60:]  # 最近 60 条记录
    recent_attacks = [log for log in recent_logs if log.get("is_attack", False)]
    
    return {
        "total_accesses": len(access_logs),
        "total_attacks": len(attack_logs),
        "recent_accesses": len(recent_logs),
        "recent_attacks": len(recent_attacks),
        "ipv6_stats": await get_ipv6_stats(),
        "blacklist_count": len(ip_blacklist)
    }

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8009))
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
