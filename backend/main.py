import os
# 禁用 passlib 的 wrap bug 检测，避免密码长度超过 72 字节的错误
os.environ['PASSLIB_NO_BYPASS_WRAP_BUG'] = '1'

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
from passlib.context import CryptContext
from pydantic import BaseModel

# 加载环境变量
load_dotenv()

# 认证配置
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24小时

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
    return pwd_context.hash(truncated_password)

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
    return pwd_context.verify(truncated_password, hashed_password)



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
