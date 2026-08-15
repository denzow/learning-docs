# study-for-data-modeling

データエンジニアの視点でデータモデリングを学ぶためのドキュメント群である。
各章は `docs/` 配下の Markdown として蓄積する。

各章は、概念の解説、具体例（SQL や dbt モデル）、参考文献の三部構成とする。
例は特定製品に依存させず、BigQuery や Snowflake 相当の一般的な SQL で書く。

## 目次

1. [データモデリングの全体像](docs/01-overview.md)
2. [リレーショナルモデルの基礎](docs/02-relational-basics.md)
3. [正規化](docs/03-normalization.md)
4. [ディメンショナルモデリング](docs/04-dimensional-modeling.md)
5. [Slowly Changing Dimensions](docs/05-slowly-changing-dimensions.md)
6. [DWH アーキテクチャ](docs/06-dwh-architecture.md)
7. [Data Vault](docs/07-data-vault.md)
8. [ワイドテーブルと One Big Table](docs/08-one-big-table.md)
9. [現代のデータスタックでのモデリング](docs/09-modern-data-stack.md)
10. [NoSQL のデータモデリング](docs/10-nosql-modeling.md)
11. [総合演習](docs/11-capstone.md)

## 演習問題

第 1〜10 章には、章の理解を確認する四択の演習問題（解答と解説つき）がある。
第 11 章は章全体が総合演習のため対象外とする。

1. [第1章 演習問題](docs/exercises/01-overview.md)
2. [第2章 演習問題](docs/exercises/02-relational-basics.md)
3. [第3章 演習問題](docs/exercises/03-normalization.md)
4. [第4章 演習問題](docs/exercises/04-dimensional-modeling.md)
5. [第5章 演習問題](docs/exercises/05-slowly-changing-dimensions.md)
6. [第6章 演習問題](docs/exercises/06-dwh-architecture.md)
7. [第7章 演習問題](docs/exercises/07-data-vault.md)
8. [第8章 演習問題](docs/exercises/08-one-big-table.md)
9. [第9章 演習問題](docs/exercises/09-modern-data-stack.md)
10. [第10章 演習問題](docs/exercises/10-nosql-modeling.md)

## 音声読み上げ

各章には、ハンズフリーで学習するための読み上げ音声（mp3、1 章 13〜20 分）がある。
本文をそのまま読むのではなく、コードブロックや表の要点を話し言葉で説明する聴取用の原稿を
`docs/audio-scripts/` に書き下ろし、そこから `docs/audio/` の mp3 を生成している。

音声は [edge-tts](https://pypi.org/project/edge-tts/) の日本語音声で合成した機械音声である。
原稿を更新したら `scripts/generate-audio.sh` で再生成できる。

1. [第1章 音声](docs/audio/01-overview.mp3)（[原稿](docs/audio-scripts/01-overview.md)）
2. [第2章 音声](docs/audio/02-relational-basics.mp3)（[原稿](docs/audio-scripts/02-relational-basics.md)）
3. [第3章 音声](docs/audio/03-normalization.mp3)（[原稿](docs/audio-scripts/03-normalization.md)）
4. [第4章 音声](docs/audio/04-dimensional-modeling.mp3)（[原稿](docs/audio-scripts/04-dimensional-modeling.md)）
5. [第5章 音声](docs/audio/05-slowly-changing-dimensions.mp3)（[原稿](docs/audio-scripts/05-slowly-changing-dimensions.md)）
6. [第6章 音声](docs/audio/06-dwh-architecture.mp3)（[原稿](docs/audio-scripts/06-dwh-architecture.md)）
7. [第7章 音声](docs/audio/07-data-vault.mp3)（[原稿](docs/audio-scripts/07-data-vault.md)）
8. [第8章 音声](docs/audio/08-one-big-table.mp3)（[原稿](docs/audio-scripts/08-one-big-table.md)）
9. [第9章 音声](docs/audio/09-modern-data-stack.mp3)（[原稿](docs/audio-scripts/09-modern-data-stack.md)）
10. [第10章 音声](docs/audio/10-nosql-modeling.mp3)（[原稿](docs/audio-scripts/10-nosql-modeling.md)）
11. [第11章 音声](docs/audio/11-capstone.mp3)（[原稿](docs/audio-scripts/11-capstone.md)）
