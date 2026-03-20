"""
集成测试 - 验证物流成本与订单利润评估的一致性

测试场景：
1. 用户输入业务描述
2. 系统计算物流成本（各环节成本）
3. 用户询问订单可行性
4. 系统使用已计算的物流成本进行利润评估
5. 验证前后物流成本一致
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.llm import AdaptiveAssessor


def test_integration():
    """测试完整流程"""
    print("="*70)
    print("集成测试 - 物流成本与订单利润评估一致性验证")
    print("="*70)
    
    assessor = AdaptiveAssessor()
    
    # 步骤1: 用户输入业务描述
    print("\n【步骤1】用户输入业务描述")
    print("-"*70)
    
    user_input = "我们想接一个企业客户，叫ABC公司，每天100单办公用品，每单5件，重量10公斤，送到20公里外的写字楼，需要上3楼"
    print(f"用户: {user_input}")
    
    # 步骤2: 系统进行物流成本评估
    print("\n【步骤2】系统处理 - 物流成本评估")
    print("-"*70)
    
    result = assessor.assess_from_text(user_input)
    
    # 如果需要确认环节
    if result.get("needs_confirmation"):
        print("系统: 识别到需要确认成本环节")
        print(result.get("confirmation_dialog", ""))
        
        # 用户确认全部环节
        print("\n用户: 确认全部")
        result = assessor.assess_from_text("确认全部")
    
    if not result.get("success"):
        print(f"物流评估失败: {result.get('message')}")
        return
    
    # 获取物流成本结果
    cost_result = result["cost_result"]
    logistics_cost_per_order = cost_result.total_cost_per_order
    
    print(f"\n✅ 物流成本评估完成")
    print(f"   场景名称: {cost_result.scenario_name}")
    print(f"   业务类型: {cost_result.business_type}")
    print(f"   月度总成本: ¥{cost_result.total_monthly_cost:,.2f}")
    print(f"   单均物流成本: ¥{logistics_cost_per_order:.2f}")
    print(f"   日订单数: {cost_result.calculation_details.get('params', {}).get('monthly_order_count', 0) // 30}")
    
    # 显示各环节成本
    print(f"\n   成本明细:")
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
    for name, cost in cost_details.items():
        if cost > 0:
            print(f"     • {name}: ¥{cost:,.2f}")
    
    # 记录物流成本用于后续验证
    recorded_logistics_cost = logistics_cost_per_order
    
    # 步骤3: 用户询问订单可行性
    print("\n【步骤3】用户询问订单可行性")
    print("-"*70)
    
    profit_query = "这单能不能做？采购价50元，售价80元"
    print(f"用户: {profit_query}")
    
    # 步骤4: 系统进行订单利润评估
    print("\n【步骤4】系统处理 - 订单利润评估")
    print("-"*70)
    
    profit_result = assessor.assess_from_text(profit_query)
    
    # 检查是否需要收集更多信息
    if profit_result.get("needs_profit_input"):
        print(f"系统: {profit_result.get('message')}")
        
        # 用户补充信息
        user_reply = "采购价50元，售价80元，每单5件"
        print(f"\n用户: {user_reply}")
        
        profit_result = assessor.assess_from_text(user_reply)
    
    if not profit_result.get("success") and not profit_result.get("has_profit_assessment"):
        print(f"利润评估失败: {profit_result.get('message')}")
        return
    
    # 步骤5: 验证物流成本一致性
    print("\n【步骤5】验证物流成本一致性")
    print("-"*70)
    
    profit_assessment = profit_result.get("profit_assessment", {})
    costs = profit_assessment.get("costs", {})
    profit_logistics_cost = costs.get("logistics_cost", 0)
    
    print(f"\n物流成本对比:")
    print(f"   物流评估阶段单均成本: ¥{recorded_logistics_cost:.2f}")
    print(f"   利润评估阶段物流成本: ¥{profit_logistics_cost:.2f}")
    
    # 验证一致性
    if abs(recorded_logistics_cost - profit_logistics_cost) < 0.01:
        print(f"\n✅ 验证通过: 物流成本一致！")
        print(f"   差异: ¥{abs(recorded_logistics_cost - profit_logistics_cost):.4f} (可忽略)")
    else:
        print(f"\n❌ 验证失败: 物流成本不一致！")
        print(f"   差异: ¥{abs(recorded_logistics_cost - profit_logistics_cost):.2f}")
        print(f"   错误: 利润评估使用了错误的物流成本")
    
    # 显示完整的利润评估结果
    print(f"\n【订单利润评估结果】")
    print("-"*70)
    print(f"商品采购成本: ¥{costs.get('product_cost', 0):.2f}")
    print(f"物流成本: ¥{costs.get('logistics_cost', 0):.2f}")
    print(f"总成本: ¥{costs.get('total_cost', 0):.2f}")
    print(f"销售收入: ¥{profit_assessment.get('revenue', {}).get('net_revenue', 0):.2f}")
    print(f"毛利: ¥{profit_assessment.get('profit', {}).get('gross_profit', 0):.2f}")
    print(f"毛利率: {profit_assessment.get('profit', {}).get('gross_margin', 0):.1f}%")
    print(f"利润水平: {profit_assessment.get('profit', {}).get('profit_level', 'unknown')}")
    print(f"可行性: {profit_assessment.get('feasibility', 'unknown')}")
    
    # 显示详细报告
    print(f"\n【详细报告】")
    print("-"*70)
    report = assessor.get_profit_assessment_report()
    if report:
        print(report)
    
    print("\n" + "="*70)
    print("集成测试完成！")
    print("="*70)


def test_multiple_scenarios():
    """测试多个场景确保一致性"""
    print("\n\n")
    print("="*70)
    print("多场景一致性测试")
    print("="*70)
    
    test_cases = [
        {
            "name": "TOB企业购-标准场景",
            "business": "每天80单办公用品，每单3件，送到15公里外的写字楼",
            "profit_query": "采购价40元，售价65元，这单利润怎么样？"
        },
        {
            "name": "餐配业务-冷链场景",
            "business": "餐厅食材配送每天60单，需要冷链，距离20公里",
            "profit_query": "进货价100元，卖150元，能做吗？"
        },
        {
            "name": "TOB企业购-上楼场景",
            "business": "每天50单设备配件，每单2件，送到10公里外，需要上5楼",
            "profit_query": "这单能不能做？采购成本200，销售价格280"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"测试场景 {i}: {case['name']}")
        print(f"{'='*70}")
        
        assessor = AdaptiveAssessor()
        
        # 物流评估
        print(f"\n业务描述: {case['business']}")
        result = assessor.assess_from_text(case['business'])
        
        if result.get("needs_confirmation"):
            result = assessor.assess_from_text("确认全部")
        
        if not result.get("success"):
            print(f"❌ 物流评估失败: {result.get('message')}")
            continue
        
        logistics_cost = result["cost_result"].total_cost_per_order
        print(f"✅ 物流成本: ¥{logistics_cost:.2f}/单")
        
        # 利润评估
        print(f"\n利润查询: {case['profit_query']}")
        profit_result = assessor.assess_from_text(case['profit_query'])
        
        if profit_result.get("needs_profit_input"):
            # 提取价格信息再次发送
            profit_result = assessor.assess_from_text(case['profit_query'])
        
        if profit_result.get("has_profit_assessment"):
            profit_logistics = profit_result["profit_assessment"]["costs"]["logistics_cost"]
            print(f"利润评估中的物流成本: ¥{profit_logistics:.2f}")
            
            if abs(logistics_cost - profit_logistics) < 0.01:
                print(f"✅ 场景{i}验证通过: 物流成本一致")
            else:
                print(f"❌ 场景{i}验证失败: 物流成本不一致 (差异: ¥{abs(logistics_cost - profit_logistics):.2f})")
        else:
            print(f"⚠️ 场景{i}: 利润评估未完成")


if __name__ == "__main__":
    test_integration()
    test_multiple_scenarios()
