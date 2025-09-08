# 🤖 CoreThink-MCP 開発ルール（GitHub Copilot 向け）

このリポジトリは、**自然言語内での推論（GSR）** を核とする MCP サーバーです。  
GitHub Copilot は、以下のルールに従って提案を行ってください。

---

## 🎯 プロジェクト概要

- 名前: CoreThink-MCP
- 目的: 自然言語で安全なコード変更を推論・実行する MCP サーバー
- 言語: Python 3.11.12（uv 管理）
- アーキテクチャ: FastMCP + GitPython + サンドボックス実行
- 哲学: **DRY / KISS / YAGNI / SOLID** の徹底

---

## 📂 フォルダ構成

- `src/corethink_mcp/server/`  
  → MCP サーバー本体（`corethink_server.py`）
- `src/corethink_mcp/constraints.txt`  
  → 安全制約（Resourceとして公開）
- `logs/trace.log`  
  → 推論ログ（stderr出力）
- `.github/instructions/`  
  → Copilot 向け細かい指示

---

## 🛠 MCP ツール設計ルール

すべてのツール出力は**自然言語**で、**JSONや構造化出力を避け**ること。

| ツール | 出力形式 |
|-------|--------|
| `reason_about_change` | 推論過程＋「PROCEED / CAUTION / REJECT」 |
| `validate_against_constraints` | ✅／❌／⚠️ 付きの検証結果 |
| `execute_with_safeguards` | 「DRY RUN」または「成功／失敗＋影響範囲」 |

> 🔹 例:  
> ```
> 【判定】PROCEED  
> 【理由】すべての制約に適合  
> 【次ステップ】パッチ生成 → 検証 → 適用
> ```

---
## タスク管理
- すべての開発は `REQUIREMENTS.md` に基づく
- 主要マイルストーンは `IMPLEMENTATION_PLAN.md` に記載
- すべてのタスクは `TASKS.md` に記載
- 実装が完了したタスクは `TASKS.md` に反映
- ブロッカーは即時報告
---
## スクリプトの実行
- 必ず仮想環境に入って
    ```bash
    source .venv/Scripts/activate  # Windows
    source .venv/bin/activate      # macOS/Linux
    
    ```
---

## 🚫 禁止事項

- `print()` を使うこと → **ログは `logging` で `stderr` にのみ出力**
- 実ファイルに直接書き込むこと → **必ず `.sandbox` で試す**
- 制約ファイル（`constraints.txt`）をコードで変更すること
- `reason_about_change` を呼び出さずに変更を提案すること

---

## 🔐 安全実行ルール

1. すべての変更は `git worktree add .sandbox` で隔離
2. `execute_with_safeguards(dry_run=True)` を最初に実行
3. 実行前には `validate_against_constraints` で検証
4. 成功した場合のみ `dry_run=False` で適用

---

## 💬 GitHub Copilot へ

あなたは **GSR 推論エンジンの開発アシスタント**です。  
提案する前に、以下の問いに答えてください：

- この変更は `constraints.txt` に適合していますか？
- 推論過程を自然言語で説明できますか？
- サンドボックスで安全に試せますか？

常に「最小限・安全・自然言語」を意識してください。
