"""
CoreThink-MCP Elicitation型定義
FastMCP標準のElicitationパターンで使用するデータクラス
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class RefinementData:
    """曖昧性解消のための追加情報要求データ"""
    context_clues: str
    domain_hints: str  # 医療、法律、技術等の専門分野
    specific_requirements: str  # 具体的な要件や制約
    priority_level: str = "normal"  # high, normal, low


@dataclass
class ReasoningContext:
    """推論処理のための追加コンテキスト要求データ"""
    background_information: str
    constraints_preference: str  # strict, balanced, flexible
    risk_tolerance: str  # low, medium, high
    expected_outcome: str


@dataclass
class ValidationParams:
    """制約検証のための詳細パラメータ要求データ"""
    validation_scope: str  # full, targeted, minimal
    compliance_level: str  # must, should, may
    special_considerations: str  # 特別な考慮事項
    stakeholder_concerns: str  # ステークホルダーの懸念


@dataclass
class ExecutionPreferences:
    """実行時設定のためのユーザー設定要求データ"""
    safety_level: str  # maximum, high, standard, minimal
    rollback_strategy: str  # auto, manual, none
    notification_level: str  # verbose, standard, minimal
    execution_timing: str  # immediate, scheduled, on_demand


@dataclass
class TracingPreferences:
    """推論トレース設定のためのユーザー設定要求データ"""
    detail_level: str  # minimal, standard, detailed, exhaustive
    output_format: str  # natural, structured, technical
    include_metadata: bool = True
    real_time_updates: bool = False
