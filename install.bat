@echo off
echo ========================================
echo   OpenAPI到MCP转换工具 - 安装程序
echo ========================================
echo.

REM 检查Python是否安装
echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python，请先安装Python 3.8+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python环境检查通过

REM 创建虚拟环境
echo.
echo [2/4] 创建虚拟环境...
if exist venv (
    echo ⚠️  虚拟环境已存在，跳过创建
) else (
    python -m venv venv
    echo ✅ 虚拟环境创建完成
)

REM 激活虚拟环境
echo.
echo [3/4] 激活虚拟环境...
call venv\Scripts\activate.bat
echo ✅ 虚拟环境已激活

REM 安装依赖
echo.
echo [4/4] 安装依赖包...
echo 使用清华大学镜像源加速下载...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
if errorlevel 1 (
    echo ❌ 依赖安装失败，尝试使用默认源...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 安装失败，请检查网络连接
        pause
        exit /b 1
    )
)
echo ✅ 依赖安装完成

echo.
echo ========================================
echo ✅ 安装完成！
echo ========================================
echo.
echo 使用方法：
echo   1. 双击运行 run.bat
echo   2. 或在命令行执行：
echo      venv\Scripts\activate.bat
echo      cd openapi_to_mcp
echo      python main.py
echo.
pause