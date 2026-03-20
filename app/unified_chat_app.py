"""
统一对话界面 - 物流业务智能可行性评估系统

采用ChatGPT风格的统一对话界面，所有功能通过自然语言对话实现
"""

import streamlit as st
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm import AdaptiveAssessorV2
from src.models import CostLinkConfig


# 页面配置
st.set_page_config(
    page_title="物流业务智能评估助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def init_session_state():
    """初始化session state"""
    if 'assessor' not in st.session_state:
        st.session_state.assessor = AdaptiveAssessorV2()
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_state' not in st.session_state:
        st.session_state.current_state = "idle"
    if 'waiting_for' not in st.session_state:
        st.session_state.waiting_for = None  # 等待用户输入的类型


def display_chat_message(role: str, content: str, message_type: str = "text"):
    """显示聊天消息"""
    with st.chat_message(role):
        if message_type == "cost_result":
            # 成本结果用特殊格式显示
            st.markdown(content)
        elif message_type == "confirmation":
            # 确认请求用信息框显示
            st.info(content)
        elif message_type == "error":
            # 错误用错误框显示
            st.error(content)
        elif message_type == "success":
            # 成功用成功框显示
            st.success(content)
        else:
            st.markdown(content)


def format_cost_result(result: dict) -> str:
    """格式化成本评估结果"""
    if not result.get("success"):
        return ""
    
    cost_result = result.get("cost_result")
    if not cost_result:
        return ""
    
    lines = [
        "\n### 📊 成本评估结果",
        f"\n**场景**: {cost_result.scenario_name}",
        f"**业务类型**: {cost_result.business_type}",
        "",
        "#### 💰 成本汇总",
        f"- 月度总成本: ¥{cost_result.total_monthly_cost:,.2f}",
        f"- 单均成本: ¥{cost_result.total_cost_per_order:.2f}",
        f"- 单件成本: ¥{cost_result.total_cost_per_item:.2f}",
        "",
        "#### 📈 成本结构",
    ]
    
    for category, percentage in cost_result.cost_structure.items():
        lines.append(f"- {category}: {percentage:.1f}%")
    
    if cost_result.risk_factors:
        lines.extend(["", "#### ⚠️ 风险提示"])
        for risk in cost_result.risk_factors:
            lines.append(f"- {risk}")
    
    lines.extend(["", "---", "💡 **提示**: 您可以继续询问订单可行性（提供采购价和售价），或询问具体的成本细节。"])
    
    return "\n".join(lines)


def format_profit_result(result: dict) -> str:
    """格式化利润评估结果"""
    if not result.get("has_profit_assessment"):
        return ""
    
    assessment = result.get("profit_assessment", {})
    costs = assessment.get("costs", {})
    profit = assessment.get("profit", {})
    
    lines = [
        "\n### 💹 订单可行性评估",
        "",
        "#### 📊 成本分析",
        f"- 商品采购成本: ¥{costs.get('product_cost', 0):.2f}",
        f"- 物流成本: ¥{costs.get('logistics_cost', 0):.2f}",
        f"- 总成本: ¥{costs.get('total_cost', 0):.2f}",
        "",
        "#### 💰 收入与利润",
        f"- 销售收入: ¥{assessment.get('revenue', {}).get('net_revenue', 0):.2f}",
        f"- 毛利: ¥{profit.get('gross_profit', 0):.2f}",
        f"- 毛利率: {profit.get('gross_margin', 0):.1f}%",
        f"- 可行性: {assessment.get('feasibility', 'unknown')}",
    ]
    
    if assessment.get("suggestions"):
        lines.extend(["", "#### 💡 建议"])
        for suggestion in assessment["suggestions"]:
            lines.append(f"- {suggestion}")
    
    if assessment.get("warnings"):
        lines.extend(["", "#### ⚠️ 警告"])
        for warning in assessment["warnings"]:
            lines.append(f"- {warning}")
    
    return "\n".join(lines)


def process_user_input(user_input: str):
    """处理用户输入"""
    # 添加用户消息到历史
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 使用评估器处理
    with st.spinner("🤔 思考中..."):
        result = st.session_state.assessor.assess_from_text(user_input)
    
    # 根据结果类型生成回复
    response_content = ""
    message_type = "text"
    
    if result.get("needs_more_info"):
        # 需要更多信息
        message_type = "confirmation"
        response_content = result.get("message", "需要更多信息")
        st.session_state.waiting_for = "parameters"
        
    elif result.get("needs_confirmation"):
        # 需要确认
        message_type = "confirmation"
        if "confirmation_dialog" in result:
            response_content = result["confirmation_dialog"]
        else:
            response_content = result.get("message", "请确认")
        st.session_state.waiting_for = "confirmation"
        
    elif result.get("success"):
        # 评估成功
        if result.get("has_profit_assessment"):
            # 利润评估结果
            message_type = "success"
            response_content = format_profit_result(result)
        else:
            # 成本评估结果
            message_type = "cost_result"
            response_content = format_cost_result(result)
        st.session_state.waiting_for = None
        
    elif result.get("needs_profit_input"):
        # 需要利润评估的输入
        message_type = "confirmation"
        response_content = result.get("message", "请提供采购价和销售价")
        st.session_state.waiting_for = "profit_info"
        
    else:
        # 其他情况（错误或其他响应）
        if result.get("error"):
            message_type = "error"
            response_content = f"抱歉，处理时出现问题：{result.get('message', '未知错误')}"
        else:
            # 普通对话响应
            response_content = result.get("message", "我已收到您的信息，请继续描述您的业务需求。")
    
    # 添加助手回复到历史
    st.session_state.messages.append({
        "role": "assistant", 
        "content": response_content,
        "type": message_type
    })


def main():
    """主函数"""
    init_session_state()
    
    # 标题
    st.title("🤖 物流业务智能评估助手")
    st.markdown("---")
    
    # 显示欢迎信息
    if not st.session_state.messages:
        welcome_message = """
        👋 您好！我是您的物流业务智能评估助手。
        
        我可以帮您：
        - 📝 **评估物流成本** - 输入业务描述，我自动计算各环节成本
        - 💹 **分析订单可行性** - 提供采购价和售价，我帮您算毛利
        - ❓ **回答物流问题** - 关于物流成本、优化建议等
        
        **示例输入**：
        - "每天运送100箱苹果到10公里外的超市，每箱重5公斤"
        - "这单能不能做？采购价50元，售价80元"
        - "如何降低配送成本？"
        
        请直接输入您的问题或业务描述，我们开始吧！
        """
        st.session_state.messages.append({
            "role": "assistant",
            "content": welcome_message,
            "type": "text"
        })
    
    # 显示对话历史
    for message in st.session_state.messages:
        display_chat_message(
            message["role"],
            message["content"],
            message.get("type", "text")
        )
    
    # 输入框
    user_input = st.chat_input("请输入业务描述或问题...")
    
    if user_input:
        process_user_input(user_input)
        st.rerun()
    
    # 侧边栏 - 显示当前状态和快捷操作
    with st.sidebar:
        st.markdown("### 📋 当前状态")
        
        state_labels = {
            "idle": "等待输入",
            "collecting_params": "收集参数",
            "confirming_params": "确认参数",
            "confirming_links": "确认成本环节",
            "calculated": "计算完成",
            "profit_assessment": "利润评估"
        }
        
        current_state = st.session_state.assessor.get_current_state()
        st.write(f"状态: {state_labels.get(current_state.get('state', 'idle'), '未知')}")
        
        if current_state.get("has_result"):
            st.success("✅ 已完成成本评估")
        
        if current_state.get("has_profit_assessment"):
            st.success("✅ 已完成利润评估")
        
        st.markdown("---")
        
        # 快捷操作
        st.markdown("### ⚡ 快捷操作")
        
        if st.button("🔄 开始新评估"):
            st.session_state.assessor.reset()
            st.session_state.messages = []
            st.session_state.waiting_for = None
            st.rerun()
        
        if st.button("🗑️ 清空对话"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        
        # 使用提示
        st.markdown("### 💡 使用提示")
        st.info("""
        **您可以这样问我：**
        
        1. **成本评估**
           - "每天100单办公用品，送到20公里外"
           - "运送50箱水果，需要冷链，距离15公里"
        
        2. **订单可行性**
           - "这单能不能做？采购价50，售价80"
           - "利润怎么样？进货100，卖150"
        
        3. **成本查询**
           - "运输成本怎么算的？"
           - "哪个环节成本最高？"
        """)


if __name__ == "__main__":
    main()
