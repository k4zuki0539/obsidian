# タスクリスト: Screenpipe 時間単位サマリーパイプライン 初回セットアップ

## Phase 0: パス設計（環境依存）
1. `<BASE>` を決める（作業ディレクトリのルート）
2. raw / hourly / daily / scripts / logs の配置方針を決定
3. 既存の Screenpipe ログ構成がある場合はその構成に合わせる

## Phase 1: ディレクトリ準備
1. raw 入力ディレクトリの存在を確認
2. hourly_summary 出力ディレクトリを作成
3. daily 出力ディレクトリを作成
4. scripts / logs ディレクトリを作成

## Phase 2: 環境変数定義
1. `.env` もしくは同等の設定ファイルを作成
2. `CODEX_COMMAND` を設定
3. `SCREENPIPE_RAW_DIR` を設定
4. `SCREENPIPE_HOURLY_OUTPUT_DIR` を設定
5. `SCREENPIPE_DAILY_OUTPUT_DIR` を設定
6. `SCREENPIPE_SUMMARY_CODEX_TIMEOUT` を設定

## Phase 3: 時間単位サマリー生成スクリプト作成
1. raw の対象時間を決定する引数/ロジックを実装
2. raw ファイル不存在時はスキップ
3. 入力をトリム（文字数上限/行長制限）
4. Codex CLI 実行（非対話）
5. 出力を `hourly_summary/YYYY-MM-DD/HH.md` に保存
6. 標準出力/標準エラーをログに記録

## Phase 4: 日次まとめスクリプト作成
1. 対象日の hourly_summary を収集
2. 結合後に Codex CLI へ送信
3. 出力を `daily/YYYY-MM-DD.md` に保存
4. 失敗時はログに記録

## Phase 5: launchd 設定（macOS）
1. 時間単位実行の plist を作成
2. 日次実行の plist を作成
3. `EnvironmentVariables` に `HOME`/`PATH`/`PYTHONPATH` を設定
4. stdout/stderr ログパスを指定
5. `launchctl load`/`bootstrap` で有効化

## Phase 6: 旧パイプラインの競合回避
1. 既存の日次スクリプトを確認
2. 同時起動の恐れがある場合は無効化

## Phase 7: 動作確認
1. 手動で時間単位スクリプトを実行
2. 期待する hourly 出力が生成されることを確認
3. 手動で日次スクリプトを実行
4. daily 出力が生成されることを確認
5. ログにエラーが無いことを確認

## Phase 8: 失敗時の復旧手順整備
1. HOME 未定義での失敗を再現しないことを確認
2. Codex タイムアウト時の再実行手順を明文化
3. raw 不在時の挙動（スキップ）を確認

## Phase 9: 受け入れ条件チェック
1. 毎時 05 分の生成が行われる
2. 23:50 の日次まとめが生成される
3. ファイルパスに従って出力される
4. ログで失敗理由が追跡できる

## 参照
- memory_bank/report/2025-12-25_screenpipe-hourly-pipeline.md
