# learning-docs

データエンジニアの視点で書いた学習教材を、教材ごとにまとめて公開するリポジトリである。
教材は `docs/` 直下のディレクトリ単位で管理し、各教材は章ごとの本文、四択の演習問題、ハンズフリー学習のための読み上げ音声で構成する。

## 教材一覧

| 教材 | ディレクトリ | 内容 |
| --- | --- | --- |
| [データモデリング](docs/data-modeling/index.md) | `docs/data-modeling/` | 概念モデルから正規化、ディメンショナルモデリング、Data Vault、NoSQL までの全 11 章 |

教材の追加や章の執筆の手順は [AUTHORING.md](AUTHORING.md) にまとめている。

## Web サイト

全文を <https://denzow.github.io/learning-docs/> で公開している。
公開版は main の内容で、develop の内容は
<https://denzow.github.io/learning-docs/develop/> でプレビューできる。
MkDocs（Material テーマ）でビルドし、main または develop への push を契機に
GitHub Actions で両ブランチをビルドして GitHub Pages へ自動デプロイされる。
公開版の更新は develop から main へのマージで行う。

サイトでは教材ごとにタブが分かれ、サイドバーにその教材の章が並ぶ。
演習問題のページでは、ブラウザ上で選択肢を選ぶと正誤と解説がその場で表示される。
読み上げ原稿のページでは、再生中の一文がハイライトされ、再生位置はブラウザに保存される。

ローカルでは次のようにプレビューできる。

```bash
pip install -r requirements.txt
mkdocs serve
```

## リポジトリの構成

```
docs/
  index.md            サイトのトップページ（教材一覧）
  css/, js/           演習の解答 UI と音声プレイヤーの機能（教材をまたいで共通）
  <教材>/             教材ごとのディレクトリ
    index.md          教材のトップページ（目次の表）
    NN-<slug>.md      章の本文
    exercises/        章ごとの演習問題
    audio-scripts/    章ごとの読み上げ原稿
    audio/            読み上げ音声（mp3）と文ごとのタイミング（timing.json）
hooks/                MkDocs の hook。nav の展開、章末の導線、旧 URL の転送
templates/            章、演習問題、読み上げ原稿、教材トップページの雛形
scripts/              教材と章の雛形生成、音声の生成
mkdocs.yml            サイトの設定。教材は nav に 1 行ずつ登録する
```

## 音声読み上げ

各章の音声は、本文をそのまま読むのではなく、コードブロックや表の要点を話し言葉で説明する聴取用の原稿から生成している。
音声は [edge-tts](https://pypi.org/project/edge-tts/) の日本語音声で合成した機械音声である。
原稿を更新したら `scripts/generate-audio.sh <教材>` で再生成できる。
mp3 を差し替えずに文ごとのタイミングだけ作り直すときは `--timings-only` を付ける。
