@echo off
echo ========================================
echo   OpenAPI到MCP转换工具
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist venv (
    echo ❌ 虚拟环境不存在，请先运行 install.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
echo 🚀 启动OpenAPI到MCP转换服务...
echo.
call venv\Scripts\activate.bat

REM 进入项目目录并运行
cd openapi_to_mcp
python main.py

echo.
echo 服务已停止
pause