# OpenAPI to FastMCP 转换工具

这是一个将OpenAPI规范转换为FastMCP服务的工具。该工具可以读取OpenAPI规范文件，并创建一个FastMCP服务器，提供API代理功能。

## 功能特点

- 支持从OpenAPI规范文件创建FastMCP服务
- 自动将HTTP路由映射为FastMCP组件（工具和资源）
- 提供交互式命令行界面，方便配置参数
- 支持自定义路由映射规则

## 安装要求

- Python 3.12+
- fastmcp
- httpx

## 使用方法

### 1. 创建并激活虚拟环境

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 2. 安装依赖

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### 3. 运行程序

```bash
python convert_openapi_to_fastmcp.py
```

