"""
增强版智能CLI界面

集成成本查询、追问处理、数据驱动建议等功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.llm import EnhancedAssessor


def print_banner():
    """打印欢迎横幅"""
    print("\n" + "="*70)
    print("  物流业务智能可行性评估系统 v0.3.0")
    print("  增强版 - 支持成本查询、追问分析、数据驱动建议")
    print("="*70)


def print_menu():
    """打印主菜单"""
    print("\n【主菜单】")
    print("1. 智能评估（自然语言输入）")
    print("2. 测试API连接")
    print("3. 查看知识库统计")
    print("4. 退出")


def test_api_connection():
    """测试API连接"""
    print("\n正在测试硅基流动API连接...")
    try:
        from src.llm import SiliconFlowClient
        client = SiliconFlowClient()
        
        if client.test_connection():
            print("✅ API连接成功！")
            print(f"使用模型: {client.model}")
        else:
            print("❌ API连接失败")
    except Exception as e:
        print(f"❌ 错误: {e}")


def show_knowledge_stats():
    """显示知识库统计"""
    try:
        from src.knowledge import KnowledgeBase
        kb = KnowledgeBase()
        stats = kb.get_stats()
        
        print("\n" + "="*60)
        print("【知识库统计】")
        print("="*60)
        print(f"总条目数: {stats['total_items']}")
        print(f"\n分类分布:")
        for category, count in stats['categories'].items():
            print(f"  • {category}: {count}条")
        
        print(f"\n最常用知识:")
        for item in stats['most_used']:
            print(f"  • {item.title} (使用{item.usage_count}次)")
    except Exception as e:
        print(f"获取知识库统计失败: {e}")


def interactive_assessment():
    """交互式评估（支持追问）"""
    print("\n【智能评估模式】")
    print("请用自然语言描述业务需求")
    print("输入 'back' 返回主菜单")
    print("-"*60)
    
    assessor = EnhancedAssessor()
    
    # 第一步：获取业务描述
    user_input = input("\n请输入业务描述: ").strip()
    
    if user_input.lower() == 'back':
        return
    
    if not user_input:
        print("输入不能为空")
        return
    
    print("\n正在分析...")
    
    try:
        result = assessor.assess_from_text(user_input)
        
        if result["success"]:
            print(result["report"])
            
            # 进入追问模式
            if result.get("can_ask_follow_up"):
                interactive_follow_up(assessor)
        else:
            print(f"\n❌ 评估失败: {result['message']}")
            if result.get("missing_params"):
                print(f"缺失参数: {result['missing_params']}")
    
    except Exception as e:
        print(f"\n❌ 处理出错: {e}")
        import traceback
        traceback.print_exc()


def interactive_follow_up(assessor: EnhancedAssessor):
    """交互式追问模式"""
    print("\n" + "="*60)
    print("【追问模式】")
    print("您可以询问具体环节成本、假设分析等问题")
    print("输入 'back' 返回主菜单，输入 'save' 保存报告")
    print("-"*60)
    
    while True:
        question = input("\n您的问题: ").strip()
        
        if question.lower() == 'back':
            break
        
        if question.lower() == 'save':
            save_report(assessor)
            continue
        
        if not question:
            print("请输入问题")
            continue
        
        print("\n正在分析...")
        
        try:
            response = assessor.handle_follow_up(question)
            
            if response["success"]:
                print(f"\n{response['answer']}")
            else:
                print(f"\n❌ {response.get('message', '无法回答')}")
        
        except Exception as e:
            print(f"\n❌ 处理出错: {e}")


def save_report(assessor: EnhancedAssessor):
    """保存评估报告"""
    try:
        if not assessor.current_result:
            print("没有可保存的评估结果")
            return
        
        filename = f"report_{assessor.current_result.scenario_name.replace(' ', '_')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            # 重新生成完整报告
            from src.knowledge import SuggestionEngine, KnowledgeBase
            
            suggestions = SuggestionEngine().generate_suggestions(
                assessor.current_result,
                assessor.current_params
            )
            
            relevant_knowledge = KnowledgeBase().get_relevant_knowledge(
                assessor.current_result.business_type,
                assessor.current_result.cost_structure
            )
            
            # 这里简化处理，实际应该调用完整的报告生成
            f.write(f"评估报告: {assessor.current_result.scenario_name}\n")
            f.write(f"月度总成本: ¥{assessor.current_result.total_monthly_cost:,.2f}\n")
            f.write(f"单均成本: ¥{assessor.current_result.total_cost_per_order:.2f}\n")
        
        print(f"✅ 报告已保存到: {filename}")
    
    except Exception as e:
        print(f"保存失败: {e}")


def main():
    """主函数"""
    print_banner()
    
    while True:
        print_menu()
        choice = input("\n请选择操作 (1-4): ").strip()
        
        if choice == "1":
            interactive_assessment()
        elif choice == "2":
            test_api_connection()
        elif choice == "3":
            show_knowledge_stats()
        elif choice == "4":
            print("\n感谢使用，再见！")
            break
        else:
            print("\n无效选项，请重新选择")


if __name__ == "__main__":
    main()
