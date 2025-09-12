#!/usr/bin/env python3
"""
CoreThink-MCP 推論ログ記録システム
人間による後検証可能な詳細ログの生成
将来のVuestic Adminダッシュボード対応を考慮した設計
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid

logger = logging.getLogger(__name__)

@dataclass
class ReasoningStep:
    """個別推論ステップの記録"""
    step_id: str
    step_name: str
    layer: str  # Layer 1-4 or "preparation", "conclusion"
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    transformation_rule: str
    timestamp: str
    execution_time_ms: float
    confidence_level: str
    notes: Optional[str] = None

@dataclass
class ReasoningSession:
    """推論セッション全体の記録"""
    session_id: str
    start_time: str
    end_time: str
    total_execution_time_ms: float
    
    # 入力情報
    situation_description: str
    required_judgment: str
    context_depth: str
    reasoning_mode: str
    
    # 推論過程
    reasoning_steps: List[ReasoningStep]
    collected_materials: Dict[str, str]
    applied_constraints: List[str]
    
    # 結果
    final_judgment: str
    final_confidence: str
    alternative_paths: List[str]
    
    # メタデータ
    gsr_version: str = "Phase3-v1.0.0"
    core_think_compliance: bool = True

class ReasoningLogger:
    """推論過程の詳細ログ記録システム"""
    
    def __init__(self, base_path: str = "logs/reasoning"):
        self.base_path = Path(base_path)
        self.current_session: Optional[ReasoningSession] = None
        self.current_steps: List[ReasoningStep] = []
        
    def start_session(
        self,
        situation_description: str,
        required_judgment: str,
        context_depth: str,
        reasoning_mode: str
    ) -> str:
        """新しい推論セッションを開始"""
        session_id = f"reasoning_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        self.current_session = ReasoningSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            end_time="",
            total_execution_time_ms=0.0,
            situation_description=situation_description,
            required_judgment=required_judgment,
            context_depth=context_depth,
            reasoning_mode=reasoning_mode,
            reasoning_steps=[],
            collected_materials={},
            applied_constraints=[],
            final_judgment="",
            final_confidence="",
            alternative_paths=[]
        )
        
        self.current_steps = []
        logger.info(f"推論セッション開始: {session_id}")
        return session_id
    
    def log_step(
        self,
        step_name: str,
        layer: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        transformation_rule: str,
        execution_time_ms: float,
        confidence_level: str = "MEDIUM",
        notes: Optional[str] = None
    ) -> str:
        """個別推論ステップを記録"""
        if not self.current_session:
            raise ValueError("セッションが開始されていません")
            
        step_id = f"step_{len(self.current_steps) + 1:03d}"
        
        step = ReasoningStep(
            step_id=step_id,
            step_name=step_name,
            layer=layer,
            input_data=input_data,
            output_data=output_data,
            transformation_rule=transformation_rule,
            timestamp=datetime.now().isoformat(),
            execution_time_ms=execution_time_ms,
            confidence_level=confidence_level,
            notes=notes
        )
        
        self.current_steps.append(step)
        logger.debug(f"推論ステップ記録: {step_id} - {step_name}")
        return step_id
    
    def log_materials(self, materials: Dict[str, str]):
        """収集された推論材料を記録"""
        if self.current_session:
            self.current_session.collected_materials.update(materials)
    
    def log_constraints(self, constraints: List[str]):
        """適用された制約を記録"""
        if self.current_session:
            self.current_session.applied_constraints.extend(constraints)
    
    def end_session(
        self,
        final_judgment: str,
        final_confidence: str,
        alternative_paths: List[str] = None
    ) -> str:
        """推論セッションを終了してログを出力"""
        if not self.current_session:
            raise ValueError("セッションが開始されていません")
            
        # セッション情報の完成
        self.current_session.end_time = datetime.now().isoformat()
        self.current_session.reasoning_steps = self.current_steps
        self.current_session.final_judgment = final_judgment
        self.current_session.final_confidence = final_confidence
        self.current_session.alternative_paths = alternative_paths or []
        
        # 実行時間の計算
        start_dt = datetime.fromisoformat(self.current_session.start_time)
        end_dt = datetime.fromisoformat(self.current_session.end_time)
        self.current_session.total_execution_time_ms = (end_dt - start_dt).total_seconds() * 1000
        
        # ログファイルの出力
        session_id = self.current_session.session_id
        self._write_detailed_log()
        self._write_summary_log()
        self._write_human_readable_log()
        
        logger.info(f"推論セッション完了: {session_id}")
        
        # セッションのクリア
        result_session_id = self.current_session.session_id
        self.current_session = None
        self.current_steps = []
        
        return result_session_id
    
    def _write_detailed_log(self):
        """詳細ログ（JSON）の出力"""
        if not self.current_session:
            return
            
        detailed_path = self.base_path / "detailed" / f"{self.current_session.session_id}.json"
        detailed_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(detailed_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self.current_session), f, ensure_ascii=False, indent=2)
    
    def _write_summary_log(self):
        """サマリーログ（JSON）の出力"""
        if not self.current_session:
            return
            
        summary_data = {
            "session_id": self.current_session.session_id,
            "timestamp": self.current_session.start_time,
            "situation": self.current_session.situation_description[:100] + "...",
            "judgment_type": self.current_session.required_judgment,
            "reasoning_mode": self.current_session.reasoning_mode,
            "total_steps": len(self.current_session.reasoning_steps),
            "execution_time_ms": self.current_session.total_execution_time_ms,
            "final_confidence": self.current_session.final_confidence,
            "gsr_layers_executed": list(set(step.layer for step in self.current_session.reasoning_steps)),
            "materials_collected": len(self.current_session.collected_materials),
            "constraints_applied": len(self.current_session.applied_constraints)
        }
        
        summary_path = self.base_path / "summary" / f"{self.current_session.session_id}_summary.json"
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
    
    def _write_human_readable_log(self):
        """人間読み取り可能ログ（Markdown）の出力"""
        if not self.current_session:
            return
            
        markdown_content = self._generate_markdown_report()
        
        markdown_path = self.base_path / "human_readable" / f"{self.current_session.session_id}.md"
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    
    def _generate_markdown_report(self) -> str:
        """Markdownレポートの生成"""
        if not self.current_session:
            return ""
            
        session = self.current_session
        
        report = f"""# CoreThink-MCP 推論セッションレポート

