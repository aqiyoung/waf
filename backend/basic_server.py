import http.server
import socketserver
import json
import time
import urllib.parse
import os

PORT = int(os.environ.get('PORT', 8009))

# 简单的用户认证
users = {
    "admin": "admin123"
}

# 简单的 token 管理
tokens = {}
TOKEN_FILE = "tokens.json"

def load_tokens():
    """从文件加载tokens"""
    global tokens
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'r') as f:
                tokens = json.load(f)
        except Exception as e:
            print(f"Error loading tokens: {e}")
            tokens = {}

def save_tokens():
    """保存tokens到文件"""
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(tokens, f)
    except Exception as e:
        print(f"Error saving tokens: {e}")

def generate_token(username):
    token = f"token_{username}_{int(time.time())}"
    tokens[token] = username
    print(f"Generated token: {token}")
    print(f"Tokens dict before save: {tokens}")
    save_tokens()
    print(f"Tokens dict after save: {tokens}")
    return token

def verify_token(token):
    print(f"Verifying token: {token}")
    print(f"Tokens dict: {tokens}")
    print(f"Token in tokens: {token in tokens}")
    return token in tokens

# 加载tokens
load_tokens()

# 存储访问日志和攻击记录
access_logs = []
attack_logs = []

# IP 黑名单
ip_blacklist = set()

class SimpleHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # 解析路径
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # 获取客户端 IP
        client_ip = self.get_client_ip()
        
        # 记录访问日志
        access_log = {
            "timestamp": time.time(),
            "ip": client_ip,
            "method": "GET",
            "path": path,
            "query": urllib.parse.parse_qs(parsed_path.query),
            "user_agent": self.headers.get("User-Agent", ""),
            "is_attack": False,
            "status": "allowed"
        }
        access_logs.append(access_log)
        
        # 限制日志大小
        if len(access_logs) > 1000:
            access_logs.pop(0)
        
        # 处理 API 请求
        if path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "message": "应用防火墙正在运行",
                "version": "1.0.0",
                "status": "active"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif path == "/api/status":
            # 检查认证
            if not self.check_auth():
                return
            
            recent_logs = access_logs[-60:]
            recent_attacks = [log for log in recent_logs if log.get("is_attack", False)]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "total_accesses": len(access_logs),
                "total_attacks": len(attack_logs),
                "recent_accesses": len(recent_logs),
                "recent_attacks": len(recent_attacks),
                "ipv6_stats": {
                    "ipv6_count": 0,
                    "total_count": len(access_logs),
                    "ipv6_percentage": 0.0
                },
                "blacklist_count": len(ip_blacklist)
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif path == "/api/access-logs":
            # 检查认证
            if not self.check_auth():
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "logs": access_logs[-100:],
                "total": len(access_logs)
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif path == "/api/attack-logs":
            # 检查认证
            if not self.check_auth():
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "logs": attack_logs[-100:],
                "total": len(attack_logs)
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif path == "/api/ipv6-stats":
            # 检查认证
            if not self.check_auth():
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "ipv6_count": 0,
                "total_count": len(access_logs),
                "ipv6_percentage": 0.0
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif path == "/api/logs-analysis":
            # 检查认证
            if not self.check_auth():
                return
            
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
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "attack_types": attack_types,
                "ip_analysis": ip_analysis,
                "method_analysis": method_analysis,
                "time_trend": time_trend,
                "status_analysis": status_analysis,
                "total_logs": len(access_logs),
                "total_attacks": len(attack_logs)
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif path == "/api/auth/me":
            # 检查认证
            token = self.get_token()
            if not token or not verify_token(token):
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "detail": "Not authenticated"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            
            username = tokens[token]
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "id": 1,
                "username": username,
                "role": "admin"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif path == "/health":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy"}
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "detail": "Not found"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def do_POST(self):
        # 解析路径
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # 获取客户端 IP
        client_ip = self.get_client_ip()
        
        # 读取请求体
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # 记录访问日志
        access_log = {
            "timestamp": time.time(),
            "ip": client_ip,
            "method": "POST",
            "path": path,
            "query": urllib.parse.parse_qs(parsed_path.query),
            "user_agent": self.headers.get("User-Agent", ""),
            "is_attack": False,
            "status": "allowed"
        }
        access_logs.append(access_log)
        
        # 限制日志大小
        if len(access_logs) > 1000:
            access_logs.pop(0)
        
        # 处理登录请求
        if path == "/api/auth/login":
            # 解析表单数据
            form_data = urllib.parse.parse_qs(post_data)
            username = form_data.get('username', [''])[0]
            password = form_data.get('password', [''])[0]
            
            if username not in users or users[username] != password:
                self.send_response(401)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "detail": "Incorrect username or password"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
            
            # 生成 token
            token = generate_token(username)
            tokens[token] = username
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "access_token": token,
                "token_type": "bearer"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        elif path == "/api/auth/logout":
            # 检查认证
            token = self.get_token()
            if token and verify_token(token):
                del tokens[token]
                save_tokens()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "message": "Successfully logged out"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "detail": "Not found"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
    
    def check_auth(self):
        token = self.get_token()
        if not token or not verify_token(token):
            self.send_response(401)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "detail": "Not authenticated"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            return False
        return True
    
    def get_client_ip(self):
        """获取真实的客户端IP地址"""
        # 检查是否有反向代理的头
        x_forwarded_for = self.headers.get("X-Forwarded-For")
        x_real_ip = self.headers.get("X-Real-IP")
        
        if x_forwarded_for:
            # X-Forwarded-For 格式通常为: client_ip, proxy1_ip, proxy2_ip
            return x_forwarded_for.split(",")[0].strip()
        elif x_real_ip:
            return x_real_ip.strip()
        else:
            # 直接返回连接的IP地址
            return self.client_address[0]
    
    def get_token(self):
        auth_header = self.headers.get("Authorization")
        if auth_header:
            if auth_header.startswith("Bearer "):
                return auth_header[7:]
            return auth_header
        return None
    
    def end_headers(self):
        # 添加 CORS 头
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

# 启动服务器
# 使用空字符串作为地址，同时监听IPv4和IPv6地址
with socketserver.TCPServer(("", PORT), SimpleHTTPRequestHandler) as httpd:
    print(f"Server running at http://0.0.0.0:{PORT}")
    httpd.serve_forever()
