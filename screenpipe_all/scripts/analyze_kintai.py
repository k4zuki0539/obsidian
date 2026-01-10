#!/usr/bin/env python3
"""
勤怠データ分析スクリプト
担当者ごとにタスクをカテゴライズして時間を集計
"""

import re
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import argparse


def parse_time_to_minutes(time_str: str) -> int:
    """時間文字列を分に変換"""
    time_str = time_str.strip()
    total_minutes = 0
    
    # 「1時間30分」「1.5時間」「30分」「1H」「1h」などに対応
    
    # 時間と分のパターン
    hour_min_match = re.search(r'(\d+(?:\.\d+)?)\s*時間\s*(\d+)?\s*分?', time_str)
    if hour_min_match:
        hours = float(hour_min_match.group(1))
        minutes = int(hour_min_match.group(2)) if hour_min_match.group(2) else 0
        return int(hours * 60 + minutes)
    
    # 時間のみ
    hour_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:時間|H|h)', time_str, re.IGNORECASE)
    if hour_match:
        return int(float(hour_match.group(1)) * 60)
    
    # 分のみ
    min_match = re.search(r'(\d+)\s*分', time_str)
    if min_match:
        return int(min_match.group(1))
    
    return 0


def parse_task_line(line: str) -> tuple:
    """タスク行をパースしてカテゴリ、タスク名、時間を抽出"""
    line = line.strip()
    
    # パターン1: ・カテゴリ：タスク名（時間）
    match1 = re.match(r'[・･]\s*([^：:]+)[：:]\s*(.+?)[（\(]([^）\)]+)[）\)]', line)
    if match1:
        category = match1.group(1).strip()
        task = match1.group(2).strip()
        time_str = match1.group(3)
        minutes = parse_time_to_minutes(time_str)
        if minutes > 0:
            return category, task, minutes
    
    # パターン2: ・タスク名＋数字（分）例: ・tiktok撮影180
    match2 = re.match(r'[・･]\s*(.+?)(\d+)\s*$', line)
    if match2:
        task_name = match2.group(1).strip()
        minutes = int(match2.group(2))
        if minutes > 0 and minutes <= 1440:  # 24時間以内
            # タスク名からカテゴリを推測
            category = guess_category(task_name)
            return category, task_name, minutes
    
    # パターン3: ・カテゴリ：タスク名 時間
    match3 = re.match(r'[・･]\s*([^：:]+)[：:]\s*(.+?)\s+(\d+(?:\.\d+)?(?:時間|分|H|h)[^\s]*)', line)
    if match3:
        category = match3.group(1).strip()
        task = match3.group(2).strip()
        time_str = match3.group(3)
        minutes = parse_time_to_minutes(time_str)
        if minutes > 0:
            return category, task, minutes
    
    return None, None, 0


def guess_category(task_name: str) -> str:
    """タスク名からカテゴリを推測"""
    task_lower = task_name.lower()
    
    if 'youtube' in task_lower or 'yt' in task_lower:
        return 'YouTube'
    elif 'tiktok' in task_lower:
        return 'TikTok'
    elif 'instagram' in task_lower or 'インスタ' in task_name:
        return 'Instagram'
    elif 'x' == task_lower or 'twitter' in task_lower:
        return 'X(Twitter)'
    elif '基本' in task_name or '採用' in task_name:
        return '基本業務'
    elif 'mtg' in task_lower or '会議' in task_name or '打ち合わせ' in task_name or '面談' in task_name:
        return 'MTG・会議'
    elif 'チャレロン' in task_name or 'チャレンジ' in task_name:
        return 'チャレンジローンチ'
    elif 'ひかり' in task_name:
        return 'ひかりch'
    elif 'lp' in task_lower or 'LP' in task_name:
        return 'LP作成'
    elif '撮影' in task_name:
        return '撮影'
    elif '台本' in task_name:
        return '台本作成'
    elif 'line' in task_lower or 'LINE' in task_name:
        return 'LINE'
    else:
        return 'その他'


