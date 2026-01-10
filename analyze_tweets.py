import csv
import re
from collections import Counter
import json

# CSVファイルを読み込む
input_file = r"C:\ドキュメント\vault\extracted_tweets.csv"

tweets = []
with open(input_file, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        tweets.append(row)

# 分析結果を格納
analysis = {
    "total_tweets": len(tweets),
    "character_length": [],
    "line_breaks": [],
    "emojis": [],
    "hashtags": [],
    "urls": [],
    "mentions": [],
    "punctuation_patterns": [],
    "opening_patterns": [],
    "high_engagement": [],
    "common_words": [],
    "sentence_structures": []
}

# 各ポストを分析
emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)

all_words = []
opening_words = []

for tweet in tweets:
    text = tweet['text']

    # 文字数
    analysis["character_length"].append(len(text))

    # 改行数
    line_breaks = text.count('\n')
    analysis["line_breaks"].append(line_breaks)

    # 絵文字の抽出
    emojis = emoji_pattern.findall(text)
    analysis["emojis"].extend(emojis)

    # ハッシュタグ
    hashtags = re.findall(r'#\w+', text)
    analysis["hashtags"].extend(hashtags)

    # URL
    urls = re.findall(r'https://t\.co/\w+', text)
    if urls:
        analysis["urls"].append(len(urls))

    # メンション
    mentions = re.findall(r'@\w+', text)
    if mentions:
        analysis["mentions"].append(len(mentions))

    # 句読点パターン（！、？、。など）
    exclamation = text.count('！')
    question = text.count('？')
    if exclamation > 0:
        analysis["punctuation_patterns"].append(f"！x{exclamation}")
    if question > 0:
        analysis["punctuation_patterns"].append(f"？x{question}")

    # 冒頭パターン（【】、＼／など）
    first_line = text.split('\n')[0] if '\n' in text else text[:50]
    if first_line.startswith('【'):
        opening_words.append("【】タイトル形式")
    elif first_line.startswith('＼'):
        opening_words.append("＼／強調形式")
    elif first_line.startswith('RT '):
        continue  # リツイートはスキップ
    else:
        opening_words.append("通常形式")

    # エンゲージメントが高い投稿（いいね30以上）
    try:
        fav_count = int(tweet['favorite_count'])
        if fav_count >= 30:
            analysis["high_engagement"].append({
                "text": text[:100] + "..." if len(text) > 100 else text,
                "favorite": fav_count,
                "retweet": tweet['retweet_count']
            })
    except:
        pass

    # 単語の抽出（簡易的）
    words = re.findall(r'[ぁ-んァ-ヶー一-龠]+', text)
    all_words.extend(words)

# 統計情報の計算
word_counter = Counter(all_words)
opening_counter = Counter(opening_words)
emoji_counter = Counter(analysis["emojis"])

# 結果をまとめる
result = {
    "基本統計": {
        "総投稿数": analysis["total_tweets"],
        "平均文字数": sum(analysis["character_length"]) / len(analysis["character_length"]) if analysis["character_length"] else 0,
        "最大文字数": max(analysis["character_length"]) if analysis["character_length"] else 0,
        "最小文字数": min(analysis["character_length"]) if analysis["character_length"] else 0,
        "平均改行数": sum(analysis["line_breaks"]) / len(analysis["line_breaks"]) if analysis["line_breaks"] else 0
    },
    "冒頭パターン（頻度順）": dict(opening_counter.most_common(10)),
    "頻出絵文字（TOP20）": dict(emoji_counter.most_common(20)),
    "頻出単語（TOP50）": dict(word_counter.most_common(50)),
    "句読点使用": {
        "感嘆符使用率": sum(1 for p in analysis["punctuation_patterns"] if '！' in p) / len(tweets) * 100 if tweets else 0,
        "疑問符使用率": sum(1 for p in analysis["punctuation_patterns"] if '？' in p) / len(tweets) * 100 if tweets else 0
    },
    "URL・メンション": {
        "URL含む投稿数": len(analysis["urls"]),
        "メンション含む投稿数": len(analysis["mentions"])
    },
    "高エンゲージメント投稿（いいね30以上、TOP20）": sorted(analysis["high_engagement"], key=lambda x: x['favorite'], reverse=True)[:20]
}

# 結果をJSONファイルに保存
output_file = r"C:\ドキュメント\vault\tweet_analysis.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("分析完了！")
print(f"出力ファイル: {output_file}")
print(f"\n【基本統計】")
print(f"総投稿数: {result['基本統計']['総投稿数']}")
print(f"平均文字数: {result['基本統計']['平均文字数']:.1f}")
print(f"平均改行数: {result['基本統計']['平均改行数']:.1f}")
print(f"\n【冒頭パターン】")
for pattern, count in list(result['冒頭パターン（頻度順）'].items())[:5]:
    print(f"{pattern}: {count}件")
