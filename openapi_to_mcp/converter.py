"""
OpenAPI到MCP转换器

将OpenAPI文档转换为FastMCP服务
"""

import httpx
from typing import Dict, Any, Optional
from fastmcp import FastMCP
from loguru import logger

from loader import OpenAPILoader


class OpenAPIMCPConverter:
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        初始化转换器
        
        Args:
            base_url: API服务器基础URL
            timeout: HTTP请求超时时间
        """
        self.base_url = base_url
        self.timeout = timeout
        self.loader = OpenAPILoader(timeout=timeout)
        self.logger = logger
        self.auth_values = {}  # 存储用户提供的认证值
    
    def convert(self, source: str, validate: bool = True) -> FastMCP:
        """
        转换OpenAPI文档为MCP服务
        
        Args:
            source: OpenAPI文档源（URL或文件路径）
            validate: 是否验证文档
            
        Returns:
            FastMCP实例
        """
        try:
            self.logger.info(f"开始转换OpenAPI文档: {source}")
            
            # 加载OpenAPI文档
            openapi_doc = self.loader.load(source)
            
            # 验证文档
            if validate:
                self._basic_validate(openapi_doc)
            
            # 检查并获取服务器URL（支持用户手动输入）
            server_url = self._check_and_get_server_url(openapi_doc)
            
            # 分析并获取认证配置
            auth_config = self._analyze_and_get_auth_config(openapi_doc)
            
            # 创建HTTP客户端配置
            client_config = self._create_http_client_config(auth_config)
            
            # 创建HTTP客户端
            client = httpx.AsyncClient(
                base_url=server_url,
                **client_config
            )
            
            # 创建FastMCP实例
            mcp = FastMCP.from_openapi(
                openapi_spec=openapi_doc,
                client=client,
                name=openapi_doc.get('info', {}).get('title', 'OpenAPI MCP Server')
            )
            
            # 统计API数量
            api_count = self._count_apis(openapi_doc)
            
            print(f"\n✅ 成功创建MCP服务: {openapi_doc.get('info', {}).get('title', 'Unknown')}")
            print(f"📊 包含 {api_count} 个API工具")
            print(f"🌐 API服务器URL: {server_url}")
            if auth_config:
                configured_schemes = [scheme for scheme in auth_config.keys() if auth_config[scheme]]
                print(f"🔐 已配置认证方案: {configured_schemes}")
            
            return mcp
            
        except Exception as e:
            self.logger.error(f"转换OpenAPI文档失败: {e}")
            raise
    
    def _analyze_and_get_auth_config(self, openapi_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析OpenAPI文档中的安全配置并获取认证信息
        
        Args:
            openapi_doc: OpenAPI文档
            
        Returns:
            认证配置字典
        """
        # 提取文档中的安全方案
        security_schemes = self._extract_security_schemes(openapi_doc)
        global_security = openapi_doc.get('security', [])
        
        if not security_schemes and not global_security:
            print("ℹ️  文档中未发现安全配置，API可能不需要认证")
            return {}
        
        print("\n🔍 发现以下安全配置：")
        self._display_security_schemes(security_schemes)
        
        # 根据安全方案获取认证值
        auth_config = self._get_auth_values_for_schemes(security_schemes, global_security)
        
        return auth_config
    
    def _extract_security_schemes(self, openapi_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        提取OpenAPI文档中的安全方案定义
        
        Args:
            openapi_doc: OpenAPI文档
            
        Returns:
            安全方案字典
        """
        components = openapi_doc.get('components', {})
        return components.get('securitySchemes', {})
    
    def _display_security_schemes(self, security_schemes: Dict[str, Any]):
        """
        显示发现的安全方案
        
        Args:
            security_schemes: 安全方案字典
        """
        for scheme_name, scheme_config in security_schemes.items():
            scheme_type = scheme_config.get('type', 'unknown')
            description = scheme_config.get('description', '')
            
            print(f"  • {scheme_name}: {scheme_type}")
            if description:
                print(f"    描述: {description}")
            
            # 显示具体配置
            if scheme_type == 'apiKey':
                key_name = scheme_config.get('name', '')
                key_location = scheme_config.get('in', '')
                print(f"    API Key名称: {key_name}, 位置: {key_location}")
            elif scheme_type == 'http':
                http_scheme = scheme_config.get('scheme', '')
                print(f"    HTTP方案: {http_scheme}")
            elif scheme_type == 'oauth2':
                flows = scheme_config.get('flows', {})
                print(f"    OAuth2流程: {list(flows.keys())}")
    
    def _get_auth_values_for_schemes(self, security_schemes: Dict[str, Any], 
                                   global_security: list) -> Dict[str, Any]:
        """
        根据安全方案获取认证值
        
        Args:
            security_schemes: 安全方案定义
            global_security: 全局安全要求
            
        Returns:
            认证配置字典
        """
        auth_config = {}
        
        # 确定需要的安全方案
        required_schemes = set()
        for security_req in global_security:
            required_schemes.update(security_req.keys())
        
        if not required_schemes:
            required_schemes = set(security_schemes.keys())
        
        print("\n🔑 请提供以下认证信息：")
        
        for scheme_name in required_schemes:
            if scheme_name in security_schemes:
                scheme_config = security_schemes[scheme_name]
                auth_value = self._get_auth_value_for_scheme(scheme_name, scheme_config)
                if auth_value:
                    auth_config[scheme_name] = auth_value
        
        return auth_config
    
    def _get_auth_value_for_scheme(self, scheme_name: str, 
                                 scheme_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        获取单个安全方案的认证值
        
        Args:
            scheme_name: 方案名称
            scheme_config: 方案配置
            
        Returns:
            认证值字典
        """
        scheme_type = scheme_config.get('type', '')
        
        print(f"\n--- {scheme_name} ({scheme_type}) ---")
        
        if scheme_type == 'apiKey':
            return self._get_api_key_value(scheme_config)
        elif scheme_type == 'http':
            return self._get_http_auth_value(scheme_config)
        elif scheme_type == 'oauth2':
            return self._get_oauth2_value(scheme_config)
        else:
            print(f"⚠️  暂不支持的认证类型: {scheme_type}")
            return None
    
    def _get_api_key_value(self, scheme_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        获取API Key认证值
        
        Args:
            scheme_config: API Key方案配置
            
        Returns:
            API Key认证配置
        """
        key_name = scheme_config.get('name', '')
        key_location = scheme_config.get('in', '')
        description = scheme_config.get('description', '')
        
        print(f"API Key名称: {key_name}")
        print(f"位置: {key_location}")
        if description:
            print(f"说明: {description}")
        
        key_value = input(f"请输入 {key_name} 的值: ").strip()
        
        if key_value:
            return {
                'type': 'apiKey',
                'name': key_name,
                'value': key_value,
                'in': key_location
            }
        return None
    
    def _get_http_auth_value(self, scheme_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        获取HTTP认证值
        
        Args:
            scheme_config: HTTP认证方案配置
            
        Returns:
            HTTP认证配置
        """
        http_scheme = scheme_config.get('scheme', '').lower()
        description = scheme_config.get('description', '')
        
        print(f"HTTP认证方案: {http_scheme}")
        if description:
            print(f"说明: {description}")
        
        if http_scheme == 'bearer':
            token = input("请输入Bearer Token: ").strip()
            if token:
                return {
                    'type': 'http',
                    'scheme': 'bearer',
                    'token': token
                }
        elif http_scheme == 'basic':
            username = input("用户名: ").strip()
            password = input("密码: ").strip()
            if username and password:
                return {
                    'type': 'http',
                    'scheme': 'basic',
                    'username': username,
                    'password': password
                }
        else:
            print(f"⚠️  暂不支持的HTTP认证方案: {http_scheme}")
        
        return None
    
    def _get_oauth2_value(self, scheme_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        获取OAuth2认证值
        
        Args:
            scheme_config: OAuth2方案配置
            
        Returns:
            OAuth2认证配置
        """
        flows = scheme_config.get('flows', {})
        description = scheme_config.get('description', '')
        
        print(f"OAuth2流程: {list(flows.keys())}")
        if description:
            print(f"说明: {description}")
        
        # 简化处理，只要求access token
        token = input("请输入Access Token: ").strip()
        if token:
            return {
                'type': 'oauth2',
                'token': token
            }
        
        return None
    
    def _create_http_client_config(self, auth_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建HTTP客户端配置
        
        Args:
            auth_config: 认证配置
            
        Returns:
            HTTP客户端配置字典
        """
        client_config = {
            'timeout': self.timeout
        }
        
        headers = {}
        cookies = {}
        auth = None
        
        # 应用认证配置
        for scheme_name, scheme_auth in auth_config.items():
            auth_type = scheme_auth.get('type', '')
            
            if auth_type == 'apiKey':
                key_name = scheme_auth['name']
                key_value = scheme_auth['value']
                key_location = scheme_auth['in']
                
                if key_location == 'header':
                    headers[key_name] = key_value
                elif key_location == 'cookie':
                    cookies[key_name] = key_value
                # query参数认证需要在每个请求中处理，这里不设置
            
            elif auth_type == 'http':
                http_scheme = scheme_auth['scheme']
                
                if http_scheme == 'bearer':
                    headers['Authorization'] = f"Bearer {scheme_auth['token']}"
                elif http_scheme == 'basic':
                    # 对于basic认证，我们设置auth参数
                    auth = (scheme_auth['username'], scheme_auth['password'])
            
            elif auth_type == 'oauth2':
                headers['Authorization'] = f"Bearer {scheme_auth['token']}"
        
        # 设置客户端配置
        if headers:
            client_config['headers'] = headers
        if cookies:
            client_config['cookies'] = cookies
        if auth:
            client_config['auth'] = auth
        
        return client_config
    
    def start_server(self, source: str, transport: str = "streamable-http", 
                    host: str = "127.0.0.1", port: int = 8000, validate: bool = True):
        """
        启动MCP服务器
        
        Args:
            source: OpenAPI文档源
            transport: 传输协议
            host: 服务器主机
            port: 服务器端口
            validate: 是否验证文档
        """
        mcp = self.convert(source, validate=validate)
        
        if transport == "streamable-http":
            print(f"🚀 启动streamable-http MCP服务器: http://{host}:{port}")
            print("按 Ctrl+C 停止服务器")
            print()
            mcp.run(transport=transport, host=host, port=port)
        else:
            print(f"🚀 启动MCP服务器，传输协议: {transport}")
            mcp.run(transport=transport)
    
    def _basic_validate(self, openapi_doc: Dict[str, Any]):
        """
        基本验证OpenAPI文档
        
        Args:
            openapi_doc: OpenAPI文档
            
        Raises:
            ValueError: 验证失败
        """
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in openapi_doc:
                raise ValueError(f"OpenAPI文档缺少必需字段: {field}")
        
        paths = openapi_doc.get('paths', {})
        if not paths:
            raise ValueError("OpenAPI文档没有定义任何API路径")
    
    def _extract_server_url(self, openapi_doc: Dict[str, Any]) -> str:
        """
        提取服务器URL
        
        Args:
            openapi_doc: OpenAPI文档
            
        Returns:
            服务器URL
        """
        # 优先使用构造函数中指定的base_url
        if self.base_url:
            self.logger.info(f"使用构造函数指定的base_url: {self.base_url}")
            return self.base_url
        
        # 从OpenAPI文档的servers字段提取
        servers = openapi_doc.get('servers', [])
        if servers and len(servers) > 0:
            server_url = servers[0].get('url', '')
            if server_url:
                self.logger.info(f"从文档servers字段提取URL: {server_url}")
                return server_url
        
        # 如果没有servers字段或为空，记录警告
        self.logger.warning("OpenAPI文档缺少servers配置或servers为空")
        return None  # 返回None表示需要用户手动输入
    
    def _check_and_get_server_url(self, openapi_doc: Dict[str, Any]) -> str:
        """
        检查并获取服务器URL，如果文档中没有则提示用户输入
        
        Args:
            openapi_doc: OpenAPI文档
            
        Returns:
            服务器URL
        """
        server_url = self._extract_server_url(openapi_doc)
        
        if server_url is None:
            print("\n⚠️  OpenAPI文档中未找到servers配置")
            print("请手动输入API服务器的基础URL")
            print("示例: https://api.example.com 或 http://localhost:3000")
            
            while True:
                manual_url = input("\nAPI服务器基础URL: ").strip()
                if manual_url:
                    # 简单的URL格式验证
                    if manual_url.startswith(('http://', 'https://')):
                        self.logger.info(f"用户手动输入的服务器URL: {manual_url}")
                        return manual_url
                    else:
                        print("⚠️  URL格式错误，请以 http:// 或 https:// 开头")
                else:
                    print("⚠️  URL不能为空，请重新输入")
        
        return server_url
    
    def _count_apis(self, openapi_doc: Dict[str, Any]) -> int:
        """
        统计API数量
        
        Args:
            openapi_doc: OpenAPI文档
            
        Returns:
            API数量
        """
        paths = openapi_doc.get('paths', {})
        count = 0
        
        for path, methods in paths.items():
            if isinstance(methods, dict):
                # 计算每个路径下的HTTP方法数量
                http_methods = ['get', 'post', 'put', 'delete', 'patch', 'head', 'options']
                count += sum(1 for method in http_methods if method in methods)
        
        return count