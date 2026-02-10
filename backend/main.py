import os
import bcrypt

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import uvicorn
import time
import ipaddress
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel

# 加载环境变量
load_dotenv()

# 认证配置
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24小时

# OAuth2 密码承载令牌
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Pydantic 模型
class User(BaseModel):
    id: int
    username: str
    role: str

class UserInDB(User):
    password_hash: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

# 用户数据存储（简化版，实际项目中应使用数据库）
def get_password_hash(password):
    # 截断密码，确保不超过 72 字节（bcrypt 限制）
    truncated_password = password[:72]
    # 使用 bcrypt 库直接哈希密码
    hashed = bcrypt.hashpw(truncated_password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

# 默认用户：admin / admin123
users_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "password_hash": get_password_hash("admin123"),
        "role": "admin"
    }
}

# 获取用户
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

# 验证密码
def verify_password(plain_password, hashed_password):
    # 截断密码，确保不超过 72 字节（bcrypt 限制）
    truncated_password = plain_password[:72]
    # 使用 bcrypt 库直接验证密码
    return bcrypt.checkpw(truncated_password.encode('utf-8'), hashed_password.encode('utf-8'))



# 创建访问令牌
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# 创建 FastAPI 应用
app = FastAPI(
    title="应用防火墙",
    description="Web Application Firewall with IPv6 monitoring and security protection",
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

# IP 黑名单
ip_blacklist = set()

# 请求频率限制（IP 地址 -> 请求时间列表）
request_rate_limit = {}

# 频率限制配置
RATE_LIMIT_WINDOW = 60  # 时间窗口（秒）
RATE_LIMIT_MAX_REQUESTS = 100  # 时间窗口内最大请求数

# WAF 规则
WAF_RULES = {
    "sql_injection": [
        r"' OR 1=1--",
        r"UNION SELECT",
        r"DROP TABLE",
        r"INSERT INTO",
        r"UPDATE.*SET",
        r"DELETE FROM",
        r"CREATE TABLE",
        r"ALTER TABLE",
        r"TRUNCATE TABLE",
        r"EXEC sp_",
        r"xp_",
        r"\bSELECT\b.*\bFROM\b",
        r"\bWHERE\b.*\bOR\b",
        r"\bAND\b.*\b1=1\b",
    ],
    "xss": [
        r"<script",
        r"javascript:",
        r"onerror=",
        r"onload=",
        r"onclick=",
        r"onmouseover=",
        r"<iframe",
        r"<object",
        r"<embed",
        r"<link",
        r"<meta",
        r"<img.*src=.*javascript:",
        r"</script>",
        r"eval\(",
        r"document\.write",
        r"window\.location",
    ],
    "command_injection": [
        r";\s*",
        r"\|\|\s*",
        r"\&\&\s*",
        r"`.*`",
        r"\|\s*",
        r"\<\s*",
        r"\>\s*",
        r"\|\s*grep\s*",
        r"\|\s*awk\s*",
        r"\|\s*sed\s*",
        r"\|\s*sort\s*",
        r"\|\s*uniq\s*",
        r"\|\s*wc\s*",
        r"\|\s*cat\s*",
        r"\|\s*tac\s*",
        r"\|\s*head\s*",
        r"\|\s*tail\s*",
    ],
    "csrf": [
        r"\bcsrf\b",
        r"\bcross-site\b",
        r"\brequest forgery\b",
    ],
    "file_upload": [
        r"\.php$",
        r"\.asp$",
        r"\.aspx$",
        r"\.jsp$",
        r"\.jspx$",
        r"\.exe$",
        r"\.sh$",
        r"\.bat$",
        r"\.cmd$",
        r"\.py$",
        r"\.pl$",
        r"\.perl$",
        r"\.cgi$",
        r"\.js$",
        r"\.vbs$",
        r"\.ps1$",
    ],
    "sensitive_info": [
        r"\bpassword\b",
        r"\bpasswd\b",
        r"\bsecret\b",
        r"\btoken\b",
        r"\bapi_key\b",
        r"\bapi_secret\b",
        r"\bauth\b",
        r"\bcookie\b",
        r"\bsession\b",
        r"\bcredit_card\b",
        r"\bssn\b",
        r"\bsocial_security\b",
        r"\bprivate\b",
        r"\bconfidential\b",
    ],
    "brute_force": [
        r"\blogin\b",
        r"\bauthenticate\b",
        r"\bsignin\b",
        r"\bpassword\b",
        r"\bpasswd\b",
    ],
    "abnormal_request": [
        r"\bnull\b",
        r"\bundefined\b",
        r"\binfinity\b",
        r"\bNaN\b",
        r"\bInfinity\b",
        r"\bundefined\b",
        r"\bnull\b",
    ],
}

# 检查请求是否包含攻击特征
async def check_waf_rules(request: Request) -> tuple[bool, str]:
    # 检查请求路径
    path = request.url.path
    
    # 检查请求参数
    query_params = dict(request.query_params)
    query_string = str(request.query_params)
    
    # 检查请求头
    headers = dict(request.headers)
    headers_string = str(request.headers)
    
    # 检查请求体
    body_string = ""
    try:
        # 仅检查文本类型的请求体
        if request.headers.get("content-type", "").startswith("application/"):
            body = await request.body()
            body_string = body.decode("utf-8", errors="ignore")
    except Exception:
        pass
    
    # 合并所有要检查的内容
    check_content = f"{path} {query_string} {headers_string} {body_string}"
    
    # 检查 SQL 注入
    for rule in WAF_RULES["sql_injection"]:
        if rule in check_content:
            return True, f"SQL 注入攻击检测"
    
    # 检查 XSS
    for rule in WAF_RULES["xss"]:
        if rule in check_content:
            return True, f"跨站脚本攻击检测"
    
    # 检查命令注入
    for rule in WAF_RULES["command_injection"]:
        if rule in check_content:
            return True, f"命令注入攻击检测"
    
    # 检查 CSRF
    for rule in WAF_RULES["csrf"]:
        if rule in check_content:
            return True, f"跨站请求伪造攻击检测"
    
    # 检查文件上传
    for rule in WAF_RULES["file_upload"]:
        if rule in check_content:
            return True, f"恶意文件上传检测"
    
    # 检查敏感信息泄露
    for rule in WAF_RULES["sensitive_info"]:
        if rule in check_content:
            return True, f"敏感信息泄露检测"
    
    # 检查暴力破解
    for rule in WAF_RULES["brute_force"]:
        if rule in check_content:
            return True, f"暴力破解攻击检测"
    
    # 检查异常请求
    for rule in WAF_RULES["abnormal_request"]:
        if rule in check_content:
            return True, f"异常请求检测"
    
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
    
    # 检查 IP 黑名单
    if client_ip in ip_blacklist:
        return JSONResponse(
            status_code=403,
            content={
                "detail": "Access denied: IP address is blacklisted",
                "attack_type": "IP 黑名单拦截"
            }
        )
    
    # 检查请求频率限制
    current_time = time.time()
    if client_ip in request_rate_limit:
        # 清理过期的请求时间
        request_rate_limit[client_ip] = [t for t in request_rate_limit[client_ip] if current_time - t < RATE_LIMIT_WINDOW]
        # 检查是否超过限制
        if len(request_rate_limit[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
            # 添加到黑名单
            ip_blacklist.add(client_ip)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests: Rate limit exceeded",
                    "attack_type": "请求频率限制"
                }
            )
    else:
        request_rate_limit[client_ip] = []
    
    # 记录请求时间
    request_rate_limit[client_ip].append(current_time)
    
    # 检查 WAF 规则
    is_attack, attack_message = await check_waf_rules(request)
    
    # 记录访问日志
    access_log = {
        "timestamp": time.time(),
        "ip": client_ip,
        "is_ipv6": is_ipv6,
        "method": request.method,
        "path": request.url.path,
        "query": dict(request.query_params),
        "user_agent": request.headers.get("user-agent", ""),
        "content_type": request.headers.get("content-type", ""),
        "accept": request.headers.get("accept", ""),
        "accept_language": request.headers.get("accept-language", ""),
        "accept_encoding": request.headers.get("accept-encoding", ""),
        "connection": request.headers.get("connection", ""),
        "is_attack": is_attack,
        "attack_message": attack_message if is_attack else None,
        "is_blacklisted": client_ip in ip_blacklist,
        "request_count": len(request_rate_limit.get(client_ip, [])),
        "status": "blocked" if is_attack else "allowed"
    }
    access_logs.append(access_log)
    
    # 限制日志大小
    if len(access_logs) > 1000:
        access_logs.pop(0)
    
    # 如果检测到攻击，记录并阻止
    if is_attack:
        # 添加到黑名单
        ip_blacklist.add(client_ip)
        
        # 记录攻击日志
        attack_logs.append(access_log)
        if len(attack_logs) > 500:
            attack_logs.pop(0)
        
        return JSONResponse(
            status_code=403,
            content={
                "detail": "访问被拒绝：检测到潜在攻击",
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
        requests_count = len([log for log in access_logs if start_time <= log["timestamp"] < end_time])
        attacks_count = len([log for log in attack_logs if start_time <= log["timestamp"] < end_time])
        
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

# 根路径
@app.get("/")
async def root():
    return {
        "message": "应用防火墙正在运行",
        "version": "1.0.0",
        "status": "active"
    }

# 认证相关 API

# 登录接口
@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(users_db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "id": user.id, "role": user.role},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 获取当前用户信息
@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    return User(id=current_user.id, username=current_user.username, role=current_user.role)

# 登出接口
@app.post("/api/auth/logout")
async def logout(current_user: UserInDB = Depends(get_current_user)):
    # JWT 是无状态的，登出主要在前端处理（清除 token）
    # 这里可以添加额外的逻辑，如将 token 加入黑名单等
    return {"message": "Successfully logged out"}

# API 接口：获取防火墙配置
@app.get("/api/firewall/config")
async def get_firewall_config(current_user: UserInDB = Depends(get_current_user)):
    return {
        "waf_rules": WAF_RULES,
        "rate_limit": {
            "window": RATE_LIMIT_WINDOW,
            "max_requests": RATE_LIMIT_MAX_REQUESTS
        },
        "blacklist": list(ip_blacklist)
    }

# API 接口：更新防火墙规则
@app.post("/api/firewall/rules")
async def update_firewall_rules(
    rules: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    global WAF_RULES
    WAF_RULES.update(rules)
    return {"message": "Firewall rules updated successfully", "rules": WAF_RULES}

# API 接口：添加 IP 到黑名单
@app.post("/api/firewall/blacklist/add")
async def add_ip_to_blacklist(
    ip: str,
    current_user: UserInDB = Depends(get_current_user)
):
    ip_blacklist.add(ip)
    return {"message": f"IP {ip} added to blacklist successfully", "blacklist": list(ip_blacklist)}

# API 接口：从黑名单移除 IP
@app.post("/api/firewall/blacklist/remove")
async def remove_ip_from_blacklist(
    ip: str,
    current_user: UserInDB = Depends(get_current_user)
):
    if ip in ip_blacklist:
        ip_blacklist.remove(ip)
        return {"message": f"IP {ip} removed from blacklist successfully", "blacklist": list(ip_blacklist)}
    else:
        return {"message": f"IP {ip} not found in blacklist", "blacklist": list(ip_blacklist)}

# API 接口：清空黑名单
@app.post("/api/firewall/blacklist/clear")
async def clear_blacklist(
    current_user: UserInDB = Depends(get_current_user)
):
    ip_blacklist.clear()
    return {"message": "Blacklist cleared successfully", "blacklist": list(ip_blacklist)}

# API 接口：更新速率限制配置
@app.post("/api/firewall/rate-limit")
async def update_rate_limit(
    config: dict,
    current_user: UserInDB = Depends(get_current_user)
):
    global RATE_LIMIT_WINDOW, RATE_LIMIT_MAX_REQUESTS
    if "window" in config:
        RATE_LIMIT_WINDOW = config["window"]
    if "max_requests" in config:
        RATE_LIMIT_MAX_REQUESTS = config["max_requests"]
    return {
        "message": "Rate limit configuration updated successfully",
        "config": {
            "window": RATE_LIMIT_WINDOW,
            "max_requests": RATE_LIMIT_MAX_REQUESTS
        }
    }

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8009))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