def parse_markdown_file(filepath: Path, target_year: int, target_month: int) -> dict:
    """Markdownファイルを解析して対象月のタスクデータを抽出"""
    data = defaultdict(lambda: defaultdict(int))
    tasks_detail = defaultdict(list)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    current_date = None
    in_target_month = False
    current_section = None  # 予定業務 or 実施業務
    
    lines = content.split('\n')
    
    for line in lines:
        # 日付行を検出
        date_match = re.match(r'^##\s+(\d{4})-(\d{2})-(\d{2})', line)
        if date_match:
            year = int(date_match.group(1))
            month = int(date_match.group(2))
            day = int(date_match.group(3))
            current_date = f"{year}-{month:02d}-{day:02d}"
            in_target_month = (year == target_year and month == target_month)
            current_section = None
            continue
        
        if not in_target_month:
            continue
        
        # セクション検出（実施業務を優先）
        if '実施業務' in line or '実績業務' in line:
            current_section = '実施'
        elif '予定業務' in line and current_section != '実施':
            current_section = '予定'
        
        # タスク行をパース（実施業務セクションのみ、または実施がなければ予定も）
        if current_section == '実施' or (current_section == '予定' and '実施' not in content[content.find(current_date):content.find(current_date)+2000]):
            category, task, minutes = parse_task_line(line)
            if category and minutes > 0:
                # カテゴリ名の正規化
                category = normalize_category(category)
                data[category]['total_minutes'] += minutes
                data[category]['count'] += 1
                tasks_detail[category].append({
                    'date': current_date,
                    'task': task,
                    'minutes': minutes
                })
    
    return dict(data), dict(tasks_detail)


def normalize_category(category: str) -> str:
    """カテゴリ名を正規化"""
    category = category.strip()
    
    # よくあるカテゴリの正規化
    mappings = {
        '基本業務': '基本業務',
        '基本': '基本業務',
        'YouTube': 'YouTube',
        'youtube': 'YouTube',
        'YT': 'YouTube',
        'X': 'X(Twitter)',
        'Twitter': 'X(Twitter)',
        'Instagram': 'Instagram',
        'IG': 'Instagram',
        'インスタ': 'Instagram',
        'TikTok': 'TikTok',
        'tiktok': 'TikTok',
        '法人': '法人',
        'MTG': 'MTG・会議',
        '会議': 'MTG・会議',
        'ミーティング': 'MTG・会議',
        '組織コーチング': '組織コーチング',
        'コーチング': '組織コーチング',
    }
    
    for key, value in mappings.items():
        if key.lower() in category.lower():
            return value
    
    return category


def format_time(minutes: int) -> str:
    """分を時間:分形式に変換"""
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0 and mins > 0:
        return f"{hours}時間{mins}分"
    elif hours > 0:
        return f"{hours}時間"
    else:
        return f"{mins}分"


def generate_report(member_name: str, data: dict, tasks_detail: dict, year: int, month: int) -> str:
    """分析レポートを生成"""
    lines = []
    lines.append(f"# {member_name} - {year}年{month}月 勤怠分析")
    lines.append("")
    lines.append(f"分析日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    if not data:
        lines.append("※ 対象期間のデータがありません")
        return "\n".join(lines)
    
    # 合計時間
    total_minutes = sum(d.get('total_minutes', 0) for d in data.values())
    lines.append(f"## 📊 サマリー")
    lines.append("")
    lines.append(f"- **総作業時間**: {format_time(total_minutes)}")
    lines.append(f"- **カテゴリ数**: {len(data)}")
    lines.append("")
    
    # カテゴリ別集計（時間順にソート）
    lines.append("## 📈 カテゴリ別作業時間")
    lines.append("")
    lines.append("| カテゴリ | 作業時間 | 割合 | タスク数 |")
    lines.append("|----------|----------|------|----------|")
    
    sorted_categories = sorted(data.items(), key=lambda x: x[1].get('total_minutes', 0), reverse=True)
    
    for category, stats in sorted_categories:
        minutes = stats.get('total_minutes', 0)
        count = stats.get('count', 0)
        percentage = (minutes / total_minutes * 100) if total_minutes > 0 else 0
        lines.append(f"| {category} | {format_time(minutes)} | {percentage:.1f}% | {count}件 |")
    
    lines.append("")
    
    # 視覚的なバーチャート
    lines.append("### 時間配分グラフ")
    lines.append("")
    lines.append("```")
    max_bar_length = 40
    max_minutes = max(d.get('total_minutes', 0) for d in data.values()) if data else 1
    
    for category, stats in sorted_categories:
        minutes = stats.get('total_minutes', 0)
        bar_length = int((minutes / max_minutes) * max_bar_length) if max_minutes > 0 else 0
        bar = "█" * bar_length
        lines.append(f"{category:15} {bar} {format_time(minutes)}")
    lines.append("```")
    lines.append("")
    
    # カテゴリ別詳細
    lines.append("## 📝 カテゴリ別詳細")
    lines.append("")
    
    for category, stats in sorted_categories:
        minutes = stats.get('total_minutes', 0)
        lines.append(f"### {category}")
        lines.append("")
        lines.append(f"**合計**: {format_time(minutes)}")
        lines.append("")
        
        if category in tasks_detail:
            # 日付ごとにグループ化
            by_date = defaultdict(list)
            for task in tasks_detail[category]:
                by_date[task['date']].append(task)
            
            for date in sorted(by_date.keys()):
                tasks = by_date[date]
                lines.append(f"**{date}**")
                for t in tasks:
                    lines.append(f"- {t['task']} ({format_time(t['minutes'])})")
                lines.append("")
        
        lines.append("---")
        lines.append("")
    
    return "\n".join(lines)


def analyze_all_members(input_dir: Path, output_dir: Path, year: int, month: int):
    """全メンバーの分析を実行"""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_data = {}
    
    for member_dir in input_dir.iterdir():
        if not member_dir.is_dir():
            continue
        
        member_name = member_dir.name
        md_file = member_dir / f"discord_{member_name}.md"
        
        if not md_file.exists():
            # 別のファイル名を試す
            md_files = list(member_dir.glob("*.md"))
            if md_files:
                md_file = md_files[0]
            else:
                print(f"Skip: {member_name} (no md file)")
                continue
        
        print(f"分析中: {member_name}...")
        data, tasks_detail = parse_markdown_file(md_file, year, month)
        
        if data:
            all_data[member_name] = {'data': data, 'tasks_detail': tasks_detail}
            
            # 個別レポート生成
            report = generate_report(member_name, data, tasks_detail, year, month)
            output_file = output_dir / f"{member_name}_{year}年{month}月.md"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"  -> {output_file.name}")
    
    # 全体サマリー生成
    if all_data:
        summary = generate_team_summary(all_data, year, month)
        summary_file = output_dir / f"チーム全体_{year}年{month}月.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"\nチーム全体サマリー -> {summary_file.name}")


