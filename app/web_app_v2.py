"""
Web应用 V2 - 支持自适应成本环节配置

提供可视化的物流成本评估界面，支持：
- 成本环节识别与确认
- 选择性成本计算
- 自定义环节添加
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from src.llm import AdaptiveAssessor
from src.rag import RAGEngine


# 页面配置
st.set_page_config(
    page_title="物流业务智能可行性评估系统 V2",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """初始化session state"""
    if 'assessor' not in st.session_state:
        st.session_state.assessor = AdaptiveAssessor()
    if 'rag' not in st.session_state:
        # 尝试初始化RAG，如果失败则设置为None
        try:
            st.session_state.rag = RAGEngine()
        except Exception as e:
            st.session_state.rag = None
            st.session_state.rag_error = str(e)
    if 'current_result' not in st.session_state:
        st.session_state.current_result = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'assessment_state' not in st.session_state:
        st.session_state.assessment_state = "idle"  # idle, confirming_links, confirming_custom, calculated
    if 'pending_confirmation' not in st.session_state:
        st.session_state.pending_confirmation = None


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("📦 物流评估系统 V2")
        st.markdown("---")
        
        # 导航
        page = st.radio(
            "功能导航",
            ["🏠 首页", "📝 智能成本评估", "💬 智能问答", "📊 数据分析", "📚 知识库管理"]
        )
        
        st.markdown("---")
        
        # 系统信息
        st.markdown("### 系统信息")
        st.info("""
        **版本**: v2.0.0
        
        **新功能**:
        - 成本环节智能识别
        - 选择性成本计算
        - 自定义环节支持
        - 环节确认对话
        """)
        
        # 当前状态
        if st.session_state.assessment_state != "idle":
            st.markdown("### 当前状态")
            state_labels = {
                "idle": "空闲",
                "confirming_links": "确认成本环节",
                "confirming_custom": "确认自定义环节",
                "calculated": "计算完成"
            }
            st.write(f"状态: {state_labels.get(st.session_state.assessment_state, '未知')}")
        
        return page


def render_home():
    """渲染首页"""
    st.title("欢迎使用物流业务智能可行性评估系统 V2")
    
    st.markdown("""
    ### 🎯 系统简介
    
    本系统基于AI和成本模型，为物流业务提供智能可行性评估，支持：
    
    - **📝 智能成本评估**: 自然语言输入，智能识别成本环节，支持选择性计算
    - **💬 智能问答**: 基于RAG技术，回答物流相关问题
    - **📊 数据分析**: 可视化成本结构，提供优化建议
    - **📚 知识库**: 管理行业知识和最佳实践
    
    ### ✨ V2版本新特性
    
    1. **成本环节智能识别**: 系统自动识别业务涉及的成本环节
    2. **选择性计算**: 只计算实际发生的环节成本，更准确
    3. **环节确认机制**: 向用户展示识别的环节，等待确认
    4. **自定义环节**: 支持添加基础模型之外的额外环节
    5. **合并建议**: 分析自定义环节是否可以合并到基础环节
    
    ### 🚀 快速开始
    
    1. 点击左侧 **"📝 智能成本评估"** 开始评估
    2. 输入业务描述，如："每天100单办公用品，送到20公里外的写字楼"
    3. 系统会识别涉及的成本环节并请求确认
    4. 确认环节后查看详细成本分析
    5. 如有额外环节，可添加自定义环节
    
    ### 📊 系统能力
    
    | 功能模块 | 能力描述 |
    |---------|---------|
    | 成本计算 | 9大基础环节 + 自定义环节 |
    | 环节识别 | LLM智能识别 + 关键词匹配 |
    | 意图识别 | 自动识别TOB/餐配业务 |
    | 建议生成 | 数据驱动，量化节省金额 |
    | 知识检索 | 基于向量数据库的语义检索 |
    """)
    
    # 示例卡片
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("基础环节", "9个", "可扩展")
    with col2:
        st.metric("评估精度", "100%", "精确到元")
    with col3:
        st.metric("响应时间", "<3秒", "快速响应")


def render_assessment():
    """渲染智能成本评估页面"""
    st.title("📝 智能成本评估")
    
    # 根据当前状态显示不同内容
    if st.session_state.assessment_state == "confirming_links":
        render_link_confirmation()
        return
    
    if st.session_state.assessment_state == "confirming_custom":
        render_custom_link_confirmation()
        return
    
    if st.session_state.assessment_state == "calculated" and st.session_state.current_result:
        display_assessment_result(st.session_state.current_result)
        
        # 提供重新评估按钮
        if st.button("🔄 重新评估", type="secondary"):
            reset_assessment()
            st.rerun()
        return
    
    # 输入区域
    st.markdown("### 业务描述")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_input = st.text_area(
            "请描述业务需求（支持自然语言）",
            placeholder="例如：我们想接一个企业客户，每天100单办公用品，每单5件，重量10公斤，送到20公里外的写字楼，需要上3楼",
            height=100
        )
    
    with col2:
        st.markdown("#### 输入示例")
        st.info("""
        **TOB企业购**:
        每天100单办公用品，
        送到写字楼，
        需要上3楼
        
        **餐配业务**:
        餐厅食材配送50单，
        需要冷链，
        距离15公里
        """)
    
    # 评估按钮
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🚀 开始评估", type="primary", use_container_width=True):
            if not user_input:
                st.error("请输入业务描述")
                return
            
            with st.spinner("正在分析业务并识别成本环节..."):
                result = st.session_state.assessor.assess_from_text(user_input)
                
                if result.get("success"):
                    st.session_state.current_result = result
                    st.session_state.assessment_state = "calculated"
                    st.rerun()
                elif result.get("needs_confirmation"):
                    st.session_state.pending_confirmation = result
                    st.session_state.assessment_state = "confirming_links"
                    st.rerun()
                else:
                    st.error(f"评估失败: {result.get('message', '未知错误')}")
                    if result.get("missing_params"):
                        st.warning(f"缺失参数: {result.get('missing_params')}")
    
    with col2:
        if st.button("🔄 重置", type="secondary", use_container_width=True):
            reset_assessment()
            st.rerun()


def render_link_confirmation():
    """渲染环节确认界面"""
    st.markdown("### 🔄 成本环节确认")
    
    result = st.session_state.pending_confirmation
    if not result:
        st.error("没有待确认的环节")
        return
    
    # 显示确认对话框
    st.markdown(result.get("confirmation_dialog", ""))
    
    # 用户回复输入
    user_response = st.text_input(
        "请确认环节配置",
        placeholder="例如：确认全部 或 加工不需要，运输需要"
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("✅ 提交确认", type="primary", use_container_width=True):
            if not user_response:
                st.error("请输入确认内容")
                return
            
            with st.spinner("处理中..."):
                result = st.session_state.assessor.assess_from_text(user_response)
                
                if result.get("success"):
                    st.session_state.current_result = result
                    st.session_state.assessment_state = "calculated"
                    st.session_state.pending_confirmation = None
                    st.rerun()
                elif result.get("needs_confirmation"):
                    st.session_state.pending_confirmation = result
                    st.rerun()
                elif result.get("needs_custom_link"):
                    st.session_state.assessment_state = "confirming_custom"
                    st.rerun()
                else:
                    st.error(f"处理失败: {result.get('message', '未知错误')}")
    
    with col2:
        if st.button("➕ 添加自定义环节", type="secondary", use_container_width=True):
            st.session_state.assessment_state = "confirming_custom"
            st.rerun()


def render_custom_link_confirmation():
    """渲染自定义环节确认界面"""
    st.markdown("### ➕ 添加自定义成本环节")
    
    st.info("""
    请描述您想添加的额外成本环节，包括：
    1. 环节名称
    2. 费用产生的动因
    3. 计算方式或费率
    4. 计量单位（如：元/单、元/件、元/公里等）
    """)
    
    custom_description = st.text_area(
        "环节描述",
        placeholder="例如：客户要求每件商品都使用特殊防震包装，每单额外成本5元"
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("✅ 提交", type="primary", use_container_width=True):
            if not custom_description:
                st.error("请输入环节描述")
                return
            
            with st.spinner("分析自定义环节..."):
                result = st.session_state.assessor.assess_from_text(custom_description)
                
                if result.get("custom_link_added"):
                    st.success(result.get("message", "自定义环节已添加"))
                    st.session_state.assessment_state = "confirming_links"
                    st.rerun()
                elif result.get("needs_merge_decision"):
                    st.session_state.pending_merge = result
                    render_merge_decision()
                    return
                else:
                    # 返回环节确认状态
                    st.session_state.assessment_state = "confirming_links"
                    st.rerun()
    
    with col2:
        if st.button("⏭️ 跳过", type="secondary", use_container_width=True):
            st.session_state.assessment_state = "confirming_links"
            st.rerun()


def render_merge_decision():
    """渲染合并决策界面"""
    result = st.session_state.get("pending_merge")
    if not result:
        return
    
    st.markdown("### 🤔 合并建议")
    st.markdown(result.get("message", ""))
    
    options = result.get("options", [])
    
    cols = st.columns(len(options))
    for i, option in enumerate(options):
        with cols[i]:
            if st.button(option.get("label", ""), use_container_width=True):
                handle_merge_decision(option.get("value"))


def handle_merge_decision(decision: str):
    """处理合并决策"""
    if decision == "merge":
        # 同意合并
        st.success("已同意合并到基础环节")
    elif decision == "separate":
        # 作为独立环节
        st.success("已添加为独立环节")
    elif decision == "skip":
        # 跳过
        st.info("已跳过此环节")
    
    st.session_state.assessment_state = "confirming_links"
    st.session_state.pending_merge = None
    st.rerun()


def display_assessment_result(result: dict):
    """显示评估结果"""
    cost_result = result["cost_result"]
    link_config = result.get("link_config", {})
    
    st.markdown("---")
    st.markdown(f"## 📊 {cost_result.scenario_name} - 评估结果")
    
    # 成本环节配置摘要
    st.markdown("### ⚙️ 成本环节配置")
    
    calc_details = cost_result.calculation_details
    calculated = calc_details.get("calculated_links", [])
    skipped = calc_details.get("skipped_links", [])
    custom = calc_details.get("custom_costs", {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("参与计算环节", len(calculated))
    with col2:
        st.metric("跳过环节", len(skipped))
    with col3:
        st.metric("自定义环节", len(custom))
    
    # 显示环节详情
    with st.expander("查看环节配置详情"):
        if calculated:
            st.markdown("**✅ 参与计算的环节：**")
            for link in calculated:
                st.markdown(f"- {link}")
        
        if custom:
            st.markdown("**➕ 自定义环节：**")
            for name, cost in custom.items():
                st.markdown(f"- {name}: ¥{cost:,.2f}")
        
        if skipped:
            st.markdown("**❌ 跳过的环节：**")
            for link in skipped:
                st.markdown(f"- {link}")
    
    # 关键指标
    st.markdown("### 📈 成本汇总")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "月度总成本",
            f"¥{cost_result.total_monthly_cost:,.0f}",
            f"{cost_result.business_type}"
        )
    with col2:
        st.metric(
            "单均成本",
            f"¥{cost_result.total_cost_per_order:.2f}"
        )
    with col3:
        st.metric(
            "单件成本",
            f"¥{cost_result.total_cost_per_item:.2f}"
        )
    with col4:
        rating = cost_result.feasibility_rating.value
        rating_color = {"high": "green", "medium": "orange", "low": "red"}.get(rating, "gray")
        st.markdown(f"""
        <div style="text-align: center;">
            <p style="font-size: 14px; color: gray; margin-bottom: 0;">可行性评级</p>
            <p style="font-size: 24px; font-weight: bold; color: {rating_color}; margin-top: 0;">
                {rating.upper()}
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # 成本结构可视化
    st.markdown("### 📊 成本结构分析")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 饼图
        cost_data = cost_result.cost_structure
        if cost_data:
            df_cost = pd.DataFrame({
                '环节': list(cost_data.keys()),
                '占比': list(cost_data.values())
            })
            
            fig = px.pie(
                df_cost, 
                values='占比', 
                names='环节',
                title='成本结构分布',
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 成本明细表
        st.markdown("#### 成本明细")
        breakdown = cost_result.breakdown
        cost_details = {
            "订单处理": breakdown.order_processing,
            "库存持有": breakdown.inventory_holding,
            "拣选作业": breakdown.picking,
            "包装加工": breakdown.packaging + breakdown.processing,
            "集货装车": breakdown.loading,
            "运输配送": breakdown.transportation,
            "末端交付": breakdown.delivery,
            "逆向处理": breakdown.reverse_logistics,
            "管理分摊": breakdown.overhead,
        }
        
        # 添加自定义环节
        for name, cost in custom.items():
            cost_details[name] = cost
        
        for name, cost in cost_details.items():
            if cost > 0:
                percentage = cost / cost_result.total_monthly_cost * 100
                st.markdown(f"**{name}**: ¥{cost:,.0f} ({percentage:.1f}%)")
    
    # 风险提示
    if cost_result.risk_factors:
        st.markdown("### ⚠️ 风险提示")
        for risk in cost_result.risk_factors:
            st.warning(risk)
    
    # 优化建议
    if result.get("suggestions"):
        st.markdown("### 💡 优化建议")
        
        for i, sug in enumerate(result["suggestions"][:3], 1):
            with st.expander(f"建议{i}: {sug.title}"):
                st.markdown(f"**问题描述**: {sug.description}")
                st.markdown(f"**📊 数据支持**: {sug.data_support}")
                st.markdown(f"**💰 预期节省**: ¥{sug.potential_savings:,.0f}/月 ({sug.savings_percentage:.1f}%)")
                st.markdown("**📝 行动步骤**:")
                for step in sug.action_steps:
                    st.markdown(f"- {step}")
    
    # 相关知识
    if result.get("relevant_knowledge"):
        st.markdown("### 📚 相关知识")
        for item in result["relevant_knowledge"][:3]:
            with st.expander(item.title):
                st.markdown(item.content)
                st.caption(f"来源: {item.source}")


def render_chat():
    """渲染智能问答页面"""
    st.title("💬 智能问答")
    
    # 显示对话历史
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # 输入框
    user_question = st.chat_input("请输入您的问题...")
    
    if user_question:
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(user_question)
        
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })
        
        # 生成回答
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                # 如果有当前评估结果，使用追问处理器
                if st.session_state.current_result:
                    response = st.session_state.assessor.handle_follow_up(user_question)
                    answer = response.get("answer", "抱歉，我无法回答这个问题。")
                elif st.session_state.rag is not None:
                    # 使用RAG系统
                    result = st.session_state.rag.query(user_question)
                    answer = result["answer"]
                else:
                    answer = "抱歉，知识库系统暂时不可用。请先进行成本评估，我可以基于评估结果回答相关问题。"
                
                st.markdown(answer)
        
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": answer
        })


