from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time
import ipaddress
import json
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 创建 FastAPI 应用
app = FastAPI(
    title="WAF for Feiniu NAS",
    description="Web Application Firewall with IPv6 monitoring for Feiniu NAS",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储访问日志和攻击记录
access_logs = []
attack_logs = []

# WAF 规则
WAF_RULES = {
    "sql_injection": [
        r"' OR 1=1--",
        r"UNION SELECT",
        r"DROP TABLE",
        r"INSERT INTO",
        r"UPDATE.*SET",
    ],
    "xss": [
        r"<script",
        r"javascript:",
        r"onerror=",
        r"onload=",
    ],
    "command_injection": [
        r";\s*",
        r"\|\|\s*",
        r"\&\&\s*",
        r"`.*`",
    ],
}

# 检查请求是否包含攻击特征
def check_waf_rules(request: Request) -> tuple[bool, str]:
    # 检查请求路径
    path = request.url.path
    for rule in WAF_RULES["sql_injection"]:
        if rule in path:
            return True, f"SQL injection detected in path: {path}"
    
    for rule in WAF_RULES["xss"]:
        if rule in path:
            return True, f"XSS detected in path: {path}"
    
    for rule in WAF_RULES["command_injection"]:
        if rule in path:
            return True, f"Command injection detected in path: {path}"
    
    return False, ""

# 中间件：请求拦截和监测
@app.middleware("http")
async def waf_middleware(request: Request, call_next):
    # 获取客户端 IP
    client_ip = request.client.host
    
    # 检查是否为 IPv6 地址
    is_ipv6 = False
    try:
        ip_obj = ipaddress.ip_address(client_ip)
        is_ipv6 = isinstance(ip_obj, ipaddress.IPv6Address)
    except ValueError:
        pass
    
    # 检查 WAF 规则
    is_attack, attack_message = check_waf_rules(request)
    
    # 记录访问日志
    access_log = {
        "timestamp": time.time(),
        "ip": client_ip,
        "is_ipv6": is_ipv6,
        "method": request.method,
        "path": request.url.path,
        "query": dict(request.query_params),
        "user_agent": request.headers.get("user-agent", ""),
        "is_attack": is_attack,
        "attack_message": attack_message if is_attack else None
    }
    access_logs.append(access_log)
    
    # 限制日志大小
    if len(access_logs) > 1000:
        access_logs.pop(0)
    
    # 如果检测到攻击，记录并阻止
    if is_attack:
        attack_logs.append(access_log)
        if len(attack_logs) > 500:
            attack_logs.pop(0)
        
        return JSONResponse(
            status_code=403,
            content={
                "detail": "Access denied: Potential attack detected",
                "attack_type": attack_message
            }
        )
    
    # 继续处理请求
    response = await call_next(request)
    return response

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
    ipv6_count = sum(1 for log in access_logs if log["is_ipv6"])
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
    recent_attacks = [log for log in recent_logs if log["is_attack"]]
    
    return {
        "total_accesses": len(access_logs),
        "total_attacks": len(attack_logs),
        "recent_accesses": len(recent_logs),
        "recent_attacks": len(recent_attacks),
        "ipv6_stats": await get_ipv6_stats()
    }

# 根路径
@app.get("/")
async def root():
    return {
        "message": "WAF for Feiniu NAS is running",
        "version": "1.0.0",
        "status": "active"
    }

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
