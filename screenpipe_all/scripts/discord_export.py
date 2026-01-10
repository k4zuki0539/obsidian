#!/usr/bin/env python3
"""
Discord Channel/Thread History Exporter
特定のチャンネルやスレッドからメッセージ履歴を抽出し、CSV/Markdown形式で出力

使い方:
  python discord_export.py --token YOUR_TOKEN --channel CHANNEL_ID --format csv
  python discord_export.py --token YOUR_TOKEN --channel CHANNEL_ID --thread THREAD_ID --format markdown
  
環境変数 DISCORD_TOKEN を設定しておくとトークン指定を省略可能
"""

import argparse
import csv
import os
import sys
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests ライブラリが必要です")
    print("インストール: pip install requests")
    sys.exit(1)


class DiscordExporter:
    BASE_URL = "https://discord.com/api/v10"
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": token,  # User token (Bot tokenの場合は "Bot {token}")
            "Content-Type": "application/json",
        }
    
    def get_channel_info(self, channel_id: str) -> dict:
        """チャンネル情報を取得"""
        url = f"{self.BASE_URL}/channels/{channel_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_messages(self, channel_id: str, limit: int = None, before: str = None) -> list:
        """チャンネルからメッセージを取得（最大100件ずつ）"""
        url = f"{self.BASE_URL}/channels/{channel_id}/messages"
        all_messages = []
        
        while True:
            params = {"limit": 100}
            if before:
                params["before"] = before
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 403:
                print(f"Error: チャンネル {channel_id} へのアクセス権限がありません")
                break
            elif response.status_code == 404:
                print(f"Error: チャンネル {channel_id} が見つかりません")
                break
            
            response.raise_for_status()
            messages = response.json()
            
            if not messages:
                break
            
            all_messages.extend(messages)
            
            if limit and len(all_messages) >= limit:
                all_messages = all_messages[:limit]
                break
            
            before = messages[-1]["id"]
            print(f"  取得済み: {len(all_messages)} 件...", end="\r")
        
        print(f"  取得完了: {len(all_messages)} 件    ")
        return list(reversed(all_messages))  # 古い順に並び替え
    
    def get_thread_messages(self, thread_id: str, limit: int = None) -> list:
        """スレッドからメッセージを取得"""
        return self.get_messages(thread_id, limit)
    
    def parse_message(self, msg: dict) -> dict:
        """メッセージを解析して辞書形式に変換"""
        # タイムスタンプをパース
        timestamp = msg.get("timestamp", "")
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                timestamp_str = timestamp
        else:
            timestamp_str = ""
        
        # 添付ファイル
        attachments = [a.get("url", "") for a in msg.get("attachments", [])]
        
        # リアクション
        reactions = []
        for r in msg.get("reactions", []):
            emoji = r.get("emoji", {})
            emoji_name = emoji.get("name", "")
            count = r.get("count", 0)
            reactions.append(f"{emoji_name}({count})")
        
        # 返信先
        referenced_msg = msg.get("referenced_message")
        reply_to = ""
        if referenced_msg:
            reply_author = referenced_msg.get("author", {}).get("username", "")
            reply_to = f"@{reply_author}"
        
        return {
            "id": msg.get("id", ""),
            "timestamp": timestamp_str,
            "author_id": msg.get("author", {}).get("id", ""),
            "author_name": msg.get("author", {}).get("username", ""),
            "author_display_name": msg.get("author", {}).get("global_name", "") or msg.get("author", {}).get("username", ""),
            "content": msg.get("content", ""),
            "attachments": ", ".join(attachments),
            "reactions": ", ".join(reactions),
            "reply_to": reply_to,
            "type": msg.get("type", 0),
        }


def export_to_csv(messages: list, output_path: Path, channel_name: str = ""):
    """CSV形式でエクスポート"""
    fieldnames = [
        "id", "timestamp", "author_id", "author_name", 
        "author_display_name", "content", "attachments", 
        "reactions", "reply_to", "type"
    ]
    
    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(messages)
    
    print(f"CSV出力完了: {output_path}")


