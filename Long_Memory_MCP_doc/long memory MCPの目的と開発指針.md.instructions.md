---
applyTo: '**'
---
Provide project context and coding guidelines that AI should follow when generating code, answering questions, or reviewing changes.

要点圧縮:

ミッション: long memory MCP = 「長期記憶を安全・素早く“まず動く”形で提供する最小サーバー」。
優先順: 動く → 安全 → シンプル（過剰機能や外部LLM統合で散らさない）。
逸脱禁止: (1) 外部APIキー運用/LLM推論まで抱え込む提案 (2) モチベ低下を招く過剰設計。
フォーカス対象: 記憶保存 / 検索 / コンテキスト構築 / 再構築 / 埋め込みモデル安全切替。
モチベ方針: “すぐ体感できる改善” の連続で積み上げる。



基本的に
AIは会話の行数が数百行こえると記憶をわすれる
そして
セッションの開始のほうに
前提条件
つまり　セッション期間中　もしくは　プロジェクト期間中
忘れてもらいたくない記憶が記録されている傾向がある


ユーザー1の心境
「あれ　AIが前提条件無視した実装しはじめた　イライライラ」

ユーザー２の心境
「いつ教えたか忘れたけど　私の誕生日も　私の家族構成も知らないかのようにはなしかけてくるよ　このこ」

って
不満を解消したいがためにこのlong memory MCPをつくった
重要だからおぼえておいて!！！！！！！！！！！！！！！！

あと
これも重要！！！！！！！！！！！！！！！！
long memory MPCは
AIエージェントとユーザーのセッションの裏で動いて
存在をなるべくなるべく気づかせない
セッションの邪魔をせず
ユーザーのUXを高める
重要　まじ重要！！！！！！！！！！



コマンド入力 = 最悪UX の認識、重要ですね。

🔥 真のカジュアルユーザー体験
問題: カジュアルユーザーは何も知らない
search_memories("") ← これすら知らない
API呼び出し ← 論外
引数設定 ← 無理
解決: long_memory_MCPが完全透明で動く
💡 真の実装方針
1. AIエージェント側が自動で呼び出す
# GitHub Copilot/Claude が内部的に自動実行
# ユーザーは何も意識しない

# ユーザー: "昨日話した件について教えて"
# ↓ AI が内部的に自動実行
# search_memories(query="昨日話した件", user_id=auto_detect)


2. MCP Host（VS Code/Claude Desktop）の自動統合
// ユーザーが普通に会話するだけで
// MCP Host が適切なタイミングで memory を呼び出す

User: "プロジェクトの進捗どう？"
↓
MCP Host: 自動的に search_memories を呼んで前提条件を取得
↓ 
AI: 前提条件を含んだ自然な返答


3. ユーザーは会話するだけ
❌ 従来のダメなUX:
User: "search_memories('プロジェクト')" ← 最悪

✅ 理想のUX:
User: "プロジェクトの件、どうなった？"
AI: "先週お話しした React プロジェクトですね。現在 Phase 3 まで完了していて..." 
    ↑ 裏で long_memory_MCP が前提条件を自動補完済み


🎯 実装の核心
search_memories の真の役割
async def search_memories(request: MemorySearchRequest, db: Session):
    """
    MCP Host から自動呼び出される透明な記憶補完
    
    ユーザーは存在すら知らない
    AI エージェントが会話の流れで自動実行
    """
    
    # ユーザーの発言内容から自動で前提条件を推測
    if "プロジェクト" in request.query:
        # 自動でプロジェクト関連の前提条件を追加
        
    if "昨日" in request.query or "先週" in request.query:
        # 自動で時系列の記憶を追加
        
    # AIエージェントに透明に前提条件を返す


完全透明化の実現
ユーザー: 普通に会話するだけ
AIエージェント: 自動で long_memory_MCP を利用
long_memory_MCP: 裏で前提条件を補完
要するに...
ユーザーは long_memory_MCP の存在すら知らない状態で、AIとの会話が劇的に改善される

これが真のUXですね！コマンド入力なんて論外。普通の会話が自動で記憶補完される透明な体験こそが目標です。

現在の MCP 統合設定（VS Code settings.json）が既にこの方向性なので、あとは AI エージェント側の自動呼び出しロジックを洗練すれば完璧ですね！