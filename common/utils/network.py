

import re
from urllib.parse import urlparse
from typing import Tuple, Optional

def extract_host_port(url: str) -> Tuple[str, Optional[int]]:
    """
    从URL中提取主机名(域名或IP地址)和端口号
    
    参数:
        url: 输入的URL字符串
        
    返回:
        (host, port): 主机名和端口号的元组，如果没有端口号则port为None
    """
    # 确保URL有协议头，如果没有则添加临时协议
    if not url.startswith(('http://', 'https://', 'ftp://', '//')):
        url = 'http://' + url
    
    # 使用urlparse解析URL
    parsed = urlparse(url)
    
    # 处理netloc部分可能包含的用户名密码
    netloc = parsed.netloc
    if '@' in netloc:
        netloc = netloc.split('@')[1]
    
    # 提取主机名和端口号
    if ':' in netloc:
        # 注意IPv6地址的特殊处理
        if '[' in netloc:  # IPv6格式 [IPv6]:port
            match = re.match(r'^\[(.+)\]:(\d+)$', netloc)
            if match:
                host = match.group(1)
                port = int(match.group(2))
            else:
                host = netloc
                port = None
        else:  # 普通域名或IPv4
            host, port_str = netloc.rsplit(':', 1)
            try:
                port = int(port_str)
            except ValueError:
                host = netloc
                port = None
    else:
        host = netloc
        port = None
    
    # 设置默认端口
    if port is None and parsed.scheme:
        default_ports = {'http': 80, 'https': 443, 'ftp': 21}
        port = default_ports.get(parsed.scheme, None)
    
    return host, port


if __name__ == "__main__":
    # 测试函数
    def test_extract():
        test_cases = [
            "example.com",
            "example.com:8080",
            "http://example.com",
            "https://example.com:8443",
            "user:pass@example.com:8080",
            "192.168.1.1",
            "192.168.1.1:8080",
            "[2001:db8::1]",
            "[2001:db8::1]:8080",
            "//example.com:8080"
        ]
        
        for url in test_cases:
            host, port = extract_host_port(url)
            print(f"URL: {url:30} -> Host: {host:20} Port: {port}")

    # 运行测试
    test_extract()