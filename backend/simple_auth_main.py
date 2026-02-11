import os
import time
import ipaddress
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

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

# 简单的用户认证
users = {
    "admin": "admin123"
}

# 简单的 token 管理
tokens = {}

def generate_token(username):
    return f"token_{username}_{int(time.time())}"

# 根路径
@app.get("/")
async def root():
    return {
        "message": "应用防火墙正在运行",
        "version": "1.0.0",
        "status": "active"
    }

# 登录接口
@app.post("/api/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if username not in users or users[username] != password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = generate_token(username)
    tokens[token] = username
    return {"access_token": token, "token_type": "bearer"}

# 获取当前用户信息
@app.get("/api/auth/me")
async def get_current_user_info(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header.split()[1] if len(auth_header.split()) > 1 else auth_header
    if token not in tokens:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = tokens[token]
    return {"id": 1, "username": username, "role": "admin"}

# 登出接口
@app.post("/api/auth/logout")
async def logout(request: Request):
    auth_header = request.headers.get("Authorization")
    if auth_header:
        token = auth_header.split()[1] if len(auth_header.split()) > 1 else auth_header
        if token in tokens:
            del tokens[token]
    return {"message": "Successfully logged out"}

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

# API 接口：获取日志分析
@app.get("/api/logs-analysis")
async def get_logs_analysis():
    # 攻击类型分布
    attack_types = {}
    for log in attack_logs:
        attack_msg = log.get("attack_message", "Unknown")
        if attack_msg:
            attack_types[attack_msg] = attack_types.get(attack_msg, 0) + 1
    
    # IP 地址分析
    ip_analysis = {
        "total_ips": len(set(log["ip"] for log in access_logs)),
        "attack_ips": len(set(log["ip"] for log in attack_logs)),
        "blacklisted_ips": len(ip_blacklist)
    }
    
    # 请求方法分析
    method_analysis = {}
    for log in access_logs:
        method = log.get("method", "Unknown")
        method_analysis[method] = method_analysis.get(method, 0) + 1
    
    # 时间趋势分析（最近 60 分钟）
    time_trend = []
    current_time = time.time()
    for i in range(60, 0, -1):
        start_time = current_time - (i * 60)
        end_time = current_time - ((i - 1) * 60)
        
        # 统计该时间段内的请求数和攻击数
        requests_count = len([log for log in access_logs if start_time <= log.get("timestamp", 0) < end_time])
        attacks_count = len([log for log in attack_logs if start_time <= log.get("timestamp", 0) < end_time])
        
        time_trend.append({
            "timestamp": end_time,
            "requests": requests_count,
            "attacks": attacks_count
        })
    
    # 状态分布
    status_analysis = {
        "allowed": len([log for log in access_logs if log.get("status") == "allowed"]),
        "blocked": len([log for log in access_logs if log.get("status") == "blocked"])
    }
    
    return {
        "attack_types": attack_types,
        "ip_analysis": ip_analysis,
        "method_analysis": method_analysis,
        "time_trend": time_trend,
        "status_analysis": status_analysis,
        "total_logs": len(access_logs),
        "total_attacks": len(attack_logs)
    }

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8009))
    uvicorn.run(
        "simple_auth_main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
