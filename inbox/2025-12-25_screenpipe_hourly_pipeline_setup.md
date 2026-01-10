# 要件定義: Screenpipe 時間単位サマリーパイプライン 初回セットアップ

## 目的
初回セットアップ時に詰まらず、Screenpipe の raw ログから **時間単位サマリー** と **日次まとめ** を自動生成するパイプラインを、Codex CLI + スケジューラで確実に再現できる状態を作る。

## 適用範囲
- Screenpipe raw ログを入力として、時間単位サマリーを生成
- 時間単位サマリーを集約して日次まとめを生成
- スケジューラ（macOS: launchd）での定期実行
- Codex CLI への移行（Claude CLI ではなく Codex CLI を使用）
- 失敗時の原因特定と復旧手順

## 対象外
- Screenpipe 本体のビルドや改修
- Linux/Windows のスケジューラ実装（必要なら別設計）
- UI/ダッシュボードの可視化

## 前提
- 実行環境は macOS（launchd が使えること）
- Codex CLI が利用できること
- raw ログが時間単位で生成されていること
- 実行ユーザーが cron/launchd での実行権限を持つこと

## 参照
- memory_bank/report/2025-12-25_screenpipe-hourly-pipeline.md

---

## 用語
- **raw ログ**: `raw/YYYY-MM-DD/HH.md` 形式の入力ログ
- **時間単位サマリー**: raw ログを 1 時間単位で要約したファイル
- **日次まとめ**: 1 日分の時間単位サマリーを統合したサマリー
- **パイプライン**: 1) 時間単位生成 2) 日次集約 の2段処理

---

## 要件

### 1. 入出力仕様
- 入力: `raw/YYYY-MM-DD/HH.md`
- 出力（時間単位）: `hourly_summary/YYYY-MM-DD/HH.md`
- 出力（日次）: `70_pipeline/YYYY-MM-DD.md` 形式
- ディレクトリやルートは **固定値禁止**。環境変数で指定可能にする。

### 1.1 音声ログ強化（必須要件）
- 音声取得は有効化する（`--disable-audio` は使わない）
- 収録デバイスは明示できるようにする（`--audio-device`）
- リアルタイム音声文字起こしを使う場合は `--enable-realtime-audio-transcription` と `--realtime-audio-device` を使う
- 音声ログ品質はテスト観点で確認する（マイク入力/システム音声出力/デバイス切替）

### 2. 実行スケジュール
- 時間単位サマリー: 毎時 05 分に実行
- 日次まとめ: 毎日 23:50 に実行
- スケジューラが `HOME` を渡さないケースに備え、**必ず環境変数を明示**

### 3. Codex CLI の利用要件
- 非対話モードで実行できること
- `--skip-git-repo-check` を使用
- 権限確認を避ける必要がある場合は、**責任を持って** `--dangerously-bypass-approvals-and-sandbox` を利用
- コマンド失敗時に stderr を返し、失敗理由をログに残す

### 4. プロンプト設計
- 時間単位サマリー:
  - 具体的なファイル名/コマンド/URLは残す
  - 機密値（APIキー/トークン/パスワード）は [REDACTED]
- 日次まとめ:
  - 概要/タイムライン/作業内容/技術メモ/課題/次アクション候補
  - 詳細度を保ち、行数を極端に削らない

### 5. 失敗耐性
- `set -u` による未定義変数エラーを避けるため、`HOME`/`PATH` は必ず注入
- 入力ファイルが無い場合はスキップし、エラー終了しない
- Codex CLI タイムアウトを設定可能にする（例: 600 秒）

### 6. ログ
- 時間単位・日次それぞれの実行ログを出力
- ログファイルは日付でローテーション
- 失敗時にエラー内容が分かる

---

## 設定項目（環境変数）
以下は **必ず設定可能** とし、スクリプトに直書きしない。

- `CODEX_COMMAND`: Codex CLI の実行コマンド
- `SCREENPIPE_RAW_DIR`: raw ログのルート
- `SCREENPIPE_HOURLY_OUTPUT_DIR`: 時間単位サマリーのルート
- `SCREENPIPE_DAILY_OUTPUT_DIR`: 日次まとめの出力先
- `SCREENPIPE_SUMMARY_CODEX_TIMEOUT`: Codex 実行タイムアウト（秒）

---

## ディレクトリ設計（例）
**パスは環境依存なので、必ず各環境で決定すること。**

- `<BASE>/screenpipe_all/raw/YYYY-MM-DD/HH.md`
- `<BASE>/screenpipe_all/hourly_summary/YYYY-MM-DD/HH.md`
- `<BASE>/70_pipeline/YYYY-MM-DD.md`
- `<BASE>/scripts/` （スクリプト置き場）
- `<BASE>/logs/` （実行ログ）

---

## 実装要件（スクリプト）

### A. 時間単位サマリー生成
- 入力を読み込み、文字数制限・長文行カットを行う
- Codex CLI にプロンプトを渡し、出力をファイル保存
- 失敗時はログに記録して終了

### B. 日次まとめ生成
- 対象日の時間単位サマリーを全て結合
- 日次まとめのフォーマットに従って Codex へ送信
- 出力を日次ファイルへ保存

---

## スケジューラ要件（macOS: launchd）
- `EnvironmentVariables` で `HOME` / `PATH` / `PYTHONPATH` を明示
- 標準出力/標準エラーをログへ出力
- plist のロード/リロード手順を明文化

---

## 受け入れ条件
1. **時間単位サマリー** が毎時自動生成される
2. **日次まとめ** が 23:50 に生成される
3. 生成物が所定ディレクトリに存在する
4. Codex の失敗ログが記録される
5. 既知の失敗要因（HOME未定義）を回避できる

---

## 既知の失敗パターンと回避策
- **launchd で HOME 未設定** → plist で EnvironmentVariables を必須化
- **raw ファイル不在** → スキップ処理を入れる
- **Codex タイムアウト** → `SCREENPIPE_SUMMARY_CODEX_TIMEOUT` を設定
- **超長文** → 文字数・行長制限を実装

---

## 運用・復旧
- 失敗ログから原因を特定
- 単発でスクリプトを手動実行し再生成できること
- 旧パイプラインが残っている場合は競合しないよう無効化

---

## テスト/検証
- 任意の日時の raw ログで単発実行
- 出力ファイルが生成されることを確認
- 生成内容にファイル名/コマンド/URLが含まれることを確認
- `cargo test` など Screenpipe 本体のテストは本要件の対象外
