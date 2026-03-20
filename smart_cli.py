"""
智能CLI界面

集成LLM理解能力的交互式评估工具
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.llm import SmartAssessor


def print_banner():
    """打印欢迎横幅"""
    print("\n" + "="*60)
    print("  物流业务智能可行性评估系统 v0.2.0")
    print("  集成LLM智能理解能力")
    print("="*60)


def print_menu():
    """打印主菜单"""
    print("\n【主菜单】")
    print("1. 自然语言评估（直接输入描述）")
    print("2. 对话式评估（逐步引导）")
    print("3. 测试API连接")
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


def natural_language_assessment():
    """自然语言评估模式"""
    print("\n【自然语言评估模式】")
    print("请用自然语言描述业务需求，例如：")
    print('  "有一个企业客户，每天100单办公用品，送到20公里外的写字楼"')
    print('  "餐厅需要每天配送50单生鲜食材，需要冷链"')
    print("\n输入 'back' 返回主菜单")
    
    assessor = SmartAssessor()
    
    while True:
        print("\n" + "-"*60)
        user_input = input("\n请输入业务描述: ").strip()
        
        if user_input.lower() == 'back':
            break
        
        if not user_input:
            print("输入不能为空，请重新输入")
            continue
        
        print("\n正在分析...")
        
        try:
            result = assessor.assess_from_text(user_input)
            
            if result["success"]:
                print(f"\n✅ 评估成功！")
                print(f"业务类型: {result['business_type']}")
                print(f"置信度: {result['confidence']:.2%}")
                print("\n" + "="*60)
                print(result["report"])
                
                # 保存选项
                save = input("\n是否保存报告? (y/N): ").strip().lower()
                if save in ['y', 'yes', '是']:
                    filename = f"report_{result['scenario']['name'].replace(' ', '_')}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(result["report"])
                    print(f"报告已保存到: {filename}")
            else:
                print(f"\n❌ 评估失败: {result['message']}")
                
                if result.get("missing_params"):
                    print(f"\n缺失参数: {result['missing_params']}")
                    print("建议使用'对话式评估'模式，可以逐步补充信息")
                    
        except Exception as e:
            print(f"\n❌ 处理出错: {e}")


def dialogue_assessment():
    """对话式评估模式"""
    print("\n【对话式评估模式】")
    print("我将通过提问逐步了解您的业务需求")
    print("输入 'back' 返回主菜单，输入 'reset' 重新开始")
    
    assessor = SmartAssessor()
    in_dialogue = False
    
    while True:
        if not in_dialogue:
            print("\n" + "-"*60)
            user_input = input("\n请描述业务需求（或输入'back'返回）: ").strip()
            
            if user_input.lower() == 'back':
                break
            
            if not user_input:
                print("输入不能为空")
                continue
            
            print("\n正在启动对话...")
            
            try:
                result = assessor.start_dialogue_assessment(user_input)
                in_dialogue = True
            except Exception as e:
                print(f"启动对话失败: {e}")
                continue
        else:
            # 继续对话
            user_input = input("\n您的回复: ").strip()
            
            if user_input.lower() == 'back':
                break
            
            if user_input.lower() == 'reset':
                in_dialogue = False
                print("\n对话已重置")
                continue
            
            if not user_input:
                print("输入不能为空")
                continue
            
            try:
                result = assessor.continue_dialogue_assessment(user_input)
            except Exception as e:
                print(f"处理失败: {e}")
                continue
        
        # 处理结果
        if result.get("status") == "complete":
            if result.get("success"):
                print(f"\n✅ 评估完成！")
                print("\n" + "="*60)
                print(result["report"])
                
                # 保存选项
                save = input("\n是否保存报告? (y/N): ").strip().lower()
                if save in ['y', 'yes', '是']:
                    filename = f"report_{result['scenario']['name'].replace(' ', '_')}.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(result["report"])
                    print(f"报告已保存到: {filename}")
                
                in_dialogue = False
            else:
                print(f"\n❌ 评估失败: {result.get('message', '未知错误')}")
                in_dialogue = False
        else:
            # 继续询问
            print(f"\n💬 {result.get('next_question', '请提供更多信息')}")
            
            if result.get("collected_params"):
                print(f"\n已收集信息:")
                for k, v in result["collected_params"].items():
                    if v is not None and k != "extracted_entities":
                        print(f"  • {k}: {v}")


def main():
    """主函数"""
    print_banner()
    
    while True:
        print_menu()
        choice = input("\n请选择操作 (1-4): ").strip()
        
        if choice == "1":
            natural_language_assessment()
        elif choice == "2":
            dialogue_assessment()
        elif choice == "3":
            test_api_connection()
        elif choice == "4":
            print("\n感谢使用，再见！")
            break
        else:
            print("\n无效选项，请重新选择")


if __name__ == "__main__":
    main()