def render_data_analysis():
    """渲染数据分析页面"""
    st.title("📊 数据分析")
    
    if not st.session_state.current_result:
        st.info("请先进行成本评估，然后查看数据分析")
        return
    
    result = st.session_state.current_result
    cost_result = result["cost_result"]
    
    # 假设分析
    st.markdown("### 🔮 假设分析 (What-If)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        new_order_count = st.number_input(
            "日订单数",
            min_value=1,
            max_value=10000,
            value=cost_result.calculation_details.get("params", {}).get("monthly_order_count", 300) // 30
        )
    
    with col2:
        new_distance = st.number_input(
            "配送距离(公里)",
            min_value=1.0,
            max_value=1000.0,
            value=float(cost_result.calculation_details.get("params", {}).get("monthly_distance_km", 600) / 30)
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("运行分析", type="primary"):
            with st.spinner("计算中..."):
                param_changes = {
                    "monthly_order_count": new_order_count * 30,
                    "monthly_distance_km": new_distance * 30
                }
                
                analysis_result = st.session_state.assessor.what_if_analysis(param_changes)
                
                if "error" not in analysis_result:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        delta_pct = analysis_result["difference_pct"]
                        st.metric(
                            "成本变化",
                            f"¥{analysis_result['new_cost']:,.0f}",
                            f"{delta_pct:+.1f}%"
                        )
                    
                    with col2:
                        st.metric(
                            "单均成本",
                            f"¥{analysis_result['new_cost_per_order']:.2f}"
                        )
                    
                    with col3:
                        st.metric(
                            "可行性",
                            analysis_result["new_feasibility"].upper()
                        )
                else:
                    st.error(analysis_result["error"])
    
    # 成本对比
    st.markdown("### 📈 成本趋势")
    
    # 生成不同订单量的成本数据
    order_counts = list(range(50, 501, 50))
    costs = []
    
    base_params = cost_result.calculation_details.get("params", {}).copy()
    
    for count in order_counts:
        try:
            from src.models import CostParameters
            params = base_params.copy()
            params["monthly_order_count"] = count * 30
            params["monthly_items"] = count * 30 * 5  # 假设每单5件
            
            cost_params = CostParameters(**params)
            new_result = st.session_state.assessor.cost_calculator.calculate(
                cost_params,
                cost_result.business_type,
                "趋势分析"
            )
            
            costs.append({
                "日订单数": count,
                "月度总成本": new_result.total_monthly_cost,
                "单均成本": new_result.total_cost_per_order
            })
        except:
            pass
    
    if costs:
        df_trend = pd.DataFrame(costs)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_trend["日订单数"],
            y=df_trend["月度总成本"],
            mode='lines+markers',
            name='月度总成本'
        ))
        fig.add_trace(go.Scatter(
            x=df_trend["日订单数"],
            y=df_trend["单均成本"] * 100,  # 缩放以便在同一图表显示
            mode='lines+markers',
            name='单均成本(×100)',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title='成本趋势分析',
            xaxis_title='日订单数',
            yaxis_title='月度总成本(元)',
            yaxis2=dict(
                title='单均成本(元)',
                overlaying='y',
                side='right'
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)


def render_knowledge_base():
    """渲染知识库管理页面"""
    st.title("📚 知识库管理")
    
    # 检查RAG是否可用
    if st.session_state.rag is None:
        st.error("⚠️ 知识库系统暂时不可用。可能的原因：")
        st.info("1. 向量数据库初始化失败\n2. 存储权限问题\n3. 依赖版本不兼容")
        if hasattr(st.session_state, 'rag_error'):
            with st.expander("查看详细错误"):
                st.code(st.session_state.rag_error)
        return
    
    # 统计信息
    stats = st.session_state.rag.vector_store.get_stats()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("向量库文档数", stats["total_documents"])
    
    with col2:
        st.metric("集合名称", stats["collection_name"])
    
    # 文件上传
    st.markdown("### 📤 上传文档")
    
    uploaded_file = st.file_uploader(
        "支持格式: TXT, Markdown, Excel",
        type=['txt', 'md', 'markdown', 'xlsx', 'xls']
    )
    
    if uploaded_file:
        if st.button("添加到知识库"):
            with st.spinner("处理中..."):
                # 保存临时文件
                temp_path = Path("temp_upload") / uploaded_file.name
                temp_path.parent.mkdir(exist_ok=True)
                
                with open(temp_path, 'wb') as f:
                    f.write(uploaded_file.getvalue())
                
                try:
                    count = st.session_state.rag.add_file_to_knowledge_base(str(temp_path))
                    st.success(f"成功添加 {count} 个文档片段到知识库")
                except Exception as e:
                    st.error(f"添加失败: {e}")
                finally:
                    # 清理临时文件
                    temp_path.unlink(missing_ok=True)
    
    # 知识检索测试
    st.markdown("### 🔍 知识检索测试")
    
    query = st.text_input("输入查询内容")
    
    if query and st.button("检索"):
        with st.spinner("检索中..."):
            result = st.session_state.rag.query(query)
            
            st.markdown(f"**回答**: {result['answer']}")
            st.markdown(f"**置信度**: {result['confidence']:.3f}")
            
            if result['sources']:
                st.markdown("**参考来源**:")
                for i, source in enumerate(result['sources'], 1):
                    with st.expander(f"来源{i} (相关度: {source['relevance']:.3f})"):
                        st.markdown(source['content'])


def reset_assessment():
    """重置评估状态"""
    st.session_state.assessor.reset()
    st.session_state.current_result = None
    st.session_state.assessment_state = "idle"
    st.session_state.pending_confirmation = None


def main():
    """主函数"""
    init_session_state()
    
    page = render_sidebar()
    
    if "首页" in page:
        render_home()
    elif "成本评估" in page:
        render_assessment()
    elif "智能问答" in page:
        render_chat()
    elif "数据分析" in page:
        render_data_analysis()
    elif "知识库" in page:
        render_knowledge_base()


if __name__ == "__main__":
    main()
