"""
OpenAPI到MCP转换工具

将OpenAPI接口文档转换为MCP服务的工具包
"""

from .converter import OpenAPIMCPConverter
from .loader import OpenAPILoader

__version__ = "1.0.0"
__author__ = "AI Assistant"
__description__ = "OpenAPI到MCP转换工具"

__all__ = [
    'OpenAPIMCPConverter',
    'OpenAPILoader'
]