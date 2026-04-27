import time
import urllib.request
import hashlib
import hmac
import base64
import requests

API_KEY = "01000000002c1335ba1bab2ca6a23823499fb780a3bb7f6fc50d8c7773a777132d3caf19ed"
SECRET_KEY = "AQAAAAAsEzW6G6sspqI4I0mft4CjZcj0WoBOsvlz5n7uc361Ug=="
CUSTOMER_ID = "802748"

def generate_signature(timestamp, method, path, secret_key):
    message = f"{timestamp}.{method}.{path}".encode("utf-8")
    signing_key = secret_key.encode("utf-8")
    hash_value = hmac.new(signing_key, message, hashlib.sha256).digest()
    return base64.b64encode(hash_value).decode()

def test_keyword_tool():
    timestamp = str(int(time.time() * 1000))
    method = "GET"
    path = "/keywordstool"
    signature = generate_signature(timestamp, method, path, SECRET_KEY)
    
    headers = {
        "X-Timestamp": timestamp,
        "X-API-KEY": API_KEY,
        "X-Customer": CUSTOMER_ID,
        "X-Signature": signature
    }
    
    url = f"https://api.naver.com{path}?hintKeywords=LED전광판&showDetail=1"
    
    response = requests.get(url, headers=headers)
    print("Status:", response.status_code)
    print("Response:", response.text)

if __name__ == "__main__":
    test_keyword_tool()
