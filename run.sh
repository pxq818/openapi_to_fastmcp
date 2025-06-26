#!/bin/bash

echo "========================================"
echo "  OpenAPI到MCP转换工具"
echo "========================================"
echo

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 虚拟环境不存在，请先运行 ./install.sh"
    exit 1
fi

# 激活虚拟环境
echo "🚀 启动OpenAPI到MCP转换服务..."
echo
source venv/bin/activate

# 进入项目目录并运行
cd openapi_to_mcp
python main.py

echo
echo "服务已停止"