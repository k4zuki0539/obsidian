---
source: "https://letter.kasumi-days.com/p/copilot?rid=pmZzcy6UPvYj&sid=RwlzSuKoPh53"
---
# Summary



# Highlights


**主な活用例**

　・メモを元に、X（旧Twitter）の投稿、ブログ記事、メルマガの原稿などを瞬時に作成

　・要約の作成や、文章構成、スペルチェック

Obsidianで使えるAIプラグインにはいくつか選択肢がありますが、**代表的なものに「Smart Composer」と「Copilot」があります 。**

Smart ComposerとCopilotの違い

Copilot: 開いているノートに加え、関連性の高い他のノートを探し出す

【実演】Copilotの導入〜使い方

**①Google AI StudioでAPIキーを取得する  
②ObsidianにCopilotを設定する  
③Copilotを使う**

①：Google AI StudioでAPIキーを取得する

②：ObsidianにCopilotを設定する

Copilotプラグインのインストール

Obsidianの「設定」 → 「コミュニティプラグイン」を開き、「Copilot」をインストールして有効化します。

初期設定

「Advanced」タブにある「Enable Encryption」をオン

「Basic」タブを開き、API Key: Set Key→Google GeminiのAPIキーをコピペ

Default Chat Model→Gemini 2.5 Flashなど、最新かつ軽量なモデルを選択

Default Mode→Chat

- Relevant Notes:→オフ

③Copilotを使う

設定が完了すると、Obsidianのサイドバーに吹き出しのアイコンが表示されます。これをクリックすると、Copilotのチャットウィンドウが開きます 。

  
**活用例1：音声入力したメモを整形＆要約する**

要約プロンプト

↓ここからコピペしてください

{activeNote}の内容を処理してください。

1\. 音声入力で書かれた文章を整形してください。  
   - 適切に句読点を補い、読みやすいように改行してください。  
   - 元の文は残さず、整形後のみを出力してください。  
  

2\. 整形した文章をもとに要点を3〜5個にまとめ、上に要約を出してください。太字も使ってわかりやすく

3\. 出力フォーマットは必ず以下の形にしてください：

\## 要約  
\- （要点1）  
\- （要点2）  
\- （要点3）  
  
  

\## 整形後本文  
（句読点と改行を入れて整形した本文）  

**活用例2：メモからSNS投稿やブログ記事を作成する**