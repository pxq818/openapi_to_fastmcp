"""
OpenAPI文档加载器

支持从URL或本地文件加载OpenAPI文档
"""

import json
import httpx
import yaml
from typing import Dict, Any
from pathlib import Path
from loguru import logger


class OpenAPILoader:
    """
    OpenAPI文档加载器
    
    支持从URL、本地JSON文件、YAML文件加载OpenAPI文档
    """
    
    def __init__(self, timeout: int = 30):
        """
        初始化加载器
        
        Args:
            timeout: HTTP请求超时时间（秒）
        """
        self.timeout = timeout
        self.logger = logger
    
    def load(self, source: str) -> Dict[str, Any]:
        """
        加载OpenAPI文档
        
        Args:
            source: 文档源（URL或文件路径）
            
        Returns:
            OpenAPI文档字典
        """
        if self._is_url(source):
            return self._load_from_url(source)
        else:
            return self._load_from_file(source)
    
    def _is_url(self, source: str) -> bool:
        """
        判断是否为URL
        
        Args:
            source: 源字符串
            
        Returns:
            是否为URL
        """
        return source.startswith(('http://', 'https://'))
    
    def _load_from_url(self, url: str) -> Dict[str, Any]:
        """
        从URL加载OpenAPI文档
        
        Args:
            url: OpenAPI文档URL
            
        Returns:
            OpenAPI文档字典
        """
        try:
            print(f"📥 从URL加载OpenAPI文档: {url}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url)
                response.raise_for_status()
                
                # 尝试解析为JSON，失败则尝试YAML
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return yaml.safe_load(response.text)
                        
        except Exception as e:
            self.logger.error(f"从URL加载OpenAPI文档失败: {e}")
            raise
    
    def _load_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        从本地文件加载OpenAPI文档
        
        Args:
            file_path: 文件路径
            
        Returns:
            OpenAPI文档字典
        """
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            print(f"📁 从文件加载OpenAPI文档: {file_path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in ['.json']:
                    return json.load(f)
                elif path.suffix.lower() in ['.yaml', '.yml']:
                    return yaml.safe_load(f)
                else:
                    # 尝试解析为JSON，失败则尝试YAML
                    content = f.read()
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return yaml.safe_load(content)
                        
        except Exception as e:
            self.logger.error(f"从文件加载OpenAPI文档失败: {e}")
            raise