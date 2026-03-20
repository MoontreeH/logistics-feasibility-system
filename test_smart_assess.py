"""
智能评估功能测试
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.llm import SmartAssessor


def test_intent_classification():
    """测试意图识别"""
    print("\n" + "="*60)
    print("测试1: 意图识别")
    print("="*60)
    
    from src.llm import IntentClassifier
    
    classifier = IntentClassifier()
    
    test_cases = [
        ("我们想接一个企业客户，每天100单办公用品，送到写字楼", "tob_enterprise"),
        ("有个餐厅需要每天配送生鲜食材，需要冷链", "meal_delivery"),
        ("学校食堂需要配送蔬菜和肉类", "meal_delivery"),
        ("某科技公司采购办公耗材", "tob_enterprise"),
    ]
    
    for test_input, expected in test_cases:
        result = classifier.classify_with_fallback(test_input)
        status = "✅" if result[0] == expected else "❌"
        print(f"\n{status} 输入: {test_input}")
        print(f"   结果: {result[0]} (置信度: {result[1]:.2f})")
        print(f"   理由: {result[2]}")


def test_entity_extraction():
    """测试实体抽取"""
    print("\n" + "="*60)
    print("测试2: 实体抽取")
    print("="*60)
    
    from src.llm import EntityExtractor
    
    extractor = EntityExtractor()
    
    test_input = "我们想接一个企业客户，叫ABC公司，每天100单办公用品，每单大概5件，重量10公斤，送到20公里外的写字楼，需要上3楼"
    
    print(f"\n输入: {test_input}")
    
    result = extractor.extract(test_input, "tob_enterprise")
    
    print("\n抽取结果:")
    for key, value in result.items():
        if key != "extracted_entities":
            print(f"  • {key}: {value}")
    
    missing = extractor.get_missing_params(result)
    if missing:
        print(f"\n缺失参数: {missing}")
    else:
        print("\n✅ 参数完整")


def test_full_assessment():
    """测试完整评估流程"""
    print("\n" + "="*60)
    print("测试3: 完整评估流程")
    print("="*60)
    
    assessor = SmartAssessor()
    
    test_cases = [
        "我们想接一个企业客户，叫ABC公司，每天100单办公用品，每单5件，重量10公斤，送到20公里外的写字楼，需要上3楼",
        "有个餐厅需要每天配送50单生鲜食材，每单20件，30公斤，距离15公里，需要冷链",
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n案例 {i}:")
        print(f"输入: {test_input}")
        print("-"*60)
        
        result = assessor.assess_from_text(test_input)
        
        if result["success"]:
            print(f"✅ 评估成功")
            print(f"业务类型: {result['business_type']}")
            print(f"置信度: {result['confidence']:.2%}")
            print(f"月度总成本: ¥{result['cost_result'].total_monthly_cost:,.2f}")
            print(f"单均成本: ¥{result['cost_result'].total_cost_per_order:,.2f}")
        else:
            print(f"❌ 评估失败: {result['message']}")
            if result.get("missing_params"):
                print(f"缺失参数: {result['missing_params']}")


def test_dialogue_mode():
    """测试对话模式"""
    print("\n" + "="*60)
    print("测试4: 对话模式")
    print("="*60)
    
    assessor = SmartAssessor()
    
    # 第一轮：部分信息
    print("\n用户: 我们想接一个企业客户，每天大概100单")
    result1 = assessor.start_dialogue_assessment("我们想接一个企业客户，每天大概100单")
    
    print(f"业务类型: {result1['business_type']}")
    print(f"状态: {result1['status']}")
    
    if result1['status'] == 'incomplete':
        print(f"下一个问题: {result1['next_question']}")
        
        # 第二轮：补充信息
        print("\n用户: 每单大概5件，重量10公斤")
        result2 = assessor.continue_dialogue_assessment("每单大概5件，重量10公斤")
        
        print(f"状态: {result2['status']}")
        if result2['status'] == 'incomplete':
            print(f"下一个问题: {result2['next_question']}")
            
            # 第三轮：完成信息
            print("\n用户: 配送距离20公里")
            result3 = assessor.continue_dialogue_assessment("配送距离20公里")
            
            print(f"状态: {result3['status']}")
            if result3['status'] == 'complete':
                print(f"✅ 对话完成！")
                print(f"月度总成本: ¥{result3['cost_result'].total_monthly_cost:,.2f}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("智能评估功能测试套件")
    print("="*60)
    
    try:
        test_intent_classification()
    except Exception as e:
        print(f"\n❌ 意图识别测试失败: {e}")
    
    try:
        test_entity_extraction()
    except Exception as e:
        print(f"\n❌ 实体抽取测试失败: {e}")
    
    try:
        test_full_assessment()
    except Exception as e:
        print(f"\n❌ 完整评估测试失败: {e}")
    
    try:
        test_dialogue_mode()
    except Exception as e:
        print(f"\n❌ 对话模式测试失败: {e}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