def generate_team_summary(all_data: dict, year: int, month: int) -> str:
    """チーム全体のサマリーを生成"""
    lines = []
    lines.append(f"# チーム全体 - {year}年{month}月 勤怠分析")
    lines.append("")
    lines.append(f"分析日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"対象メンバー: {len(all_data)}名")
    lines.append("")
    
    # メンバー別総作業時間
    lines.append("## 👥 メンバー別作業時間")
    lines.append("")
    lines.append("| メンバー | 総作業時間 | 主要カテゴリ |")
    lines.append("|----------|------------|--------------|")
    
    member_totals = []
    for member, info in all_data.items():
        total = sum(d.get('total_minutes', 0) for d in info['data'].values())
        top_category = max(info['data'].items(), key=lambda x: x[1].get('total_minutes', 0))[0] if info['data'] else "-"
        member_totals.append((member, total, top_category))
    
    member_totals.sort(key=lambda x: x[1], reverse=True)
    
    for member, total, top_cat in member_totals:
        lines.append(f"| {member} | {format_time(total)} | {top_cat} |")
    
    lines.append("")
    
    # チーム全体のカテゴリ別集計
    lines.append("## 📊 チーム全体カテゴリ別時間")
    lines.append("")
    
    team_categories = defaultdict(int)
    for info in all_data.values():
        for cat, stats in info['data'].items():
            team_categories[cat] += stats.get('total_minutes', 0)
    
    total_team = sum(team_categories.values())
    sorted_cats = sorted(team_categories.items(), key=lambda x: x[1], reverse=True)
    
    lines.append("| カテゴリ | 合計時間 | 割合 |")
    lines.append("|----------|----------|------|")
    
    for cat, minutes in sorted_cats:
        pct = (minutes / total_team * 100) if total_team > 0 else 0
        lines.append(f"| {cat} | {format_time(minutes)} | {pct:.1f}% |")
    
    lines.append("")
    
    # グラフ
    lines.append("### 時間配分グラフ")
    lines.append("")
    lines.append("```")
    max_bar = 40
    max_min = max(team_categories.values()) if team_categories else 1
    
    for cat, minutes in sorted_cats[:10]:  # 上位10カテゴリ
        bar_len = int((minutes / max_min) * max_bar)
        bar = "█" * bar_len
        lines.append(f"{cat:15} {bar} {format_time(minutes)}")
    lines.append("```")
    lines.append("")
    
    # メンバー別リンク
    lines.append("## 📁 個別レポート")
    lines.append("")
    for member, total, _ in member_totals:
        lines.append(f"- [[{member}_{year}年{month}月]]")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="勤怠データを分析してレポート生成")
    parser.add_argument("-i", "--input", required=True, help="入力ディレクトリ（メンバー勤怠フォルダ）")
    parser.add_argument("-o", "--output", required=True, help="出力ディレクトリ")
    parser.add_argument("-y", "--year", type=int, required=True, help="対象年")
    parser.add_argument("-m", "--month", type=int, required=True, help="対象月")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    if not input_dir.exists():
        print(f"Error: 入力ディレクトリが存在しません: {input_dir}")
        return
    
    analyze_all_members(input_dir, output_dir, args.year, args.month)
    print("\n分析完了!")


if __name__ == "__main__":
    main()

