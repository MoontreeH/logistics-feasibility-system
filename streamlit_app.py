"""
Streamlit Cloud 主入口文件

物流业务智能可行性评估系统 - 统一对话界面版本
部署到 Streamlit Cloud 使用此文件作为入口
"""

import streamlit as st
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

# 导入统一对话界面
from app.unified_chat_app import main

if __name__ == "__main__":
    main()
