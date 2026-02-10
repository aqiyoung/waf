import http.server
import socketserver
import json
import time
import ipaddress
import threading
import urllib.parse
import re
import random
import requests

# IP 地理位置查询 API 配置
IP_GEOLOCATION_API_URL = "https://ipinfo.io/{ip}/json"
IP_GEOLOCATION_API_TIMEOUT = 5

PORT = 8010

# 存储访问日志和攻击记录
access_logs = []
attack_logs = []

# IP 白名单（允许绕过黑名单检查的 IP）
ip_whitelist = {"127.0.0.1", "localhost", "::1"}

# IP 黑名单
ip_blacklist = set()

# 请求频率限制（IP 地址 -> 请求时间列表）
request_rate_limit = {}

# 频率限制配置
RATE_LIMIT_WINDOW = 60  # 时间窗口（秒）
RATE_LIMIT_MAX_REQUESTS = 100  # 时间窗口内最大请求数

# 模拟用户数据
users = {
    "admin": {
        "username": "admin",
        "password": "admin123",  # 实际应用中应该使用哈希密码
        "role": "admin",
        "id": 1
    }
}

# 生成模拟的 JWT token
def generate_token(username):
    # 这里只是简单生成一个模拟的 token，实际应用中应该使用真实的 JWT 库
    return f"mock-token-{username}-{int(time.time())}"

# 查询 IP 地址的地理位置信息
def get_ip_geolocation(ip):
    """
    查询 IP 地址的地理位置信息
    :param ip: IP 地址
    :return: 地理位置信息字典，包含城市、地区、国家、经纬度等信息
    """
    try:
        # 本地 IP 地址不需要查询
        if ip in ip_whitelist:
            return {
                "city": "Localhost",
                "region": "Localhost",
                "country": "Local",
                "loc": "0,0",
                "org": "Local Network"
            }
        
        # 发送请求查询 IP 地理位置
        response = requests.get(
            IP_GEOLOCATION_API_URL.format(ip=ip),
            timeout=IP_GEOLOCATION_API_TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "city": "Unknown",
                "region": "Unknown",
                "country": "Unknown",
                "loc": "0,0",
                "org": "Unknown"
            }
    except Exception as e:
        print(f"Error querying IP geolocation: {e}")
        return {
            "city": "Unknown",
            "region": "Unknown",
            "country": "Unknown",
            "loc": "0,0",
            "org": "Unknown"
        }

