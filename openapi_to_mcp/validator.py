"""
OpenAPI文档验证器

验证OpenAPI文档的格式和完整性
"""

from typing import Dict, Any, List, Tuple
from loguru import logger


class OpenAPIValidator:
    """
    OpenAPI文档验证器
    
    验证OpenAPI 3.0文档的基本结构和必需字段
    """
    
    def __init__(self):
        self.logger = logger
        self.required_fields = ['openapi', 'info', 'paths']
        self.supported_versions = ['3.0.0', '3.0.1', '3.0.2', '3.0.3', '3.1.0']
    
    def validate(self, openapi_doc: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        验证OpenAPI文档
        
        Args:
            openapi_doc: OpenAPI文档字典
            
        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []
        
        # 检查必需字段
        errors.extend(self._check_required_fields(openapi_doc))
        
        # 检查版本
        errors.extend(self._check_version(openapi_doc))
        
        # 检查info字段
        errors.extend(self._check_info_section(openapi_doc))
        
        # 检查paths字段
        errors.extend(self._check_paths_section(openapi_doc))
        
        is_valid = len(errors) == 0
        
        if is_valid:
            self.logger.info("OpenAPI文档验证通过")
        else:
            self.logger.warning(f"OpenAPI文档验证失败，发现 {len(errors)} 个错误")
            for error in errors:
                self.logger.warning(f"  - {error}")
        
        return is_valid, errors
    
    def _check_required_fields(self, doc: Dict[str, Any]) -> List[str]:
        """
        检查必需字段
        
        Args:
            doc: OpenAPI文档
            
        Returns:
            错误信息列表
        """
        errors = []
        for field in self.required_fields:
            if field not in doc:
                errors.append(f"缺少必需字段: {field}")
        return errors
    
    def _check_version(self, doc: Dict[str, Any]) -> List[str]:
        """
        检查OpenAPI版本
        
        Args:
            doc: OpenAPI文档
            
        Returns:
            错误信息列表
        """
        errors = []
        version = doc.get('openapi')
        if version and version not in self.supported_versions:
            errors.append(f"不支持的OpenAPI版本: {version}，支持的版本: {', '.join(self.supported_versions)}")
        return errors
    
    def _check_info_section(self, doc: Dict[str, Any]) -> List[str]:
        """
        检查info部分
        
        Args:
            doc: OpenAPI文档
            
        Returns:
            错误信息列表
        """
        errors = []
        info = doc.get('info', {})
        
        if not isinstance(info, dict):
            errors.append("info字段必须是对象")
            return errors
        
        required_info_fields = ['title', 'version']
        for field in required_info_fields:
            if field not in info:
                errors.append(f"info部分缺少必需字段: {field}")
        
        return errors
    
    def _check_paths_section(self, doc: Dict[str, Any]) -> List[str]:
        """
        检查paths部分
        
        Args:
            doc: OpenAPI文档
            
        Returns:
            错误信息列表
        """
        errors = []
        paths = doc.get('paths', {})
        
        if not isinstance(paths, dict):
            errors.append("paths字段必须是对象")
            return errors
        
        if len(paths) == 0:
            errors.append("paths部分为空，没有定义任何API路径")
        
        return errors