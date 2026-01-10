# 配布用: Screenpipe 時間単位サマリーパイプライン 環境確定の質問テンプレ

目的: 各メンバーの環境差分を Codex が確実に把握し、手戻りなくセットアップできるようにする。

---

## 1. 環境情報
- OS とバージョンは？Windows 11
- 実行ユーザー名は？nino
- 既に Codex CLI は利用可能？分からないから確認して

## 2. Screenpipe ログの配置
- raw ログのルートパスは？
- raw のファイル形式は `raw/YYYY-MM-DD/HH.md` で合ってる？
- 既に hourly_summary 置き場がある？
-回答：分からないから確認して、無ければ設計して

## 3. 出力先とログ
- hourly_summary 出力先はどこにする？
- 日次まとめの出力先はどこにする？
- 実行ログの保存先はどこにする？
-適切な場所に設計して作成して

## 4. 既存パイプライン
- 旧パイプライン（Claude CLI / 日次処理）は動いている？
- 同時実行で競合する可能性はある？

## 5. スケジューラ
- macOS なら launchd を使って良い？
- 既存の plist（progress-update など）を編集して良い？
- 実行時に必要な環境変数（HOME, PATH, PYTHONPATH）は？

## 6. Codex 実行条件
- `--dangerously-bypass-approvals-and-sandbox` を使って良い？
- タイムアウトは何秒が適切？600秒
- 入力上限や行長制限の希望値は？
- ログ出力先を上書きする必要はある？（SCREENPIPE_LOG_DIR）
- 追加のCodexフラグは必要？（SCREENPIPE_CODEX_FLAGS）

## 7. 受け入れ基準
- 成功判定は何を満たせばOK？
- 動作確認は誰がどこまでやる？

---

## 返信フォーマット（例）
```
OS: macOS 14.1
User: nu
Codex: codex (PATH通ってる)
Raw: /path/to/screenpipe_all/raw
Format: raw/YYYY-MM-DD/HH.md
HourlyOut: /path/to/screenpipe_all/hourly_summary
DailyOut: /path/to/70_pipeline
Logs: /path/to/logs
OldPipeline: あり（progress-update）
Scheduler: launchd OK / plist編集OK
Env: HOME, PATH, PYTHONPATH
CodexFlags: dangerously-bypass OK
Timeout: 600
LineLimit: 400
LogDir: /path/to/logs (optional)
CodexFlags: --dangerously-bypass-approvals-and-sandbox (optional)
Criteria: hourly/daily生成＋ログ無エラー
```

---

## ✅ 設定完了結果（2026-01-01 更新: VAULT内に変更）

```
OS: Windows 11 (10.0.26100)
User: PC_User
Codex: codex-cli 0.77.0 (C:\Users\PC_User\AppData\Roaming\npm\codex.cmd)
Raw: C:\ドキュメント\vault\screenpipe_all\raw
Format: raw/YYYY-MM-DD/HH.md
HourlyOut: C:\ドキュメント\vault\screenpipe_all\hourly_summary
DailyOut: C:\ドキュメント\vault\screenpipe_all\daily_summary
Logs: C:\ドキュメント\vault\screenpipe_all\logs
OldPipeline: なし（新規設定）
Scheduler: Windows Task Scheduler
  - Screenpipe-HourlySummary: 毎時実行 (Ready)
  - Screenpipe-DailySummary: 毎日00:30実行 (Ready)
Env: PATH (npm global bin含む)
CodexFlags: --dangerously-bypass-approvals-and-sandbox OK
Timeout: 600秒
LineLimit: 制限なし
Criteria: hourly/daily生成＋ログ無エラー
```

### 作成されたフォルダ構造（VAULT内）
```
C:\ドキュメント\vault\screenpipe_all\
├── raw\              # Screenpipe生ログ (YYYY-MM-DD/HH.md形式)
├── hourly_summary\   # 時間単位サマリー出力
├── daily_summary\    # 日次サマリー出力
├── logs\             # 実行ログ
└── scripts\
    ├── hourly_summary.ps1
    └── daily_summary.ps1
```

### スケジュールタスク
| タスク名 | 実行間隔 | 状態 |
|---------|---------|------|
| Screenpipe-HourlySummary | 毎時 | Ready |
| Screenpipe-DailySummary | 毎日 00:30 | Ready |

### 次のステップ
1. Screenpipeを起動してログを `C:\ドキュメント\vault\screenpipe_all\raw` に出力するよう設定
2. 動作確認：手動でスクリプトを実行してテスト
   ```powershell
   & "C:\ドキュメント\vault\screenpipe_all\scripts\hourly_summary.ps1"
   ```
