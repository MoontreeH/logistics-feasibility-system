"""
LLM模块

提供自然语言理解能力，包括：
- 意图识别
- 实体抽取
- 参数校验
- 多轮对话
- 智能评估
- 增强版评估（含成本查询、追问处理）
- 成本环节识别与确认
- 订单利润评估
"""

from .client import SiliconFlowClient
from .intent_classifier import IntentClassifier
from .entity_extractor import EntityExtractor
from .parameter_validator import ParameterValidator
from .dialogue_manager import DialogueManager
from .smart_assessor import SmartAssessor
from .enhanced_assessor import EnhancedAssessor
from .cost_link_identifier import CostLinkIdentifier, CostLinkConfirmationHandler
from .order_profit_handler import (
    OrderProfitHandler,
    OrderProfitIntentDetector,
    OrderProfitInputCollector,
    should_trigger_profit_assessment
)
from .adaptive_assessor import AdaptiveAssessor
from .adaptive_assessor_v2 import AdaptiveAssessorV2
from .smart_parameter_collector import SmartParameterCollector, ParameterStatus

__all__ = [
    "SiliconFlowClient",
    "IntentClassifier",
    "EntityExtractor",
    "ParameterValidator",
    "DialogueManager",
    "SmartAssessor",
    "EnhancedAssessor",
    "CostLinkIdentifier",
    "CostLinkConfirmationHandler",
    "OrderProfitHandler",
    "OrderProfitIntentDetector",
    "OrderProfitInputCollector",
    "should_trigger_profit_assessment",
    "AdaptiveAssessor",
    "AdaptiveAssessorV2",
    "SmartParameterCollector",
    "ParameterStatus",
]
