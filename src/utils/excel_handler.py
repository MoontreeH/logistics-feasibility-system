"""
Excel处理模块

支持Excel导入和导出
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models import BusinessScenario, BusinessType, DeliveryRequirement


class ExcelHandler:
    """
    Excel处理器
    
    处理Excel文件的导入和导出
    """
    
    # 导入模板列名
    IMPORT_COLUMNS = [
        "客户名称",
        "业务类型",  # TOB企业购 / 餐配业务
        "日订单数",
        "平均每单行数",
        "平均每单件数",
        "平均每单重量(kg)",
        "配送距离(km)",
        "配送点数",
        "是否需要上楼",
        "配送楼层",
        "是否有电梯",
        "是否需要冷链",
        "是否需要加工",
        "预期退货率",
        "备注"
    ]
    
    @classmethod
    def create_import_template(cls, output_path: str):
        """
        创建导入模板
        
        Args:
            output_path: 输出路径
        """
        # 示例数据
        sample_data = {
            "客户名称": ["ABC科技公司", "某连锁餐厅"],
            "业务类型": ["TOB企业购", "餐配业务"],
            "日订单数": [100, 50],
            "平均每单行数": [5, 10],
            "平均每单件数": [5, 20],
            "平均每单重量(kg)": [10.0, 30.0],
            "配送距离(km)": [20.0, 15.0],
            "配送点数": [1, 5],
            "是否需要上楼": ["是", "否"],
            "配送楼层": [3, 1],
            "是否有电梯": ["是", "是"],
            "是否需要冷链": ["否", "是"],
            "是否需要加工": ["否", "是"],
            "预期退货率": [0.01, 0.05],
            "备注": ["办公用品配送", "生鲜食材配送"]
        }
        
        df = pd.DataFrame(sample_data)
        
        # 添加说明sheet
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='导入模板', index=False)
            
            # 说明sheet
            instructions = pd.DataFrame({
                '字段名': cls.IMPORT_COLUMNS,
                '说明': [
                    '客户或场景名称',
                    'TOB企业购 或 餐配业务',
                    '每天的订单数量',
                    '平均每单有多少行商品',
                    '平均每单有多少件商品',
                    '平均每单的重量（公斤）',
                    '配送距离（公里）',
                    '每天配送的点位数量',
                    '是/否',
                    '配送楼层（1-100）',
                    '是/否',
                    '是/否（餐配业务默认是）',
                    '是/否（餐配业务可能需要）',
                    '0-1之间的小数，如0.05表示5%',
                    '其他说明信息'
                ],
                '示例': [
                    'ABC公司',
                    'TOB企业购',
                    '100',
                    '5',
                    '5',
                    '10',
                    '20',
                    '1',
                    '是',
                    '3',
                    '是',
                    '否',
                    '否',
                    '0.01',
                    '办公用品'
                ]
            })
            instructions.to_excel(writer, sheet_name='填写说明', index=False)
        
        return output_path
    
    @classmethod
    def import_from_excel(cls, file_path: str) -> List[Dict[str, Any]]:
        """
        从Excel导入业务场景
        
        Args:
            file_path: Excel文件路径
        
        Returns:
            业务场景参数列表
        """
        df = pd.read_excel(file_path, sheet_name='导入模板')
        
        scenarios = []
        
        for _, row in df.iterrows():
            try:
                # 解析业务类型
                business_type_str = str(row.get('业务类型', '')).lower()
                if 'tob' in business_type_str or '企业' in business_type_str:
                    business_type = BusinessType.TOB_ENTERPRISE
                else:
                    business_type = BusinessType.MEAL_DELIVERY
                
                # 解析布尔值
                need_upstairs = str(row.get('是否需要上楼', '否')).lower() in ['是', 'yes', 'true']
                has_elevator = str(row.get('是否有电梯', '是')).lower() in ['是', 'yes', 'true']
                need_cold_chain = str(row.get('是否需要冷链', '否')).lower() in ['是', 'yes', 'true']
                need_processing = str(row.get('是否需要加工', '否')).lower() in ['是', 'yes', 'true']
                
                # 构建场景参数
                scenario_params = {
                    'business_type': business_type,
                    'scenario_name': str(row.get('客户名称', '未命名')),
                    'daily_order_count': int(row.get('日订单数', 10)),
                    'avg_order_lines': int(row.get('平均每单行数', 5)),
                    'avg_items_per_order': int(row.get('平均每单件数', 5)),
                    'avg_weight_kg': float(row.get('平均每单重量(kg)', 5.0)),
                    'delivery_distance_km': float(row.get('配送距离(km)', 10.0)),
                    'delivery_points': int(row.get('配送点数', 1)),
                    'delivery_requirement': DeliveryRequirement(
                        need_upstairs=need_upstairs,
                        floor=int(row.get('配送楼层', 1)),
                        has_elevator=has_elevator
                    ),
                    'need_cold_chain': need_cold_chain,
                    'need_processing': need_processing,
                    'expected_return_rate': float(row.get('预期退货率', 0.01)),
                    'remark': str(row.get('备注', ''))
                }
                
                scenarios.append(scenario_params)
            
            except Exception as e:
                print(f"解析第{_+1}行时出错: {e}")
                continue
        
        return scenarios
    
    @classmethod
    def export_report_to_excel(
        cls,
        results: List[Dict[str, Any]],
        output_path: str
    ):
        """
        导出评估报告到Excel
        
        Args:
            results: 评估结果列表
            output_path: 输出路径
        """
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 1. 汇总sheet
            summary_data = []
            for result in results:
                if result.get('success'):
                    cost_result = result['cost_result']
                    summary_data.append({
                        '场景名称': cost_result.scenario_name,
                        '业务类型': cost_result.business_type,
                        '月度总成本': cost_result.total_monthly_cost,
                        '单均成本': cost_result.total_cost_per_order,
                        '单件成本': cost_result.total_cost_per_item,
                        '可行性评级': cost_result.feasibility_rating.value,
                        '日订单数': result['scenario']['daily_orders'],
                        '配送距离': result['scenario']['distance_km']
                    })
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='评估汇总', index=False)
            
            # 2. 成本明细sheet
            detail_data = []
            for result in results:
                if result.get('success'):
                    cost_result = result['cost_result']
                    breakdown = cost_result.breakdown
                    
                    detail_data.append({
                        '场景名称': cost_result.scenario_name,
                        '订单处理': breakdown.order_processing,
                        '库存持有': breakdown.inventory_holding,
                        '拣选作业': breakdown.picking,
                        '包装加工': breakdown.packaging + breakdown.processing,
                        '集货装车': breakdown.loading,
                        '运输配送': breakdown.transportation,
                        '末端交付': breakdown.delivery,
                        '逆向处理': breakdown.reverse_logistics,
                        '管理分摊': breakdown.overhead,
                        '月度总成本': cost_result.total_monthly_cost
                    })
            
            df_detail = pd.DataFrame(detail_data)
            df_detail.to_excel(writer, sheet_name='成本明细', index=False)
            
            # 3. 建议sheet
            suggestions_data = []
            for result in results:
                if result.get('success') and result.get('suggestions'):
                    for i, sug in enumerate(result['suggestions'], 1):
                        suggestions_data.append({
                            '场景名称': result['cost_result'].scenario_name,
                            '建议序号': i,
                            '建议标题': sug.title,
                            '类别': sug.category,
                            '问题描述': sug.description,
                            '预期节省金额': sug.potential_savings,
                            '预期节省比例': f"{sug.savings_percentage:.1f}%",
                            '实施难度': sug.implementation_difficulty,
                            '优先级': sug.priority,
                            '数据支持': sug.data_support
                        })
            
            if suggestions_data:
                df_suggestions = pd.DataFrame(suggestions_data)
                df_suggestions.to_excel(writer, sheet_name='优化建议', index=False)


if __name__ == "__main__":
    # 测试Excel处理
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    print("="*60)
    print("Excel处理测试")
    print("="*60)
    
    # 创建模板
    template_path = "import_template.xlsx"
    ExcelHandler.create_import_template(template_path)
    print(f"✅ 已创建导入模板: {template_path}")
    
    # 测试导入
    scenarios = ExcelHandler.import_from_excel(template_path)
    print(f"✅ 成功导入 {len(scenarios)} 个场景")
    
    for scenario in scenarios:
        print(f"  - {scenario['scenario_name']} ({scenario['business_type'].value})")