# 增强的 WAF 规则
WAF_RULES = {
    "sql_injection": [
        r"'\s*OR\s*1=1",
        r"UNION\s+SELECT",
        r"DROP\s+TABLE",
        r"INSERT\s+INTO",
        r"UPDATE.*SET",
        r"DELETE\s+FROM",
        r"CREATE\s+TABLE",
        r"ALTER\s+TABLE",
        r"TRUNCATE\s+TABLE",
        r"EXEC\s+sp_",
        r"xp_",
        r"\bSELECT\b.*\bFROM\b",
        r"\bWHERE\b.*\bOR\b",
        r"\bAND\b.*\b1=1\b",
        r"\bOR\b\s+1=1",
        r"\bOR\b\s+'1'='1'",
        r"\bOR\b\s+\"1\"=\"1\"",
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
        r"alert\(",
        r"prompt\(",
        r"confirm\(",
        r"<svg.*onload=",
        r"<body.*onload=",
    ],
    "command_injection": [
        r";\s*",
        r"\|\|\s*",
        r"&&\s*",
        r"`.*`",
        r"\|\s*",
        r"<\s*",
        r">\s*",
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
        r"rm\s*-rf",
        r"cp\s*-r",
        r"mv\s*",
        r"mkdir\s*",
        r"rmdir\s*",
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

# 反机器人挑战存储
robot_challenges = {}

# 动态保护配置
dynamic_protection = {
    "enabled": True,
    "html_encryption": True,
    "js_encryption": True,
}

# 认证挑战配置
auth_challenge = {
    "enabled": False,
    "password": "",
}

# 防护应用存储
protected_apps = []

# 应用 ID 生成器
next_app_id = 1

# 检查请求是否包含攻击特征
def check_attack_patterns(request_path, request_data):
    """检查请求是否包含攻击特征"""
    # 合并所有要检查的内容
    check_content = f"{request_path} {request_data}"
    
    # 检查各种攻击模式
    for attack_type, patterns in WAF_RULES.items():
        for pattern in patterns:
            if re.search(pattern, check_content, re.IGNORECASE):
                return True, f"{attack_type.upper()} 攻击检测"
    
    return False, ""

# 检查速率限制
def check_rate_limit(client_ip):
    """检查 IP 是否超过速率限制"""
    current_time = time.time()
    
    if client_ip in request_rate_limit:
        # 清理过期的请求时间
        request_rate_limit[client_ip] = [t for t in request_rate_limit[client_ip] if current_time - t < RATE_LIMIT_WINDOW]
        # 检查是否超过限制
        if len(request_rate_limit[client_ip]) >= RATE_LIMIT_MAX_REQUESTS:
            return True
    else:
        request_rate_limit[client_ip] = []
    
    # 添加当前请求时间
    request_rate_limit[client_ip].append(current_time)
    return False

# 生成反机器人挑战
def generate_robot_challenge():
    """生成反机器人挑战"""
    # 生成简单的数学题
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operator = random.choice(["+", "-", "*"])
    
    if operator == "+":
        answer = num1 + num2
    elif operator == "-":
        answer = num1 - num2
    else:
        answer = num1 * num2
    
    challenge_id = f"challenge_{int(time.time())}_{random.randint(1000, 9999)}"
    robot_challenges[challenge_id] = {
        "num1": num1,
        "num2": num2,
        "operator": operator,
        "answer": answer,
        "created_at": time.time(),
    }
    
    return challenge_id, f"{num1} {operator} {num2} = ?"

# 验证反机器人挑战
def verify_robot_challenge(challenge_id, user_answer):
    """验证反机器人挑战"""
    if challenge_id not in robot_challenges:
        return False
    
    challenge = robot_challenges[challenge_id]
    # 检查挑战是否过期（5分钟）
    if time.time() - challenge["created_at"] > 300:
        del robot_challenges[challenge_id]
        return False
    
    try:
        user_answer = int(user_answer)
        if user_answer == challenge["answer"]:
            del robot_challenges[challenge_id]
            return True
    except ValueError:
        pass
    
    return False

class BasicHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 获取客户端 IP
        client_ip = self.client_address[0]
        
        # 检查是否为 IPv6 地址
        is_ipv6 = False
        try:
            ip_obj = ipaddress.ip_address(client_ip)
            is_ipv6 = isinstance(ip_obj, ipaddress.IPv6Address)
        except ValueError:
            pass
        
        # 检查 IP 白名单（本地 IP 跳过黑名单检查）
        if client_ip in ip_whitelist:
            pass  # 白名单 IP 跳过黑名单检查
        # 检查 IP 黑名单
        elif client_ip in ip_blacklist:
            self.send_response(403)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "detail": "Access denied: IP address is blacklisted",
                "attack_type": "IP 黑名单拦截"
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return
        
        # 检查速率限制（白名单 IP 跳过速率限制）
        if client_ip not in ip_whitelist and check_rate_limit(client_ip):
            # 添加到黑名单
            ip_blacklist.add(client_ip)
            self.send_response(429)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "detail": "Too many requests: Rate limit exceeded",
                "attack_type": "请求频率限制"
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return
        
        # 检查攻击特征
        is_attack, attack_message = check_attack_patterns(self.path, "")
        if is_attack:
            # 添加到黑名单
            ip_blacklist.add(client_ip)
            
            # 查询 IP 地理位置信息
            geo_info = get_ip_geolocation(client_ip)
            
            # 记录攻击日志
            attack_log = {
                "timestamp": time.time(),
                "ip": client_ip,
                "is_ipv6": is_ipv6,
                "method": "GET",
                "path": self.path,
                "is_attack": True,
                "attack_message": attack_message,
                "is_blacklisted": True,
                "status": "blocked",
                "geolocation": geo_info
            }
            attack_logs.append(attack_log)
            if len(attack_logs) > 500:
                attack_logs.pop(0)
            
            # 更新应用攻击统计
            for app in protected_apps:
                if app["isProtected"] and app["status"] == "running":
                    # 简单匹配路径，实际应用中可能需要更复杂的路由匹配
                    if app["backend"] in self.path:
                        app["attacksCount"] += 1
            
            self.send_response(403)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "detail": "访问被拒绝：检测到潜在攻击",
                "attack_type": attack_message
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return
        
        # 查询 IP 地理位置信息
        geo_info = get_ip_geolocation(client_ip)
        
        # 记录访问日志
        access_log = {
            "timestamp": time.time(),
            "ip": client_ip,
            "is_ipv6": is_ipv6,
            "method": "GET",
            "path": self.path,
            "is_attack": False,
            "attack_message": None,
            "is_blacklisted": client_ip in ip_blacklist,
            "status": "allowed",
            "geolocation": geo_info
        }
        access_logs.append(access_log)
        
        # 限制日志大小
        if len(access_logs) > 1000:
            access_logs.pop(0)
        
        # 更新应用请求统计
        for app in protected_apps:
            if app["isProtected"] and app["status"] == "running":
                # 简单匹配路径，实际应用中可能需要更复杂的路由匹配
                if app["backend"] in self.path:
                    app["requestsCount"] += 1
        
        # 提取路径（去除查询参数）
        path = self.path.split('?')[0]
        
        # 处理不同的路径
        if path == "/":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "message": "应用防火墙正在运行",
                "version": "1.0.0",
                "status": "active"
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            recent_logs = access_logs[-60:]
            recent_attacks = [log for log in recent_logs if log.get("is_attack", False)]
            
            ipv6_count = sum(1 for log in access_logs if log.get("is_ipv6", False))
            total_count = len(access_logs)
            ipv6_percentage = (ipv6_count / total_count * 100) if total_count > 0 else 0
            
            response = {
                "total_accesses": len(access_logs),
                "total_attacks": len(attack_logs),
                "recent_accesses": len(recent_logs),
                "recent_attacks": len(recent_attacks),
                "ipv6_stats": {
                    "ipv6_count": ipv6_count,
                    "total_count": total_count,
                    "ipv6_percentage": round(ipv6_percentage, 2)
                },
                "blacklist_count": len(ip_blacklist),
                "rate_limit": {
                    "window": RATE_LIMIT_WINDOW,
                    "max_requests": RATE_LIMIT_MAX_REQUESTS
                },
                "dynamic_protection": dynamic_protection,
                "auth_challenge": auth_challenge
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/access-logs":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "logs": access_logs[-100:],
                "total": len(access_logs)
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/attack-logs":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "logs": attack_logs[-100:],
                "total": len(attack_logs)
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/ipv6-stats":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            ipv6_count = sum(1 for log in access_logs if log.get("is_ipv6", False))
            total_count = len(access_logs)
            ipv6_percentage = (ipv6_count / total_count * 100) if total_count > 0 else 0
            
            response = {
                "ipv6_count": ipv6_count,
                "total_count": total_count,
                "ipv6_percentage": round(ipv6_percentage, 2)
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/auth/me":
            # 获取当前用户信息
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "id": 1,
                "username": "admin",
                "role": "admin"
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/protection-rules":
            # 获取防护规则
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "rules": WAF_RULES,
                "status": "active"
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/rate-limiting":
            # 获取速率限制配置
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "window": RATE_LIMIT_WINDOW,
                "max_requests": RATE_LIMIT_MAX_REQUESTS,
                "current_usage": {}
            }
            # 添加当前使用情况
            for ip, times in request_rate_limit.items():
                response["current_usage"][ip] = len(times)
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/robot-challenge":
            # 生成反机器人挑战
            challenge_id, challenge_text = generate_robot_challenge()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "challenge_id": challenge_id,
                "challenge_text": challenge_text
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/protected-apps":
            # 获取防护应用列表
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "apps": protected_apps,
                "total": len(protected_apps)
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path.startswith("/api/protected-apps/"):
            # 获取单个防护应用详情
            app_id = path.split("/")[-1]
            try:
                app_id = int(app_id)
                app = next((a for a in protected_apps if a["id"] == app_id), None)
                if app:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    response = app
                    self.wfile.write(json.dumps(response).encode("utf-8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    response = {"detail": "应用不存在"}
                    self.wfile.write(json.dumps(response).encode("utf-8"))
            except ValueError:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response = {"detail": "无效的应用 ID"}
                self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"status": "healthy"}
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        else:
            self.send_response(404)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"detail": "Not Found"}
            self.wfile.write(json.dumps(response).encode("utf-8"))
    
    def do_POST(self):
        # 获取客户端 IP
        client_ip = self.client_address[0]
        
        # 检查是否为 IPv6 地址
        is_ipv6 = False
        try:
            ip_obj = ipaddress.ip_address(client_ip)
            is_ipv6 = isinstance(ip_obj, ipaddress.IPv6Address)
        except ValueError:
            pass
        
        # 检查 IP 黑名单
        if client_ip in ip_blacklist:
            self.send_response(403)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "detail": "Access denied: IP address is blacklisted",
                "attack_type": "IP 黑名单拦截"
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return
        
        # 检查速率限制
        if check_rate_limit(client_ip):
            # 添加到黑名单
            ip_blacklist.add(client_ip)
            self.send_response(429)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "detail": "Too many requests: Rate limit exceeded",
                "attack_type": "请求频率限制"
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return
        
        # 处理 POST 请求
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # 解析 POST 数据
        post_params = {}
        if self.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            post_params = urllib.parse.parse_qs(post_data.decode('utf-8'))
            # 将列表值转换为单个值
            for key, value in post_params.items():
                if isinstance(value, list) and len(value) == 1:
                    post_params[key] = value[0]
        elif self.headers.get('Content-Type') == 'application/json':
            try:
                post_params = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                pass
        
        # 检查攻击特征（白名单 IP 跳过攻击特征检查）
        is_attack, attack_message = check_attack_patterns(self.path, str(post_params))
        if client_ip not in ip_whitelist and is_attack:
            # 添加到黑名单
            ip_blacklist.add(client_ip)
            
            # 查询 IP 地理位置信息
            geo_info = get_ip_geolocation(client_ip)
            
            # 记录攻击日志
            attack_log = {
                "timestamp": time.time(),
                "ip": client_ip,
                "is_ipv6": is_ipv6,
                "method": "POST",
                "path": self.path,
                "is_attack": True,
                "attack_message": attack_message,
                "is_blacklisted": True,
                "status": "blocked",
                "geolocation": geo_info
            }
            attack_logs.append(attack_log)
            if len(attack_logs) > 500:
                attack_logs.pop(0)
            
            # 更新应用攻击统计
            for app in protected_apps:
                if app["isProtected"] and app["status"] == "running":
                    # 简单匹配路径，实际应用中可能需要更复杂的路由匹配
                    if app["backend"] in self.path:
                        app["attacksCount"] += 1
            
            self.send_response(403)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "detail": "访问被拒绝：检测到潜在攻击",
                "attack_type": attack_message
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
            return
        
        # 查询 IP 地理位置信息
        geo_info = get_ip_geolocation(client_ip)
        
        # 记录访问日志
        access_log = {
            "timestamp": time.time(),
            "ip": client_ip,
            "is_ipv6": is_ipv6,
            "method": "POST",
            "path": self.path,
            "is_attack": False,
            "attack_message": None,
            "is_blacklisted": client_ip in ip_blacklist,
            "status": "allowed",
            "geolocation": geo_info
        }
        access_logs.append(access_log)
        
        # 限制日志大小
        if len(access_logs) > 1000:
            access_logs.pop(0)
        
        # 更新应用请求统计
        for app in protected_apps:
            if app["isProtected"] and app["status"] == "running":
                # 简单匹配路径，实际应用中可能需要更复杂的路由匹配
                if app["backend"] in self.path:
                    app["requestsCount"] += 1
        
        # 提取路径（去除查询参数）
        path = self.path.split('?')[0]
        
        # 处理登录请求
        if path == "/api/auth/login":
            username = post_params.get('username')
            password = post_params.get('password')
            
            # 验证用户名和密码
            if username in users and users[username]['password'] == password:
                # 生成 token
                token = generate_token(username)
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response = {
                    "access_token": token,
                    "token_type": "bearer"
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))
            else:
                self.send_response(401)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response = {
                    "detail": "Incorrect username or password"
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/auth/logout":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {"message": "Successfully logged out"}
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/protection-rules":
            # 更新防护规则
            if "rules" in post_params:
                global WAF_RULES
                WAF_RULES.update(post_params["rules"])
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response = {
                    "message": "防护规则更新成功",
                    "rules": WAF_RULES
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))
            else:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response = {
                    "detail": "缺少规则数据"
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/rate-limiting":
            # 更新速率限制配置
            if "window" in post_params and "max_requests" in post_params:
                global RATE_LIMIT_WINDOW, RATE_LIMIT_MAX_REQUESTS
                RATE_LIMIT_WINDOW = post_params["window"]
                RATE_LIMIT_MAX_REQUESTS = post_params["max_requests"]
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response = {
                    "message": "速率限制配置更新成功",
                    "window": RATE_LIMIT_WINDOW,
                    "max_requests": RATE_LIMIT_MAX_REQUESTS
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))
            else:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response = {
                    "detail": "缺少配置数据"
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/robot-challenge/verify":
            # 验证反机器人挑战
            challenge_id = post_params.get('challenge_id')
            user_answer = post_params.get('answer')
            
            if challenge_id and user_answer:
                if verify_robot_challenge(challenge_id, user_answer):
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    response = {
                        "success": True,
                        "message": "验证成功"
                    }
                    self.wfile.write(json.dumps(response).encode("utf-8"))
                else:
                    self.send_response(401)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    response = {
                        "success": False,
                        "message": "验证失败"
                    }
                    self.wfile.write(json.dumps(response).encode("utf-8"))
            else:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response = {
                    "detail": "缺少挑战数据"
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/blacklist":
            # 管理黑名单
            if "action" in post_params:
                action = post_params["action"]
                if action == "add" and "ip" in post_params:
                    ip = post_params["ip"]
                    ip_blacklist.add(ip)
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    response = {
                        "message": f"IP {ip} 添加到黑名单成功",
                        "blacklist": list(ip_blacklist)
                    }
                    self.wfile.write(json.dumps(response).encode("utf-8"))
                elif action == "remove" and "ip" in post_params:
                    ip = post_params["ip"]
                    if ip in ip_blacklist:
                        ip_blacklist.remove(ip)
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.end_headers()
                        response = {
                            "message": f"IP {ip} 从黑名单移除成功",
                            "blacklist": list(ip_blacklist)
                        }
                        self.wfile.write(json.dumps(response).encode("utf-8"))
                    else:
                        self.send_response(404)
                        self.send_header("Content-type", "application/json")
                        self.send_header("Access-Control-Allow-Origin", "*")
                        self.end_headers()
                        response = {
                            "detail": f"IP {ip} 不在黑名单中"
                        }
                        self.wfile.write(json.dumps(response).encode("utf-8"))
                elif action == "clear":
                    ip_blacklist.clear()
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    response = {
                        "message": "黑名单清空成功",
                        "blacklist": list(ip_blacklist)
                    }
                    self.wfile.write(json.dumps(response).encode("utf-8"))
                else:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    response = {
                        "detail": "无效的操作"
                    }
                    self.wfile.write(json.dumps(response).encode("utf-8"))
            else:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response = {
                    "detail": "缺少操作参数"
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path == "/api/protected-apps":
            # 添加防护应用
            global next_app_id
            
            required_fields = ["name", "backend", "protocol", "port"]
            for field in required_fields:
                if field not in post_params:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    response = {
                        "detail": f"缺少必填字段: {field}"
                    }
                    self.wfile.write(json.dumps(response).encode("utf-8"))
                    return
            
            # 创建新应用
            new_app = {
                "id": next_app_id,
                "name": post_params["name"],
                "backend": post_params["backend"],
                "protocol": post_params["protocol"],
                "port": post_params["port"],
                "status": "running",
                "statusText": "运行中",
                "isProtected": True,
                "ccProtection": post_params.get("ccProtection", True),
                "botProtection": post_params.get("botProtection", True),
                "authProtection": post_params.get("authProtection", False),
                "dynamicProtection": post_params.get("dynamicProtection", False),
                "ccRateLimit": post_params.get("ccRateLimit", 100),
                "ccPenaltyTime": post_params.get("ccPenaltyTime", 5),
                "requestsCount": 0,
                "attacksCount": 0,
                "created_at": time.time()
            }
            
            protected_apps.append(new_app)
            next_app_id += 1
            
            self.send_response(201)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            response = {
                "message": "应用添加成功",
                "app": new_app
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        elif path.startswith("/api/protected-apps/"):
            # 编辑或删除防护应用
            app_id = path.split("/")[-1]
            try:
                app_id = int(app_id)
                app = next((a for a in protected_apps if a["id"] == app_id), None)
                if not app:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    response = {"detail": "应用不存在"}
                    self.wfile.write(json.dumps(response).encode("utf-8"))
                    return
                
                # 处理删除操作
                if post_params.get("action") == "delete":
                    protected_apps.remove(app)
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    response = {
                        "message": "应用删除成功"
                    }
                    self.wfile.write(json.dumps(response).encode("utf-8"))
                    return
                
                # 处理状态切换操作
                if post_params.get("action") == "toggle-protection":
                    app["isProtected"] = not app["isProtected"]
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    response = {
                        "message": f"应用防护已{'' if app['isProtected'] else '取消'}开启",
                        "app": app
                    }
                    self.wfile.write(json.dumps(response).encode("utf-8"))
                    return
                
                # 处理应用状态切换（运行/停止）
                if post_params.get("action") == "toggle-status":
                    if app["status"] == "running":
                        app["status"] = "stopped"
                        app["statusText"] = "已停止"
                        app["isProtected"] = False
                    else:
                        app["status"] = "running"
                        app["statusText"] = "运行中"
                        app["isProtected"] = True
                    
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    response = {
                        "message": f"应用状态已切换为{app['statusText']}",
                        "app": app
                    }
                    self.wfile.write(json.dumps(response).encode("utf-8"))
                    return
                
                # 处理编辑操作
                editable_fields = ["name", "backend", "protocol", "port", "ccProtection", "botProtection", "authProtection", "dynamicProtection", "ccRateLimit", "ccPenaltyTime"]
                for field in editable_fields:
                    if field in post_params:
                        app[field] = post_params[field]
                
                # 处理防护配置更新
                if "protection_config" in post_params:
                    app["protection_config"] = post_params["protection_config"]
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response = {
                    "message": "应用更新成功",
                    "app": app
                }
                self.wfile.write(json.dumps(response).encode("utf-8"))
                return
                
            except ValueError:
                self.send_response(400)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                response = {"detail": "无效的应用 ID"}
                self.wfile.write(json.dumps(response).encode("utf-8"))
        
        else:
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            
            response = {"message": "POST request received"}
            self.wfile.write(json.dumps(response).encode("utf-8"))
    
    def do_OPTIONS(self):
        # 处理 CORS 预检请求
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

def run_server():
    with socketserver.TCPServer(("", PORT), BasicHTTPRequestHandler) as httpd:
        print(f"服务器运行在 http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