## セッション情報
- **セッションID**: `{session.session_id}`
- **開始時刻**: {session.start_time}
- **終了時刻**: {session.end_time}
- **実行時間**: {session.total_execution_time_ms:.2f}ms
- **GSRバージョン**: {session.gsr_version}

## 入力情報
### 状況記述
```
{session.situation_description}
```

### 推論パラメータ
- **判断種別**: {session.required_judgment}
- **コンテキスト深度**: {session.context_depth}
- **推論モード**: {session.reasoning_mode}

## 推論過程詳細

"""
        
        # 推論ステップの詳細
        current_layer = ""
        for step in session.reasoning_steps:
            if step.layer != current_layer:
                current_layer = step.layer
                report += f"\n### {current_layer}\n\n"
            
            report += f"#### ステップ {step.step_id}: {step.step_name}\n"
            report += f"- **実行時間**: {step.execution_time_ms:.2f}ms\n"
            report += f"- **信頼度**: {step.confidence_level}\n"
            report += f"- **変換規則**: {step.transformation_rule}\n"
            
            if step.notes:
                report += f"- **備考**: {step.notes}\n"
            
            report += "\n**入力データ**:\n```json\n"
            report += json.dumps(step.input_data, ensure_ascii=False, indent=2)
            report += "\n```\n\n**出力データ**:\n```json\n"
            report += json.dumps(step.output_data, ensure_ascii=False, indent=2)
            report += "\n```\n\n---\n\n"
        
        # 収集材料
        if session.collected_materials:
            report += "## 収集された推論材料\n\n"
            for material_type, content in session.collected_materials.items():
                report += f"### {material_type}\n"
                report += f"```\n{content[:500]}{'...' if len(content) > 500 else ''}\n```\n\n"
        
        # 適用制約
        if session.applied_constraints:
            report += "## 適用された制約\n\n"
            for constraint in session.applied_constraints:
                report += f"- {constraint}\n"
            report += "\n"
        
        # 最終結果
        report += f"""## 最終結果

### 判断
```
{session.final_judgment}
```

### 信頼度
**{session.final_confidence}**

### 代替推論パス
"""
        if session.alternative_paths:
            for path in session.alternative_paths:
                report += f"- {path}\n"
        else:
            report += "なし\n"
        
        report += f"""
## 検証情報
- **CoreThink論文準拠**: {'✅ Yes' if session.core_think_compliance else '❌ No'}
- **総推論ステップ数**: {len(session.reasoning_steps)}
- **GSR層実行**: {', '.join(set(step.layer for step in session.reasoning_steps))}

---
*このレポートは CoreThink-MCP 推論ログシステムにより自動生成されました*
"""
        
        return report

# グローバルロガーインスタンス
reasoning_logger = ReasoningLogger()