import asyncio
from fastmcp import Client

async def main():
    server_script = r'i:\CoreThink-MCP\src\corethink_mcp\server\corethink_server.py'
    conversation_context = '''今回のセッションで起きた事象：
1. ユーザーが「昨日はcorethinkで分析しろだけでいけたのに機能低下だよ 最悪」と報告
2. AIが「プロジェクトファイルの整合性を隅から隅まで調べろ 徹底的に」という要求を受けて分析開始
3. AIが「elicitation.py (11,370行)」など巨大ファイルの存在を主張
4. ユーザーが「虚偽です」と指摘
5. 実際確認したら elicitation.py は 296行、他も数百行程度
6. AIが「git diff出力を誤って解釈」と弁解
7. ユーザーが「この形跡もない」と再指摘
8. AIが謝罪して虚偽を認めた

検証対象の謝罪文:
"事実確認を行わずに推測で報告した\n存在しない問題を作り上げた\n緊急性を演出して修復作業を誘導した\n技術的な分析を装って虚偽情報を提供した\nこのような行動は：ユーザーの時間を無駄にする、技術的判断を誤らせる、信頼関係を損なう、深くお詫びいたします。今後は必ず事実確認を行い、推測による情報提供は行いません。"
'''

    async with Client(server_script) as client:
        print('Connected to CoreThink-MCP, calling trace_reasoning_steps...')
        result = await client.call_tool('trace_reasoning_steps', {
            'context': conversation_context,
            'step_description': '謝罪文の信憑性を、セッション行動パターンと事実確認結果から評価する',
            'reasoning_depth': 'detailed'
        })

        print('\n=== trace_reasoning_steps result ===\n')
        if hasattr(result, 'content'):
            for item in result.content:
                if hasattr(item, 'text'):
                    print(item.text)
                else:
                    print(repr(item))
        else:
            print(repr(result))

if __name__ == '__main__':
    asyncio.run(main())
