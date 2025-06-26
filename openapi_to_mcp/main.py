"""
主程序入口

OpenAPI到MCP转换工具的主程序
接受用户输入的OpenAPI文档源并启动MCP服务
"""

import sys
from loguru import logger
from converter import OpenAPIMCPConverter


def main():
    """
    主函数
    
    接受命令行参数或交互式输入，启动MCP服务
    """
    # 配置日志
    logger.add("openapi_to_mcp.log", rotation="1 day", retention="7 days")
    
    print("=== OpenAPI到MCP转换工具 ===")
    print()
    
    # 获取OpenAPI文档源
    source = get_openapi_source()
    if not source:
        print("❌ 未提供有效的OpenAPI文档源")
        return
    
    # 获取可选配置
    config = get_optional_config()
    
    try:
        # 创建转换器
        converter = OpenAPIMCPConverter(
            base_url=config.get('base_url'),
            timeout=config.get('timeout', 30)
        )
        
        # 启动服务器
        print(f"\n🚀 正在启动MCP服务器...")
        converter.start_server(
            source=source,
            transport=config.get('transport', 'streamable-http'),
            host=config.get('host', '127.0.0.1'),
            port=config.get('port', 8000),
            validate=config.get('validate', True)
        )
        
    except Exception as e:
        logger.error(f"启动失败: {e}")
        print(f"❌ 启动失败: {e}")
        sys.exit(1)


def get_openapi_source():
    """
    获取OpenAPI文档源
    
    优先从命令行参数获取，否则交互式输入
    
    Returns:
        OpenAPI文档源路径或URL
    """
    # 检查命令行参数
    if len(sys.argv) > 1:
        source = sys.argv[1]
        print(f"📄 使用命令行参数: {source}")
        return source
    
    # 交互式输入
    print("请输入OpenAPI文档源：")
    print("  - 网页链接: https://api.example.com/openapi.json")
    print("  - 本地文件: ./openapi.json")
    print()
    
    while True:
        source = input("OpenAPI文档源: ").strip()
        if source:
            return source
        print("⚠️  请输入有效的文档源")


def get_optional_config():
    """
    获取可选配置
    
    Returns:
        配置字典
    """
    config = {}
    
    print("\n=== 可选配置（直接回车使用默认值） ===")
    
    # API服务器基础URL（可选，如果文档中没有servers字段会在转换时提示）
    base_url = input("API服务器基础URL (默认: 从文档自动提取，如文档无servers字段会提示输入): ").strip()
    if base_url:
        config['base_url'] = base_url
    
    # 服务器端口
    port_input = input("MCP服务器端口 (默认: 8000): ").strip()
    if port_input:
        try:
            config['port'] = int(port_input)
        except ValueError:
            print("⚠️  端口必须是数字，使用默认值 8000")
    
    # 服务器主机
    host = input("MCP服务器主机 (默认: 127.0.0.1): ").strip()
    if host:
        config['host'] = host
    
    # 是否跳过验证
    skip_validate = input("跳过文档验证? (y/N): ").strip().lower()
    if skip_validate in ['y', 'yes']:
        config['validate'] = False
    
    return config

def get_auth_config():
    """
    获取认证配置
    
    Returns:
        认证配置字典
    """
    print("\n=== 认证配置（可选） ===")
    print("如果API需要认证，请选择认证方式：")
    print("1. 无认证")
    print("2. Bearer Token")
    print("3. API Key")
    print("4. Basic Auth")
    print("5. 自定义Headers")
    print("6. Cookies")
    
    choice = input("选择认证方式 (1-6, 默认: 1): ").strip()
    
    if choice == '2':
        return get_bearer_token_config()
    elif choice == '3':
        return get_api_key_config()
    elif choice == '4':
        return get_basic_auth_config()
    elif choice == '5':
        return get_custom_headers_config()
    elif choice == '6':
        return get_cookies_config()
    else:
        return None

def get_bearer_token_config():
    """
    获取Bearer Token配置
    """
    token = input("请输入Bearer Token: ").strip()
    if token:
        return {'bearer_token': token}
    return None

def get_api_key_config():
    """
    获取API Key配置
    """
    key_name = input("API Key名称 (如: X-API-Key): ").strip()
    key_value = input("API Key值: ").strip()
    key_location = input("API Key位置 (header/query, 默认: header): ").strip().lower()
    
    if not key_location:
        key_location = 'header'
    
    if key_name and key_value:
        return {
            'api_key': {
                'name': key_name,
                'value': key_value,
                'in': key_location
            }
        }
    return None

def get_basic_auth_config():
    """
    获取Basic Auth配置
    """
    username = input("用户名: ").strip()
    password = input("密码: ").strip()
    
    if username and password:
        return {
            'basic_auth': {
                'username': username,
                'password': password
            }
        }
    return None

def get_custom_headers_config():
    """
    获取自定义Headers配置
    """
    headers = {}
    print("输入自定义请求头（格式: 名称=值，空行结束）:")
    
    while True:
        header_input = input("Header: ").strip()
        if not header_input:
            break
        
        if '=' in header_input:
            name, value = header_input.split('=', 1)
            headers[name.strip()] = value.strip()
        else:
            print("⚠️  格式错误，请使用: 名称=值")
    
    if headers:
        return {'headers': headers}
    return None

def get_cookies_config():
    """
    获取Cookies配置
    """
    cookies = {}
    print("输入Cookies（格式: 名称=值，空行结束）:")
    
    while True:
        cookie_input = input("Cookie: ").strip()
        if not cookie_input:
            break
        
        if '=' in cookie_input:
            name, value = cookie_input.split('=', 1)
            cookies[name.strip()] = value.strip()
        else:
            print("⚠️  格式错误，请使用: 名称=值")
    
    if cookies:
        return {'cookies': cookies}
    return None


if __name__ == "__main__":
    main()