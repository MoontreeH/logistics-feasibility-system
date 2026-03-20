"""
快速演示脚本 - 无需交互
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.models import BusinessScenario, BusinessType, DeliveryRequirement, CostParameters
from src.cost_engine import CostCalculator


def demo_tob():
    """TOB企业购示例"""
    print("\n" + "="*60)
    print("示例1: TOB企业购 - 办公用品配送")
    print("="*60)
    
    scenario = BusinessScenario(
        business_type=BusinessType.TOB_ENTERPRISE,
        scenario_name="某科技公司办公用品配送",
        daily_order_count=20,
        avg_order_lines=8,
        avg_items_per_order=15,
        avg_weight_kg=25.0,
        delivery_distance_km=25.0,
        delivery_points=5,
        delivery_requirement=DeliveryRequirement(
            need_upstairs=True,
            floor=3,
            has_elevator=True,
            waiting_time_hours=0.5
        ),
        need_cold_chain=False,
        expected_return_rate=0.01,
        inventory_amount=50000,
        warehouse_area_sqm=50,
        storage_days=5,
        remark="TOB企业购示例"
    )
    
    print(f"场景: {scenario.scenario_name}")
    print(f"日订单数: {scenario.daily_order_count}单")
    print(f"配送距离: {scenario.delivery_distance_km}公里")
    print(f"需要上楼: {'是' if scenario.delivery_requirement.need_upstairs else '否'}")
    
    # 计算成本
    params = CostParameters.from_scenario(scenario)
    calculator = CostCalculator()
    result = calculator.calculate(
        params=params,
        business_type=scenario.business_type.value,
        scenario_name=scenario.scenario_name
    )
    
    print("\n" + result.to_report())


def demo_meal():
    """餐配业务示例"""
    print("\n" + "="*60)
    print("示例2: 餐配业务 - 餐厅食材配送")
    print("="*60)
    
    scenario = BusinessScenario(
        business_type=BusinessType.MEAL_DELIVERY,
        scenario_name="某连锁餐厅食材配送",
        daily_order_count=50,
        avg_order_lines=12,
        avg_items_per_order=20,
        avg_weight_kg=30.0,
        delivery_distance_km=15.0,
        delivery_points=10,
        delivery_requirement=DeliveryRequirement(
            need_upstairs=False,
            floor=1,
            has_elevator=True,
            waiting_time_hours=0.25
        ),
        need_cold_chain=True,
        cold_chain_type="refrigerated",
        need_processing=True,
        processing_weight_kg=10.0,
        expected_return_rate=0.05,
        inventory_amount=30000,
        warehouse_area_sqm=30,
        storage_days=3,
        remark="餐配业务示例"
    )
    
    print(f"场景: {scenario.scenario_name}")
    print(f"日订单数: {scenario.daily_order_count}单")
    print(f"配送距离: {scenario.delivery_distance_km}公里")
    print(f"需要冷链: {'是' if scenario.need_cold_chain else '否'}")
    print(f"需要加工: {'是' if scenario.need_processing else '否'}")
    
    # 计算成本
    params = CostParameters.from_scenario(scenario)
    calculator = CostCalculator()
    result = calculator.calculate(
        params=params,
        business_type=scenario.business_type.value,
        scenario_name=scenario.scenario_name
    )
    
    print("\n" + result.to_report())


if __name__ == "__main__":
    print("\n" + "="*60)
    print("物流业务智能可行性评估系统 - 快速演示")
    print("="*60)
    
    demo_tob()
    demo_meal()
    
    print("\n" + "="*60)
    print("演示完成！")
    print("="*60)
