---
title: "Claude Skillsとは何なのか？"
source: "https://blog.lai.so/claude-skills/"
author:
  - "[[laiso]]"
published: 2025-10-18
created: 2025-11-04
description: "AnthropicがClaudeの新機能 Claude Skills （Agent Skills）を追加したと発表しました。Claude Skillsは、Markdownファイルとスクリプトで構成される「スキルフォルダ」を通じて、モデルに特定の機能や知識を拡張できる仕組みです。Claude Skills: Customize AI for your workflowsBuild custom Skills to teach Claude specialized tasks. Create once, use everywhere—from spreadsheets to coding. Available across Claude.ai, API, and Code.Box logoもともとClaudeは8月にチャットアシスタントからのコード実行環境をアップデートしていました。それまでは指示に応じてPythonコードを実行しグラフ生成やデータ分析をするちょとした用途でしたが、この時にBashコマンドをサンドボックス以下で自由に実行できる環境が構築されています。Claude"
tags:
  - "clippings"
---
==AnthropicがClaudeの新機能 **Claude Skills** （Agent Skills）を追加したと発表しました。Claude Skillsは、Markdownファイルとスクリプトで構成される「スキルフォルダ」を通じて、モデルに特定の機能や知識を拡張できる仕組みです。==

![](https://blog.lai.so/content/images/thumbnail/opengraph-illustration-1)

Claude Skills: Customize AI for your workflows

==もともとClaudeは8月にチャットアシスタントからのコード実行環境をアップデートしていました。それまでは指示に応じてPythonコードを実行しグラフ生成やデータ分析をするちょとした用途でしたが、この時にBashコマンドをサンドボックス以下で自由に実行できる環境が構築されています。==

![](https://blog.lai.so/content/images/thumbnail/opengraph-illustration-2)

Claude can now create and use files

Claude Skills はこのコード実行環境のインフラ [”Code execution tool”](https://docs.claude.com/en/docs/agents-and-tools/tool-use/code-execution-tool?ref=blog.lai.so) を活用したものです。「スキル」としてまとめたパッケージを事前にアップロードしておき、コード実行時に参照します。その時のエントリーポイントがSKILL.mdというファイルです。

SKILL.mdの先頭にはメタ情報としてフロントマター形式で名前、説明などを宣言します。Claudeは会話の開始時に現在登録されたスキル一覧をリストアップし、ユーザーのコンテキストに一致したスキルを呼び出すようにルーティングします。

## ==MCPのコンテキスト肥大化問題==

一見これはMCPサーバーへの接続によるツール登録に似ています。しかしレイヤーが少し異なります。

MCPが関数単位の登録の仕組みだとするとClaude Skills はプロジェクト単位（ディレクトリ）になります。MCPではモデルは関数の呼び出し方法を推論して結果を返し、ホストとなるエージェントの実装によってプログラムが実行されますが、Claude Skills はモデルがコード実行環境内で好き勝手にプログラムを実行した結果をユーザーに返します。これだけで２つのライフサイクルが異なることが分かります。

ではなぜAnthropicがClaude SkillsというMCPに類似した枠組みを出してきたのかというと「MCPのコンテキスト肥大化問題」に注目してリリースを読むとモチベーションが見えてきます。

MCPの仕様では登録されたMCPサーバーが返すツールのパラメータの定義を全て含め、モデルのコンテキストに乗せることで選択させます。

単純な単一のMCPサーバーでは問題はないのですが、登録するMCPサーバーや内部ツールが増えてくるとツール件数\*パラメータ数とスキーマ情報のコンテキストが上乗せされます。以下のYuta Takahashiさんの調査では、Claude Codeの利用時に使用頻度の低いMCPツールが大量の定義を常時コンテキストに載せていたそうです。

![](https://blog.lai.so/content/images/thumbnail/og-base-w1200-v2-9.png)

MCPツール棚卸しによるClaude Codeのコンテキスト最適化

問題は初期コンテキスト読み込み時だけにはとどまらず、MCPはその構造上ツール呼び出しの連鎖が発生するとコンテキストに入出力を含めることになります。ツールAの呼び出し結果を引数としてツールBの入力に使う場合モデルは通過する情報を全てコンテキストに保持する必要があります。これが複数の処理を実行するワークフローを実現するときにボトルネックになります。

これはMCPクライアントの仕様がツールをフラットな構造で保持することに起因しますが、数多くのMCPサーバーを活用するユーザーほどコンテキストウィンドウが狭くなり、ときには実行タスクの品質劣化を招きます。そのため、集約関数にまとめる、MCPサーバーの有効無効をタスク毎に切り替えるなど試行錯誤が行われています。

この問題を意識してかAnthropicはClaude Skillsについて「 **Progressive Disclosure** （必要なときに、必要な情報だけをロードする）」という特性を強調します。

> エージェント（Claude）は起動時に、インストールされている **すべてのスキル** の **名前と説明** をシステムプロンプトに **事前ロード** します。  
>   
> このメタデータは、 **「プログレッシブ・ディスクロージャー（Progressive Disclosure）」の第一レベル** です。これにより、 **コンテキスト全体にロードすることなく** 、Claudeが **各スキルをいつ使用すべきか** を知るのに十分な情報が提供されます。  
>   
> このファイルの **実際の本文（Markdown Body）第二レベル** となります。Claudeが現在のタスクに対してそのスキルが **関連性がある** と判断した場合、 `SKILL.md` の **全内容** を読み込んでコンテキストにロードします。  
>   
> [https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills?ref=blog.lai.so)

Claude Skillsは前述のフロントマターにあるdescriptionのみを読み込み、あとはMarkdownすなわちプロンプトレイヤーで解決するようにモデルを導きます。SKILL.mdを500行以下に保ちdescriptionについても”1024文字まで”という制限をつける徹底ぶりです^\[1\]。初期Twitterか。

^\[1\]: [https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview?ref=blog.lai.so)

## ==自作Skillsのつくりかた==

Anthropicは「 [skill-creator](https://github.com/anthropics/skills/tree/main/skill-creator?ref=blog.lai.so) 」というSkillsを作るスキルを用意していますが、それは素通りしてサンプルリポジトリごとエージェントに与え「既存コードを参考に新スキル○○を作成して」とバイブコーディングするのがおすすめです。

![](https://blog.lai.so/content/images/thumbnail/skills)

GitHub - anthropics/skills: Public repository for Skills

もっと言えばSKILL.mdさえあれば動作するので、全く関係のないプロジェクトのREADME.mdをSKILL.mdにリネームしてYAMLフロントマターを添えるだけでそれなりに動きます。

ちなみにAnthropicは「理論上、無制限のコンテキスト読み込みが可能」と説明していますがZIPファイルは8MBまでのファイルしかアップロードできません^\[2\]。

^\[2\]: [https://docs.claude.com/en/api/skills-guide](https://docs.claude.com/en/api/skills-guide?ref=blog.lai.so)

このためディレクトリにrequirements.txtやpackage.jsonを含めることで外部モジュールを活用します。slack-gif-creatorにPythonライブラリ活用の例、webapp-testingにPlaywright連携という実践的なサンプルがあります。

![](https://blog.lai.so/content/images/thumbnail/skills-1)

skills/slack-gif-creator at main · anthropics/skills

![](https://blog.lai.so/content/images/thumbnail/skills-2)

skills/webapp-testing/examples at main · anthropics/skills

注意点としてはCode execution toolのサンドボックスは一部のサービスからアクセスをブロックされているので依存モジュールの追加インストールが実行できないことがありました。筆者はこの環境でBunやChromiumバイナリのインストールを試みたところ失敗しました。

![](https://blog.lai.so/content/images/size/w600/2025/10/image-1.png)

Claudeでコーディングしたアプリをwebapp-testing skillで自動テストする様子

上記はClaudeチャットのウェブインターフェイスからClaude Skills を呼び出す時の話で、Claude Codeに登録して使うときはこのサンドボックスには該当しません。Claude Codeでは単にローカルでBashツールとしてコードを実行しています。

## Claude Skillsの今後

ここまで見たように、Claude Skills は「スキル名＋ディレクトリ＋プロンプト」を事前に登録（アップロード）しておき、モデルにコード実行で活用させる、というシンプルな仕組みです。これは内部的にはCode execution toolという単一のツールに全ての自律実行を委譲している状態になります。Code executionはClaudeとAnthropicのAPIサーバーにしか対応しません。

この仕組みのシステム要件は「skillsディレクトリを読み込み、コードを自律実行できる環境（サンドボックス）」です。ChatGPTにも [Code Interpreter](https://platform.openai.com/docs/guides/tools-code-interpreter?ref=blog.lai.so) というこれに相当する機能はあるので技術的には対応可能ですが、MCPとの棲み分けも含めてSkills方式が他のプラットフォームにまで普及するかどうかは分かりません。さらにClaude SkillsはMCPサーバーが持つ既存の認証済みリソースのアクセスなどのユースケースは満たせていませんので置き換わることもないでしょう。

しかし、ディレクトリ＋プロンプトというシンプルな仕組みゆえ、コーディングエージェントでは十分に転用が効くレベルのフローです。実際、Claude SkillsをClaude Codeから使う仕組みは特定のSkill登録ディレクトリに誘導するだけで、あとは既存のClaude Codeの機能で賄われています。リモートのサンドボックスでのコード実行の機能もありません。これらはCLAUDE.mdへの設定で「PDFを生成するときはこのディレクトリにあるスクリプトを使ってください」と書いておくのとそう違いはありません。また「MCPではなくコマンドラインツールの使い方をMarkdownに書いてBashツールで自動化する」というTIPSも以前からあり、その延長線にもあります。

なので本線は「Claudeのチャット機能の拡張とスクリプト配布のポータビリティ向上」になるのだと予測します。Claude Skillsに登録したコードはモバイルアプリのチャットからも使うことができますし、ZIPファイルで配布できます。おまけとしてClaude Codeからも読み込める、といった具合です。

![](https://blog.lai.so/content/images/size/w600/2025/10/image-2.png)

Claudeでコーディングしたアプリをwebapp-testing skillで自動テストする様子