#!/bin/bash

echo "========================================"
echo "  OpenAPI到MCP转换工具 - 安装程序"
echo "========================================"
echo

# 检查Python是否安装
echo "[1/4] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "❌ 错误：未找到Python，请先安装Python 3.8+"
        echo "Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
        echo "CentOS/RHEL: sudo yum install python3 python3-pip"
        echo "macOS: brew install python3"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi
echo "✅ Python环境检查通过"

# 创建虚拟环境
echo
echo "[2/4] 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "⚠️  虚拟环境已存在，跳过创建"
else
    $PYTHON_CMD -m venv venv
    echo "✅ 虚拟环境创建完成"
fi

# 激活虚拟环境
echo
echo "[3/4] 激活虚拟环境..."
source venv/bin/activate
echo "✅ 虚拟环境已激活"

# 安装依赖
echo
echo "[4/4] 安装依赖包..."
echo "使用清华大学镜像源加速下载..."
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败，尝试使用默认源..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 安装失败，请检查网络连接"
        exit 1
    fi
fi
echo "✅ 依赖安装完成"

echo
echo "========================================"
echo "✅ 安装完成！"
echo "========================================"
echo
echo "使用方法："
echo "  1. 运行 ./run.sh"
echo "  2. 或在命令行执行："
echo "     source venv/bin/activate"
echo "     cd openapi_to_mcp"
echo "     python main.py"
echo