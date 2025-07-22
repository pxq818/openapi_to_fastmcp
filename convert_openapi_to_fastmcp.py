import json
import os
import sys
from typing import Any, Dict, List, Optional, Set

import httpx
from fastmcp import FastMCP
from fastmcp.server.openapi import FastMCPOpenAPI, MCPType, RouteMap
from fastmcp.utilities.openapi import HTTPRoute
import asyncio


def load_openapi_spec(file_path: str) -> Dict[str, Any]:
    """加载OpenAPI规范文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载OpenAPI文件失败: {e}")
        sys.exit(1)


def create_route_maps() -> List[RouteMap]:
    """创建路由映射配置
    
    默认配置：
    - GET请求映射为RESOURCE
    - 其他请求映射为TOOL
    """
    return [
        # GET请求映射为资源
        # RouteMap(methods=["GET"], mcp_type=MCPType.RESOURCE),
        # 其他请求映射为工具
        RouteMap(mcp_type=MCPType.TOOL),
    ]


def custom_route_map_fn(route: HTTPRoute, mcp_type: MCPType) -> Optional[MCPType]:
    """自定义路由映射函数
    
    可以根据路由的特定属性（如路径、标签等）自定义映射类型
    """
    # 示例：如果路径包含特定字符串，将其映射为特定类型
    if "statistics" in route.path.lower():
        return MCPType.RESOURCE
    
    # 返回None表示使用默认映射
    return None


async def get_component_counts(fastmcp_server: FastMCPOpenAPI):
    """异步获取组件数量"""
    # 获取工具数量
    tools = await fastmcp_server.get_tools()
    tools_count = len(tools)
    print(f"- 工具数量: {tools_count}")
    
    # 获取资源数量
    resources = await fastmcp_server.get_resources()
    resources_count = len(resources)
    print(f"- 资源数量: {resources_count}")
    
    # 获取资源模板数量
    templates = await fastmcp_server.get_resource_templates()
    templates_count = len(templates)
    print(f"- 资源模板数量: {templates_count}")


def convert_openapi_to_fastmcp(openapi_file: str, base_url: str = "http://localhost:8000"):
    """将OpenAPI文件转换为FastMCP服务"""
    print(f"正在加载OpenAPI文件: {openapi_file}")
    openapi_spec = load_openapi_spec(openapi_file)
    
    # 创建HTTP客户端
    client = httpx.AsyncClient(base_url=base_url)
    
    # 创建路由映射
    route_maps = create_route_maps()
    
    print("正在解析OpenAPI规范...")
    try:
        # 创建FastMCP服务
        fastmcp_server = FastMCP.from_openapi(
            openapi_spec=openapi_spec,
            client=client,
            route_maps=route_maps
            # route_map_fn=custom_route_map_fn,
            # 可选：自定义组件名称
            # mcp_names={},
            # # 可选：添加标签
            # tags=set(["api"]),
            # # 可选：设置超时时间（秒）
            # timeout=30.0,
        )
        
        print("OpenAPI规范解析成功！")
        print(f"创建了FastMCP服务，包含以下组件:")
        
        # 异步获取组件数量
        asyncio.run(get_component_counts(fastmcp_server))
        
        return fastmcp_server
    
    except Exception as e:
        print(f"解析OpenAPI规范失败: {e}")
        sys.exit(1)


def start_server(fastmcp_server: FastMCPOpenAPI, transport: str = "streamable-http", host: str = "localhost", port: int = 8080):
    """启动FastMCP服务器"""
    print(f"正在启动FastMCP服务器，监听地址: {host}:{port}")
    try:
        fastmcp_server.run(transport="streamable-http", host=host, port=port)
    except Exception as e:
        print(f"启动FastMCP服务器失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # 通过用户交互获取参数
    print("=== FastMCP OpenAPI 转换工具 ===")
    
    # OpenAPI文件路径
    default_openapi_file = "FSSTHJJ.openapi.json"
    openapi_file = input(f"请输入OpenAPI文件路径 [默认: {default_openapi_file}]: ").strip()
    if not openapi_file:
        openapi_file = default_openapi_file
    
    # 目标API服务的基础URL
    default_base_url = "http://27.36.118.5:21100"
    base_url = input(f"请输入目标API服务的基础URL [默认: {default_base_url}]: ").strip()
    if not base_url:
        base_url = default_base_url
    
    # 主机名
    default_host = "localhost"
    host = input(f"请输入服务器主机名 [默认: {default_host}]: ").strip()
    if not host:
        host = default_host
    
    # 端口号
    default_port = 8045
    port_input = input(f"请输入服务器端口号 [默认: {default_port}]: ").strip()
    port = int(port_input) if port_input else default_port
    
    # 传输方式
    default_transport = "streamable-http"
    transport = input(f"请输入传输方式 [默认: {default_transport}]: ").strip()
    if not transport:
        transport = default_transport
    
    print("\n=== 参数确认 ===")
    print(f"OpenAPI文件路径: {openapi_file}")
    print(f"目标API服务的基础URL: {base_url}")
    print(f"服务器主机名: {host}")
    print(f"服务器端口号: {port}")
    print(f"传输方式: {transport}")
    print("\n")
    
    # 转换OpenAPI为FastMCP服务
    fastmcp_server = convert_openapi_to_fastmcp(openapi_file, base_url)
    
    # 启动FastMCP服务器
    start_server(fastmcp_server, transport=transport, host=host, port=port)
