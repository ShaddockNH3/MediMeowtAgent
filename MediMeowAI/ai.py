import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 导入并运行服务器
from connect.server import run_server

if __name__ == "__main__":
    run_server()
