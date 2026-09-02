# データ分析のための統計入門

データ分析の実務で使う統計の考え方を、データエンジニアとデータアナリストの視点で学ぶためのドキュメント群である。
記述統計から推定と検定、回帰、A/B テスト、因果推論、時系列までを、分析基盤に蓄積されたデータに対して使う場面に沿って解説する。
各章は、概念の解説、具体例（SQL と Python）、参考文献の三部構成とする。
集計は特定製品に依存しない一般的な SQL で、検定や回帰は Python（pandas、SciPy、statsmodels）で書く。
数式は LaTeX を使わず、言葉と簡単な記号、コードで表す。

題材には、データモデリングの教材と同じ書籍のオンラインストアを使う。
注文、セッション、顧客、日次売上、A/B テストの割り当てという分析用のテーブルを章を通して使い、章同士が相互参照できるようにする。
総合演習の章だけは、別の題材（オンライン学習サービス）で通しの分析を行う。

## 目次

各章の本文、演習問題、読み上げ音声を章ごとにまとめる。
演習問題は四択で、選択肢を選ぶと正誤と解説がその場で表示される。
第 11 章の演習問題は、全章の知識を横断的に復習する全 30 問の総合演習問題である。
音声は聴取用の読み上げ原稿から生成した mp3 で、移動中などのハンズフリー学習に使える。

| 章 | 本文 | 演習問題 | 音声 |
| --- | --- | --- | --- |
| 第1章 | [データ分析における統計の役割](01-role-of-statistics.md) | [演習問題](exercises/01-role-of-statistics.md) | [mp3](audio/01-role-of-statistics.mp3)（[原稿](audio-scripts/01-role-of-statistics.md)） |
| 第2章 | [記述統計と分布の要約](02-descriptive-statistics.md) | [演習問題](exercises/02-descriptive-statistics.md) | [mp3](audio/02-descriptive-statistics.mp3)（[原稿](audio-scripts/02-descriptive-statistics.md)） |
| 第3章 | [確率分布](03-probability-distributions.md) | [演習問題](exercises/03-probability-distributions.md) | [mp3](audio/03-probability-distributions.mp3)（[原稿](audio-scripts/03-probability-distributions.md)） |
| 第4章 | [標本と推定](04-estimation.md) | [演習問題](exercises/04-estimation.md) | [mp3](audio/04-estimation.mp3)（[原稿](audio-scripts/04-estimation.md)） |
| 第5章 | [仮説検定の考え方](05-hypothesis-testing.md) | [演習問題](exercises/05-hypothesis-testing.md) | [mp3](audio/05-hypothesis-testing.mp3)（[原稿](audio-scripts/05-hypothesis-testing.md)） |
| 第6章 | [代表的な検定手法](06-common-tests.md) | [演習問題](exercises/06-common-tests.md) | [mp3](audio/06-common-tests.mp3)（[原稿](audio-scripts/06-common-tests.md)） |
| 第7章 | [相関と回帰分析](07-correlation-and-regression.md) | [演習問題](exercises/07-correlation-and-regression.md) | [mp3](audio/07-correlation-and-regression.mp3)（[原稿](audio-scripts/07-correlation-and-regression.md)） |
| 第8章 | [A/B テストの設計と落とし穴](08-ab-testing.md) | [演習問題](exercises/08-ab-testing.md) | [mp3](audio/08-ab-testing.mp3)（[原稿](audio-scripts/08-ab-testing.md)） |
| 第9章 | [因果推論の入門](09-causal-inference.md) | [演習問題](exercises/09-causal-inference.md) | [mp3](audio/09-causal-inference.mp3)（[原稿](audio-scripts/09-causal-inference.md)） |
| 第10章 | [時系列データの分析](10-time-series.md) | [演習問題](exercises/10-time-series.md) | [mp3](audio/10-time-series.mp3)（[原稿](audio-scripts/10-time-series.md)） |
| 第11章 | [総合演習](11-capstone.md) | [総合演習問題](exercises/11-capstone.md) | [mp3](audio/11-capstone.mp3)（[原稿](audio-scripts/11-capstone.md)） |