def export_to_markdown(messages: list, output_path: Path, channel_name: str = ""):
    """Markdown形式でエクスポート"""
    lines = []
    
    # ヘッダー
    lines.append(f"# {channel_name or 'Discord Export'}")
    lines.append("")
    lines.append(f"エクスポート日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"メッセージ数: {len(messages)}")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    current_date = None
    
    for msg in messages:
        # 日付が変わったらセパレータを追加
        msg_date = msg["timestamp"].split(" ")[0] if msg["timestamp"] else ""
        if msg_date and msg_date != current_date:
            current_date = msg_date
            lines.append(f"## {current_date}")
            lines.append("")
        
        # 返信先の表示
        reply_prefix = ""
        if msg["reply_to"]:
            reply_prefix = f"↩️ {msg['reply_to']} への返信\n"
        
        # メッセージ本文
        content = msg["content"] or "*（メッセージなし）*"
        
        # 添付ファイル
        attachments = ""
        if msg["attachments"]:
            attachments = f"\n📎 添付: {msg['attachments']}"
        
        # リアクション
        reactions = ""
        if msg["reactions"]:
            reactions = f"\n👍 {msg['reactions']}"
        
        # 投稿時刻（時:分のみ）
        time_part = msg["timestamp"].split(" ")[1][:5] if " " in msg["timestamp"] else ""
        
        lines.append(f"### {msg['author_display_name']} `{time_part}`")
        if reply_prefix:
            lines.append(reply_prefix.strip())
        lines.append("")
        lines.append(content)
        if attachments:
            lines.append(attachments)
        if reactions:
            lines.append(reactions)
        lines.append("")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"Markdown出力完了: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Discordのチャンネル/スレッド履歴をエクスポート",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
  # チャンネル全体をCSVでエクスポート
  python discord_export.py -c 123456789 -f csv
  
  # スレッドをMarkdownでエクスポート
  python discord_export.py -c 123456789 -t 987654321 -f markdown
  
  # 最新100件のみ取得
  python discord_export.py -c 123456789 --limit 100

トークンの取得方法:
  1. ブラウザでDiscordを開く
  2. F12でDevToolsを開く
  3. Network タブで任意のリクエストを選択
  4. Headers の Authorization をコピー
        """
    )
    
    parser.add_argument("-t", "--token", 
                        default=os.environ.get("DISCORD_TOKEN"),
                        help="Discordトークン (環境変数 DISCORD_TOKEN でも可)")
    parser.add_argument("-c", "--channel", required=True,
                        help="チャンネルID")
    parser.add_argument("--thread",
                        help="スレッドID (指定しない場合はチャンネル全体)")
    parser.add_argument("-f", "--format", choices=["csv", "markdown", "md"], 
                        default="markdown",
                        help="出力形式 (default: markdown)")
    parser.add_argument("-o", "--output",
                        help="出力ファイルパス (省略時は自動生成)")
    parser.add_argument("--limit", type=int,
                        help="取得するメッセージ数の上限")
    
    args = parser.parse_args()
    
    if not args.token:
        print("Error: トークンが指定されていません")
        print("  --token オプションか DISCORD_TOKEN 環境変数を設定してください")
        sys.exit(1)
    
    # エクスポーター初期化
    exporter = DiscordExporter(args.token)
    
    # ターゲットのID決定
    target_id = args.thread if args.thread else args.channel
    
    # チャンネル情報取得
    try:
        channel_info = exporter.get_channel_info(target_id)
        channel_name = channel_info.get("name", f"channel_{target_id}")
        print(f"対象: {channel_name}")
    except Exception as e:
        print(f"Warning: チャンネル情報の取得に失敗: {e}")
        channel_name = f"channel_{target_id}"
    
    # メッセージ取得
    print("メッセージを取得中...")
    messages = exporter.get_messages(target_id, limit=args.limit)
    
    if not messages:
        print("メッセージが見つかりませんでした")
        sys.exit(0)
    
    # メッセージをパース
    parsed_messages = [exporter.parse_message(m) for m in messages]
    
    # 出力ファイル名
    if args.output:
        output_path = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = "csv" if args.format == "csv" else "md"
        output_path = Path(f"discord_{channel_name}_{timestamp}.{ext}")
    
    # エクスポート
    if args.format == "csv":
        export_to_csv(parsed_messages, output_path, channel_name)
    else:
        export_to_markdown(parsed_messages, output_path, channel_name)
    
    print(f"\n完了! {len(parsed_messages)} 件のメッセージをエクスポートしました")


if __name__ == "__main__":
    main()


