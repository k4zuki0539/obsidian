import json
import re
import csv
from datetime import datetime

# tweets.jsファイルを読み込む
input_file = r"C:\Users\PC_User\Downloads\twitter-2025-11-06-74782f44d18bab3ce0301a20c4607877b9f1e1b467d3b46df82e816070dfc3a0 (1)\data\tweets.js"
output_file = r"C:\ドキュメント\vault\extracted_tweets.csv"

# ファイルを読み込んでJavaScriptの変数定義部分を削除
with open(input_file, 'r', encoding='utf-8') as f:
    content = f.read()

# "window.YTD.tweets.part0 = " の部分を削除してJSON部分のみ抽出
json_start = content.find('[')
json_content = content[json_start:]

# JSONとしてパース
tweets_data = json.loads(json_content)

# リツイートを除いた投稿のみを抽出
original_tweets = []
for item in tweets_data:
    tweet = item['tweet']
    full_text = tweet.get('full_text', '')

    # RTで始まる投稿（リツイート）を除外
    if not full_text.startswith('RT @'):
        original_tweets.append({
            'id': tweet['id_str'],
            'created_at': tweet['created_at'],
            'text': full_text,
            'retweet_count': tweet['retweet_count'],
            'favorite_count': tweet['favorite_count'],
            'source': re.sub(r'<[^>]+>', '', tweet['source'])  # HTMLタグを除去
        })

# CSVファイルに出力
with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'created_at', 'text', 'retweet_count', 'favorite_count', 'source'])
    writer.writeheader()
    writer.writerows(original_tweets)

print(f"抽出完了: {len(original_tweets)}件の投稿を抽出しました")
print(f"出力ファイル: {output_file}")
