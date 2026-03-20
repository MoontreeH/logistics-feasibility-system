"""
测试选择性成本计算功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.models import CostLinkConfig, CostParameters, InventoryConfig, TransportationConfig
from src.cost_engine import SelectiveCostCalculator, calculate_with_link_config


def test_selective_calculation():
    """测试选择性计算"""
    print("="*60)
    print("测试选择性成本计算功能")
    print("="*60)
    
    # 创建基础成本参数
    params = CostParameters(
        monthly_order_count=3000,
        monthly_order_lines=15000,
        monthly_items=15000,
        monthly_packages=3000,
        monthly_distance_km=600,
        monthly_delivery_points=30,
        monthly_loading_hours=150,
        inventory_config=InventoryConfig(
            avg_inventory_amount=10000,
            warehouse_area_sqm=10,
            storage_days=7
        ),
        transportation_config=TransportationConfig(
            use_own_vehicle=True,
            vehicle_type="normal"
        )
    )
    
    calculator = SelectiveCostCalculator()
    
    # 测试1: 计算所有环节
    print("\n【测试1】计算所有环节")
    config_all = CostLinkConfig.create_for_business_type("tob_enterprise")
    # 将所有环节设为可用
    for link in config_all.get_all_links():
        link.data_status = "available"
        link.is_active = True
    
    result_all = calculator.calculate(params, "tob_enterprise", "全环节计算", config_all)
    print(f"月度总成本: ¥{result_all.total_monthly_cost:,.2f}")
    print(f"单均成本: ¥{result_all.total_cost_per_order:.2f}")
    print(f"计算环节数: {len(result_all.calculation_details.get('calculated_links', []))}")
    print(f"跳过环节数: {len(result_all.calculation_details.get('skipped_links', []))}")
    
    # 测试2: 只计算部分环节
    print("\n【测试2】只计算部分环节（排除库存持有和逆向处理）")
    config_partial = CostLinkConfig.create_for_business_type("tob_enterprise")
    config_partial.inventory_holding.is_active = False
    config_partial.inventory_holding.data_status = "not_applicable"
    config_partial.reverse_logistics.is_active = False
    config_partial.reverse_logistics.data_status = "not_applicable"
    # 其他环节设为可用
    for link in config_partial.get_all_links():
        if link.is_active:
            link.data_status = "available"
    
    result_partial = calculator.calculate(params, "tob_enterprise", "部分环节计算", config_partial)
    print(f"月度总成本: ¥{result_partial.total_monthly_cost:,.2f}")
    print(f"单均成本: ¥{result_partial.total_cost_per_order:.2f}")
    print(f"计算环节: {', '.join(result_partial.calculation_details.get('calculated_links', []))}")
    print(f"跳过环节: {', '.join(result_partial.calculation_details.get('skipped_links', []))}")
    
    # 验证成本差异
    cost_diff = result_all.total_monthly_cost - result_partial.total_monthly_cost
    print(f"\n成本差异: ¥{cost_diff:,.2f} (全环节 - 部分环节)")
    
    # 测试3: 添加自定义环节
    print("\n【测试3】添加自定义环节")
    config_custom = CostLinkConfig.create_for_business_type("tob_enterprise")
    for link in config_custom.get_all_links():
        link.data_status = "available"
    
    # 添加自定义环节
    custom_link = config_custom.add_custom_link(
        name="特殊包装",
        description="客户要求的特殊包装材料",
        rate=5.0,
        unit="单"
    )
    
    result_custom = calculator.calculate(params, "tob_enterprise", "含自定义环节", config_custom)
    print(f"月度总成本: ¥{result_custom.total_monthly_cost:,.2f}")
    print(f"自定义环节成本: {result_custom.calculation_details.get('custom_costs', {})}")
    
    # 测试4: 环节配置摘要
    print("\n【测试4】环节配置摘要")
    print(config_custom.get_confirmation_summary())
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


def test_cost_link_config():
    """测试成本环节配置"""
    print("\n" + "="*60)
    print("测试成本环节配置功能")
    print("="*60)
    
    # 创建TOB配置
    print("\n【TOB企业购默认配置】")
    config_tob = CostLinkConfig.create_for_business_type("tob_enterprise")
    print(f"总环节数: {len(config_tob.get_all_links())}")
    print(f"启用环节数: {len(config_tob.get_active_links())}")
    print(f"加工环节状态: {'启用' if config_tob.processing.is_active else '禁用'}")
    
    # 创建餐配配置
    print("\n【餐配业务默认配置】")
    config_meal = CostLinkConfig.create_for_business_type("meal_delivery")
    print(f"总环节数: {len(config_meal.get_all_links())}")
    print(f"启用环节数: {len(config_meal.get_active_links())}")
    print(f"加工环节状态: {'启用' if config_meal.processing.is_active else '禁用'}")
    
    # 测试环节状态管理
    print("\n【环节状态管理】")
    config_tob.set_link_status("运输配送", False, "not_applicable")
    print("禁用运输配送环节后:")
    print(f"  启用环节数: {len(config_tob.get_active_links())}")
    
    # 测试自定义环节
    print("\n【自定义环节管理】")
    custom = config_tob.add_custom_link(
        name="保险费",
        description="货物运输保险",
        rate=0.5,
        unit="单"
    )
    print(f"添加自定义环节: {custom.name}")
    print(f"自定义环节数: {len(config_tob.custom_links)}")
    print(f"总环节数: {len(config_tob.get_all_links())}")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)


if __name__ == "__main__":
    test_cost_link_config()
    test_selective_calculation()
