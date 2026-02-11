import requests
import json

# 测试后端登录接口
def test_login():
    print("Testing backend login API...")
    
    # 测试数据
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    # 测试1: 直接访问后端服务
    print("\n1. Testing direct backend access...")
    try:
        response = requests.post('http://192.168.31.58:8009/api/auth/login', 
                               data=login_data, 
                               headers={'Content-Type': 'application/x-www-form-urlencoded'})
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            print("✓ Direct backend login successful!")
        else:
            print("✗ Direct backend login failed!")
    except Exception as e:
        print(f"✗ Direct backend login error: {e}")
    
    # 测试2: 通过前端代理访问
    print("\n2. Testing through frontend proxy...")
    try:
        response = requests.post('https://waf.threel.site/api/auth/login', 
                               data=login_data, 
                               headers={'Content-Type': 'application/x-www-form-urlencoded'})
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 200:
            print("✓ Frontend proxy login successful!")
        else:
            print("✗ Frontend proxy login failed!")
    except Exception as e:
        print(f"✗ Frontend proxy login error: {e}")
    
    # 测试3: 获取状态信息
    print("\n3. Testing status API...")
    try:
        # 先获取token
        response = requests.post('http://192.168.31.58:8009/api/auth/login', 
                               data=login_data, 
                               headers={'Content-Type': 'application/x-www-form-urlencoded'})
        if response.status_code == 200:
            token = response.json()['access_token']
            print(f"Got token: {token}")
            
            # 使用token访问状态接口
            status_response = requests.get('http://192.168.31.58:8009/api/status', 
                                         headers={'Authorization': f'Bearer {token}'})
            print(f"Status code: {status_response.status_code}")
            if status_response.status_code == 200:
                print("✓ Status API access successful!")
            else:
                print("✗ Status API access failed!")
        else:
            print("✗ Failed to get token for status API test!")
    except Exception as e:
        print(f"✗ Status API error: {e}")

if __name__ == "__main__":
    test_login()
