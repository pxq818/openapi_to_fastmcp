# OpenAPI到MCP转换工具

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

将OpenAPI文档转换为MCP (Model Context Protocol) 服务的工具，支持跨平台部署。

## ✨ 特性

- 🔄 自动将OpenAPI文档转换为MCP服务
- 🔐 支持多种认证方式（API Key、Bearer Token、Basic Auth、OAuth2）
- 🌐 支持本地文件和远程URL的OpenAPI文档
- 🚀 一键启动MCP服务器
- 📦 跨平台支持（Windows、Linux、macOS）
- 🛠️ 简单的安装和配置流程

## 🚀 快速开始

### 系统要求

- Python 3.8 或更高版本
- 网络连接（用于下载依赖包）

### 安装方法

#### 方法1：克隆仓库（推荐）

```bash
# 克隆项目
git clone https://github.com/yourusername/openapi-to-mcp.git
cd openapi-to-mcp

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖（使用清华镜像源）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```
