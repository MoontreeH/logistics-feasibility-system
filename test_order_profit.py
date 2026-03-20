"""
测试订单利润评估功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.models import OrderProfitAssessment, OrderProfitAssessmentInput, ProductCostInfo, SalesRevenueInfo
from src.llm import OrderProfitHandler, OrderProfitIntentDetector


def test_order_profit_model():
    """测试订单利润评估模型"""
    print("="*60)
    print("测试订单利润评估模型")
    print("="*60)
    
    # 测试1: 正常盈利情况
    print("\n【测试1】正常盈利情况")
    assessment1 = OrderProfitAssessment(
        scenario_name="办公用品订单",
        product_cost=ProductCostInfo(
            purchase_price_per_unit=50,
            purchase_quantity_per_order=5
        ),
        logistics_cost_per_order=33.79,
        sales_revenue=SalesRevenueInfo(
            selling_price_per_unit=80,
            sales_quantity_per_order=5
        )
    )
    assessment1.calculate()
    
    print(f"商品采购成本: ¥{assessment1.product_cost.total_purchase_cost_per_order:.2f}")
    print(f"物流成本: ¥{assessment1.logistics_cost_per_order:.2f}")
    print(f"总成本: ¥{assessment1.total_cost_per_order:.2f}")
    print(f"销售收入: ¥{assessment1.revenue_per_order:.2f}")
    print(f"毛利: ¥{assessment1.gross_profit_per_order:.2f}")
    print(f"毛利率: {assessment1.gross_profit_margin:.1%}")
    print(f"利润水平: {assessment1.profit_level.value}")
    print(f"可行性: {assessment1.feasibility.value}")
    
    # 测试2: 亏损情况
    print("\n【测试2】亏损情况")
    assessment2 = OrderProfitAssessment(
        scenario_name="低利润订单",
        product_cost=ProductCostInfo(
            purchase_price_per_unit=90,
            purchase_quantity_per_order=1
        ),
        logistics_cost_per_order=50,
        sales_revenue=SalesRevenueInfo(
            selling_price_per_unit=100,
            sales_quantity_per_order=1
        )
    )
    assessment2.calculate()
    
    print(f"商品采购成本: ¥{assessment2.product_cost.total_purchase_cost_per_order:.2f}")
    print(f"物流成本: ¥{assessment2.logistics_cost_per_order:.2f}")
    print(f"总成本: ¥{assessment2.total_cost_per_order:.2f}")
    print(f"销售收入: ¥{assessment2.revenue_per_order:.2f}")
    print(f"毛利: ¥{assessment2.gross_profit_per_order:.2f}")
    print(f"毛利率: {assessment2.gross_profit_margin:.1%}")
    print(f"利润水平: {assessment2.profit_level.value}")
    print(f"可行性: {assessment2.feasibility.value}")
    
    # 测试3: 高利润情况
    print("\n【测试3】高利润情况")
    assessment3 = OrderProfitAssessment(
        scenario_name="高利润订单",
        product_cost=ProductCostInfo(
            purchase_price_per_unit=30,
            purchase_quantity_per_order=10
        ),
        logistics_cost_per_order=25,
        sales_revenue=SalesRevenueInfo(
            selling_price_per_unit=60,
            sales_quantity_per_order=10
        )
    )
    assessment3.calculate()
    
    print(f"商品采购成本: ¥{assessment3.product_cost.total_purchase_cost_per_order:.2f}")
    print(f"物流成本: ¥{assessment3.logistics_cost_per_order:.2f}")
    print(f"总成本: ¥{assessment3.total_cost_per_order:.2f}")
    print(f"销售收入: ¥{assessment3.revenue_per_order:.2f}")
    print(f"毛利: ¥{assessment3.gross_profit_per_order:.2f}")
    print(f"毛利率: {assessment3.gross_profit_margin:.1%}")
    print(f"利润水平: {assessment3.profit_level.value}")
    print(f"可行性: {assessment3.feasibility.value}")
    
    print("\n" + "="*60)
    print("模型测试完成！")
    print("="*60)


def test_intent_detection():
    """测试意图检测"""
    print("\n" + "="*60)
    print("测试意图检测")
    print("="*60)
    
    test_inputs = [
        "这单能不能做？",
        "采购价50元，卖80元",
        "利润怎么样？",
        "这个报价划算吗？",
        "能赚多少钱？",
        "值得接这个订单吗？",
        "普通业务咨询",
        "帮我计算一下成本",
    ]
    
    for text in test_inputs:
        intent = OrderProfitIntentDetector.detect_profit_intent(text)
        print(f"\n输入: {text}")
        print(f"  利润意图: {'是' if intent['has_profit_intent'] else '否'}")
        print(f"  置信度: {intent['confidence']}")
        print(f"  提取价格: {intent['extracted_prices']}")


def test_handler():
    """测试处理器"""
    print("\n" + "="*60)
    print("测试订单利润处理器")
    print("="*60)
    
    handler = OrderProfitHandler()
    
    # 模拟物流成本
    logistics_cost = 33.79
    
    # 开始评估
    print("\n【开始评估】")
    result = handler.start_assessment(logistics_cost)
    print(f"系统: {result['message']}")
    
    # 用户回复（包含价格信息）
    print("\n【用户回复】")
    user_input = "采购价50元，售价80元，每单5件"
    print(f"用户: {user_input}")
    
    result = handler.process_input(user_input)
    
    if result['status'] == 'completed':
        print("\n【评估结果】")
        print(result['message'])
    else:
        print(f"\n系统: {result['message']}")
    
    print("\n" + "="*60)
    print("处理器测试完成！")
    print("="*60)


def test_input_collector():
    """测试输入收集器"""
    print("\n" + "="*60)
    print("测试输入收集器")
    print("="*60)
    
    from src.llm import OrderProfitInputCollector
    
    collector = OrderProfitInputCollector()
    
    test_cases = [
        "办公用品采购价50元，售价80元，每单5件",
        "商品名称：打印纸，采购单价25元，销售单价40元",
        "进货价100，卖150",
        "这单采购成本200元，可以卖280元",
    ]
    
    for text in test_cases:
        print(f"\n输入: {text}")
        result = collector.extract_from_text(text)
        print(f"提取结果: {result['extracted']}")
        print(f"缺失字段: {result['missing_fields']}")
        print(f"是否完整: {result['is_complete']}")
        
        # 重置收集器
        collector = OrderProfitInputCollector()


if __name__ == "__main__":
    test_order_profit_model()
    test_intent_detection()
    test_handler()
    test_input_collector()
