# 第9章 現代のデータスタックでのモデリング

第8章の最後で、問いの単位が変わったことを確かめた。
提供する一枚が増え、モデルを書く人が増えるほど、問われるのはテーブル一枚の形ではなく、staging から OBT まで並んだ変換の流れ全体をどう保つかになる。
本章では、この状況を作った**現代のデータスタック**の成り立ちを確かめたうえで、dbt のレイヤリング（staging、intermediate、marts）を決定の置き場の規約として整理し、規約でも防げずに残る指標の定義の複製への答えとして**セマンティックレイヤー**を扱う。
具体例では、ここまで育ててきたプロジェクトを規約に照らして点検し、全社売上の指標を宣言で定義する。

## 概念の解説

### 現代のデータスタックと ELT

本書は第1章から、クラウド DWH の上で dbt のモデルを書くという形で例を進めてきたが、この道具立て自体の成り立ちには立ち入らずにきた。
クラウド DWH を中心に据え、データの取り込み、変換、可視化をそれぞれ専業の道具が分担する構成は、2010 年代後半から**現代のデータスタック**（Modern Data Stack）という通称で呼ばれている[^mds-name]。
規約を論じる前に、この構成が変換の作り方をどう変えたかを確かめる。

転換の中身は、処理の順序の入れ替えである。
かつての標準は **ETL**、すなわち抽出（Extract）したデータを DWH の外の変換サーバで整形（Transform）してから、結果だけを DWH にロード（Load）する順序だった。
DWH の計算資源は高価で、生データを置いておく容量も貴重だったから、外で整えた結果だけを積むのが合理的だった。
第8章で確かめたとおり、クラウド DWH はこの前提を崩した。
容量が安くなり計算が従量課金になった結果、先に生のままロードし、変換は DWH の中で SQL として行う **ELT** の順序が合理的になった。

変換が DWH 内の SQL になったことの帰結が、変換の管理の形である。
変換はテキストファイルの集合になり、Git でバージョン管理し、レビューし、CI で検査できる。
dbt は、この SQL の集合に ref による依存の宣言とテストを与える実行系であり、本書が各章で書いてきた models と tests は、この働き方の実践だった。
ソフトウェアエンジニアリングの実践を分析用データの変換に適用するこの職能は、**アナリティクスエンジニアリング**と呼ばれる[^ae]。

### モデルの増殖と規約の必要

ELT は、モデリングの成果物も変えた。
ここまでの章の設計は、ER 図や DDL の図面としてではなく、すべて変換のコード（モデル）とその宣言（sources、tests）として書かれてきた。
テーブルは変換の出力であり、設計の対象は一枚ずつの形に加えて、ref がつなぐ依存グラフ（DAG）の全体になっている。

このとき、変換が安く自由になったこと自体が、新しい問題を生む。
モデルは SELECT 文一つで一枚増やせるから、分析の要望のたびに足された一枚が積もっていく。
規約なしに育った DAG では、同じ結合や同じ読み替えが何度も書かれ、どの数字がどのモデルで決まるのかを誰も追えなくなる。
第6章の独立データマートのサイロは、マートを立てる重さがあってなお部門の数だけ起きた。
ELT はその重さを取り除いたから、同じ症状は、モデル一枚の細かさで、日々の開発の中で起きるようになった。

処方は第6章と同じで、決定を一度だけ行う場所を用意することである。
違いは、場所が製品やサーバの壁で仕切られなくなったことにある。
どの層も同じリポジトリの中のディレクトリにすぎないから、場所の仕切りは、書き手が守る**規約**として与えるほかない。
層の規約とは、どの種類の決定をどの層のモデルに書くか、の合意である。

### 三層の規約

第6章では、dbt の staging、intermediate、marts の三層を、Inmon と Kimball の混成として役割の面から紹介した。
ここでは同じ三層を、各層に置いてよい決定と置いてはならない決定の線引きとして述べ直す[^style-guide]。

- **staging**：ソーステーブルと 1 対 1 に対応させる。置いてよいのは、列名と型の統一、コードの読み替えといった、行を増減させない整形（第7章の語彙でいえば hard rule）である。結合と集約は置かない。source() の参照は staging だけに許す。
- **intermediate**：複数の marts モデルから再利用される変換と、一枚に収めると読めなくなる変換の分割を置く。利用者には見せない。必要が現れるまで作らない。
- **marts**：利用者に提供する層である。グレインの宣言、適合ディメンション、履歴の表現を担うスタースキーマ（fct_、dim_）と、そこから導出する提供用の一枚（obt_）を置く。
- 統合層を立てる場合（第7章の Vault）は、staging と marts の間に挟む。

線引きには、それぞれ買っているものがある。
staging の 1 対 1 は、ソースの構造変更の影響を staging の中に堰き止める。
source() の参照を staging に限るのは、ソースが変わったとき確かめる場所を一箇所にするためである。
そして依存の向きを一方向（staging から marts へ）に限れば、変更の影響が届く範囲は DAG の下流だけと読める。

規約のもう半分は命名である。
stg_、int_、fct_、dim_、obt_ の接頭辞は、モデル名だけでそのモデルの約束（1 対 1 の写しか、提供用の一枚か）を運ぶ。
数百枚に育ったプロジェクトでは、読み手が全モデルの中身を確かめるわけにはいかないから、名前が約束を運ぶことは飾りではなく、規約が規模に耐えるための条件である。

物理モデルのレベルの決定も、層の規約に含める。
staging は実体を持たない view、統合層は追記の incremental（第7章）、marts は table か incremental（第8章）、という要領である。
第1章では物理モデルの決定をテーブルごとに下すものとして紹介したが、層で既定を決めておけば、モデル一枚ごとの判断は既定から外れる例外の宣言だけになる。

規約は、破っても dbt の実行は通る。
ref の循環はエラーになるが、marts が source() を直接読んでも、stg_ のモデルが集約を行っても、dbt は層を知らないから止めようがない。
だから規約も検査に翻訳する。
DAG と命名を検査するパッケージがあり、ソースの直参照、層をまたぐ参照、命名の逸脱を一覧できる[^evaluator]。
グレインの宣言を unique テストに翻訳してきた本書の要領が、テーブルの宣言からプロジェクト構造の宣言へ広がった形である。

### テーブルに焼き込めない指標の定義

ここまでの規約で、変換の決定には置き場が決まった。
それでも複製され続ける決定が一つ残る。
**指標**、すなわち売上や出荷率のような、業務を測る数値の合意された計算式である。
第4章のメジャーとは区別が要る。
メジャーはグレインを持つ行の上の値（明細 1 行の amount）であり、指標はメジャーを切り口で集計して初めて値になる（先月の売上、書籍別の売上）。

指標の定義は、テーブルの列として保存できない。
テーブルは一つのグレインを宣言して持つ（第4章）。
一方、指標の値は、どの切り口で集計するかが決まって初めて一つに定まり、その切り口は問いの側が選ぶ。
値を行として持ちたければ切り口の組み合わせごとの集計テーブルが要り（第8章の脚注で触れた OLAP キューブの形）、あり得る問いを提供側が列挙し尽くすことはできない。
だから指標の計算式は問い合わせの側に残り、ダッシュボードの SQL、BI ツールの設定、スプレッドシートの式へ、問いの数だけ複製される。

複製された計算式は、複製されたロジックの常として分岐する。
キャンセルを除くか、送料を含めるか、月をどの日付で区切るかという第6章で挙げた決定は、どれも指標の定義の一部であり、複製のたびに別々に下される。
比率の指標は特に危うい。
平均単価は金額の合計を数量の合計で割る（第4章）と決めても、単価の平均という誤った複製は、SQL としては何の警告も出さずに動く。
marts をどれだけ規約で整えても、この複製は marts の外（問い合わせとその置き場）で起きるから、テーブル側の設計では防げない。
第8章の OBT は「正しい結合」の複製を一枚に畳んで消したが、「正しい集計」は畳めずに残っている。

### セマンティックレイヤー

この問題への答えは、BI ツールの中には以前からあった。
テーブルに意味づけ（この列は切り口である、この列はこう集計する）を定義しておき、利用者の操作から SQL を生成する定義層である[^lookml]。
定義層を持つ BI の中では、指標の計算式は定義に一度だけ書かれ、ダッシュボードの数だけ複製されることはない。
ただしその定義は製品の中に閉じている。
BI が二つになれば、あるいはノートブックやスプレッドシートから同じ指標が要れば、複製が戻ってくる。

**セマンティックレイヤー**は、この定義層を特定の BI から切り離し、独立した層としたものである。
指標と切り口の定義を宣言として一元管理し、「この指標を、この切り口で」という問いを受けて SQL にコンパイルし、DWH に発行して結果を返す。
BI もノートブックも社内アプリも、この層に指標の名前で問い合わせる限り、同じ定義から生成された同じ数字を受け取る[^headless]。

宣言は、大きく二種類からなる。
一つは、marts のテーブルへの意味づけ（**セマンティックモデル**）であり、テーブルごとに、結合に使うキー（エンティティ）、切り口（ディメンション）、集計の材料（メジャー）を宣言する。
もう一つは、指標そのものの定義であり、メジャーの集計方法、対象を絞る条件、指標同士の組み合わせ（比率や和）を宣言する。
前者の項目の並びには見覚えがあるはずである。
グレイン、キー、切り口、測る数値は、第4章の設計プロセスが決めてきたことと同じ並びである。
セマンティックレイヤーはディメンショナルモデリングの代替ではなく、その成果を機械可読の宣言に写し、問い合わせの生成に使えるようにした層である。

第8章の OBT とは、狙いが重なるので整理しておく。
どちらも、利用者に規約の知識（正しい結合、正しい集計）を求めずに済ませるための仕組みである。
OBT は結合を済ませた表という物を渡すから、表を入力に要求する道具（スプレッドシート、機械学習）に効く。
セマンティックレイヤーは問いのたびに SQL を生成するから、指標の定義の一貫性に効く。
役割が違うので置き換えではなく併存になり、第8章の採用の判断はそのまま残る。

採用の判断も条件付きで述べておく。
効くのは、同じ指標を使う提供先が複数あり、指標と利用部門の数が多い場面である。
BI が一つに定まっているなら、その BI の定義層で同じ一元化ができ、独立した層を挟む理由は薄い。
定義言語の標準はまだなく、製品を替えれば宣言は書き直しになる。
宣言から生成できる問いの形にも制約があり、分析者が書く自由な SQL を置き換えるものではない。

## 具体例

書籍オンラインストアのデータ基盤は、第7章の統合層の導入を経て、モデルの数が数十枚に育った。
電子書籍ストアの開発も進んでおり、データチームには二人目、三人目のエンジニアが加わることになった。
一人で育てているあいだは頭の中にあった決まりごとを規約として書き出し、プロジェクトの構造をそれに合わせて整えるときである。

### プロジェクトの全景

まず、ここまでの章で作ってきたモデルを層に並べ、全景を確かめる。

```text
models/
├── staging/
│   ├── shop/  stg_customers, stg_orders, stg_order_items,
│   │          stg_books, stg_authors, stg_book_authors
│   ├── wms/   stg_shipments, stg_shipment_items, stg_carriers
│   └── pos/   stg_pos_products, stg_pos_sales, stg_pos_sale_items
├── vault/     hub_ 4 枚、link_ 4 枚、sat_ 6 枚（第7章）
├── intermediate/
└── marts/     dim_date, dim_customers, dim_books, dim_carriers,
               fct_order_items, fct_shipments, fct_store_sales,
               obt_order_items
```

ソースごとのサブディレクトリ、接頭辞、依存の向きは、おおむね規約のとおりに育っている。
これは偶然ではなく、癖の吸収は入り口で、定義は marts で一度だけ、という各章の判断が、規約と同じ処方を追ってきた結果である。
それでも、規約の目で点検すると二つの逸脱が見つかる。

### 規約に照らした点検

一つ目は、staging に置かれた結合である。
第6章の stg_shipment_items は、wms の出荷明細に stg_books を結合し、ISBN を book_id へ読み替えていた。
語彙をそろえてから下流に渡すという第6章の判断は変わらないが、規約は staging に他モデルとの結合を許さない。
結合を含むモデルに stg_ の名が付いたままだと、「stg_ はソースの 1 対 1 の写しである」という約束をモデル名から信じられなくなり、名前が約束を運ぶという規約の利得が失われる。
そこで stg_shipment_items は wms の写しに戻し、読み替えの結合は同じ SQL のまま int_shipment_items として intermediate へ移す[^shipments-vault]。
変わるのは置き場と名前だけだが、この整理の目的が名前の運ぶ約束の回復なのだから、それで足りている。

二つ目は、同じ変換の重複である。
書籍と著者の対応を書籍 1 冊に畳む集約が、第4章の dim_books（表示順で連結した文字列）と第8章の obt_order_items（構造体の配列）の二箇所に書かれている。
対応表の結合と表示順の決定が二回現れているから、著者の並び順の規則を変えたとき、片方だけが直って二つの著者名表記が食い違う事故が起きうる。
複数の marts モデルから再利用される変換は、intermediate の出番である。
第6章では「必要に応じて置く」層とだけ述べたが、その必要がここで初めて現れた。

```sql
-- models/intermediate/int_book_authors.sql
SELECT
    bk.isbn,
    ARRAY_AGG(
        STRUCT(a.name AS author_name, ba.position AS position)
        ORDER BY ba.position
    ) AS authors,
    STRING_AGG(a.name, ', ' ORDER BY ba.position) AS author_names,
    COUNT(a.author_id) AS author_count
FROM {{ ref('stg_book_authors') }} AS ba
JOIN {{ ref('stg_books') }}   AS bk ON bk.book_id = ba.book_id
JOIN {{ ref('stg_authors') }} AS a  ON a.author_id = ba.author_id
GROUP BY bk.isbn
```

dim_books と obt_order_items は、このモデルからそれぞれ必要な列（連結文字列と人数、配列）を写すだけになる。
表示順と区切り文字の決定は、このモデルだけに書かれている。

点検を目視で続けるわけにはいかないので、規約の検査はパッケージに任せる[^evaluator]。
ソースの直参照や命名の逸脱が CI で検出されるようになれば、三人になったチームがモデルを足していっても、全景の読みやすさは保たれる。

### 「売上」の食い違い

構造を整えたところへ、経営企画室から相談が届いたとしよう。
役員会に出している月次の全社売上が、マーケティングチームの月次売上レポートと毎月合わない。
調べると、どちらの数字にも計算の誤りはない。
マーケティングのレポートは obt_order_items の集計で、オンラインストアの売上だけを数えている。
経営企画のダッシュボードは、自分で書いた SQL で店舗の販売（fct_store_sales）を足し込んでいる。
二つの部門は、「売上」という同じ名前で別の量を指していた。

この食い違いは、第6章のサイロと似て非なるものである。
第6章の食い違いは変換ロジックの重複から生まれ、統合と定義を一度だけ行う層で抑えた。
今度は marts に誤りがなく、検査もすべて通ったうえで、marts の外の問い合わせの側で「売上」の対象範囲という決定が複製され、分岐している。
概念の解説で述べたとおり、指標の定義の複製はテーブルの規約では防げない。
指標を宣言に出す。

### 指標の宣言

やることは二段である。
まず、混同されていた量に別の名前を与える。
オンライン売上、店舗売上、その和の全社売上は、三つの別の指標である。
次に、それぞれの定義を宣言として一箇所に書く。
宣言の前半は、marts のテーブルへの意味づけ（セマンティックモデル）である[^sl-syntax]。

```yaml
# models/semantic/_semantic_models.yml（主要な宣言の抜粋）
semantic_models:
  - name: order_items
    model: ref('fct_order_items')
    defaults:
      agg_time_dimension: ordered_date
    entities:
      - name: book
        type: foreign
        expr: book_hk
    dimensions:
      - name: ordered_date
        type: time
    measures:
      - name: online_amount
        expr: amount
        agg: sum

  - name: store_sales
    model: ref('fct_store_sales')
    defaults:
      agg_time_dimension: sold_date
    entities:
      - name: book
        type: foreign
        expr: book_hk
    dimensions:
      - name: sold_date
        type: time
    measures:
      - name: store_amount
        expr: amount
        agg: sum

  - name: books
    model: ref('dim_books')
    entities:
      - name: book
        type: primary
        expr: book_hk
    dimensions:
      - name: title
        type: categorical
```

書いている内容は、第4章から積み上げてきた設計の宣言の写しである。
entities の book は、ファクトとディメンションを book_hk で結ぶという、relationships テストに書いてきたのと同じ参照の宣言であり、コンパイラはこれを結合の生成に使う。
時間軸の既定（注文は注文日で、店舗販売は販売日で数える）も、ここに一度だけ書かれる[^metric-time]。

宣言の後半が、指標の定義である。

```yaml
# models/semantic/_metrics.yml
metrics:
  - name: online_revenue
    label: オンライン売上
    type: simple
    type_params:
      measure: online_amount

  - name: store_revenue
    label: 店舗売上
    type: simple
    type_params:
      measure: store_amount

  - name: total_revenue
    label: 全社売上
    type: derived
    type_params:
      expr: online_revenue + store_revenue
      metrics:
        - name: online_revenue
        - name: store_revenue
```

total_revenue は、二つの指標の和として定義した派生の指標である。
「全社売上とはオンライン売上と店舗売上の和である」という、今回の食い違いの核心だった決定は、この数行だけに書かれている。

### 宣言からコンパイルされる SQL

利用者やツールがこの層に発行するのは、SQL ではなく指標と切り口の組である。
「total_revenue を、月と書籍タイトルで」という問いに対して、セマンティックレイヤーは次の形の SQL をコンパイルし、DWH に発行する[^sl-query]。

```sql
-- コンパイル結果の要旨
WITH online AS (
    SELECT
        DATE_TRUNC(f.ordered_date, MONTH) AS month,
        b.title,
        SUM(f.amount) AS online_revenue
    FROM fct_order_items AS f
    JOIN dim_books AS b ON b.book_hk = f.book_hk
    GROUP BY month, title
),

store AS (
    SELECT
        DATE_TRUNC(f.sold_date, MONTH) AS month,
        b.title,
        SUM(f.amount) AS store_revenue
    FROM fct_store_sales AS f
    JOIN dim_books AS b ON b.book_hk = f.book_hk
    GROUP BY month, title
)

SELECT
    COALESCE(o.month, s.month) AS month,
    COALESCE(o.title, s.title) AS title,
    COALESCE(o.online_revenue, 0) + COALESCE(s.store_revenue, 0)
        AS total_revenue
FROM online AS o
FULL OUTER JOIN store AS s
    ON  s.month = o.month
    AND s.title = o.title
```

この形には見覚えがあるはずである。
各ファクトを共通のディメンション属性でそれぞれ集計してから突き合わせる、第6章で手書きしたドリルアクロスの定石が、宣言から生成されている。
書き手が定石を知っている必要はなく、グレインの違う二つのファクトの直接結合という事故は、生成の過程に存在しないから起きない。
経営企画のダッシュボードもマーケティングのレポートも、この層に total_revenue と online_revenue を問い合わせる形に改めれば、二つの数字は定義ごと分かれ、同じ名前が別の量を指すことはなくなる。

### 決定の置き場の全景

最後に、本章で整えた構成を、これまでの章の上に置いて見渡す。
各章の技法はテーブルの形として学んできたが、どれも「この決定をどこに一度だけ書くか」への答えでもあった。

| 決定 | 置き場 | 主に扱った章 |
| --- | --- | --- |
| ソースの癖の吸収（列名、型、hard rule） | staging | 第6章 |
| ソースをまたぐ事実と履歴の保存 | 統合層（Raw Vault） | 第7章 |
| 解釈の選択（soft rule）、グレイン、適合ディメンション、履歴の表現 | marts のスタースキーマ | 第4章から第7章 |
| 再利用される中間変換 | intermediate | 第6章、本章 |
| 提供の形（結合済みの一枚） | OBT | 第8章 |
| 指標の計算式と対象範囲 | セマンティックレイヤー | 本章 |

どの決定も一度だけ書かれ、層と接頭辞がその所在を教える。
統合と共通の定義を一度だけ行う場所を用意するという処方（第6章）は、Inmon と Kimball の時代から変わっていない。
現代のデータスタックが変えたのは場所の作り方であり、かつて製品とサーバの壁だった層の仕切りは、いまはリポジトリの中の規約と宣言になっている。

本書はここまで、一貫してリレーショナルモデルの世界を歩いてきた。
構造はテーブルで持ち、問いは SQL と結合で組み立てる前提である。
第10章では、この前提を共有しないデータベース群、NoSQL でのモデリングを扱う。
結合という道具を持たない世界では、問いの形に合わせて構造をあらかじめ畳んでおくという第8章の発想が、選択肢の一つではなく設計の出発点になる。

## 参考文献

- dbt Labs, "How we structure our dbt projects". https://docs.getdbt.com/best-practices/how-we-structure/1-guide （三層構成と命名規約の公式ガイド。第6章に続き、本章の規約の出典）
- dbt Labs, "About MetricFlow", dbt documentation. https://docs.getdbt.com/docs/build/about-metricflow （dbt Semantic Layer の宣言の構文と SQL 生成の仕組み）
- Benn Stancil, "The missing piece of the modern data stack", 2021. https://benn.substack.com/p/metrics-layer （指標の定義層の不在を指摘し、セマンティックレイヤーをめぐる議論の起点になった記事）
- Amit Pahwa et al., "How Airbnb Achieved Metric Consistency at Scale", The Airbnb Tech Blog, 2021. https://medium.com/airbnb-engineering/how-airbnb-achieved-metric-consistency-at-scale-f23cc53dea70 （社内指標基盤 Minerva の事例。指標の一元管理を大規模に実装した先行例）
- Tristan Handy, "The Modern Data Stack: Past, Present, and Future", dbt Blog, 2020. https://www.getdbt.com/blog/future-of-the-modern-data-stack （現代のデータスタックという語の背景と経緯を当事者がまとめた記事）

[^mds-name]: 方法論の術語ではなく、ベンダーとコミュニティの中で定着した通称であり、厳密な範囲の定義はない。典型的には、取り込み（Fivetran、Airbyte など）、クラウド DWH（BigQuery、Snowflake、Redshift など）、変換（dbt）、BI（Looker、Tableau など）の組み合わせを指す。

[^ae]: アナリティクスエンジニアという職能名は dbt Labs（旧 Fishtown Analytics）が広めた。データエンジニア（基盤と取り込み）とデータアナリスト（分析）の間に立ち、分析に使える形へのデータの変換を受け持つ役割とされる。

[^style-guide]: 本文の線引きは、参考文献に挙げた公式ガイドの推奨をまとめたものである。規約はプロジェクトごとに調整してよく、実際、コードの読み替えをどこまで staging に許すか、結合をどこから禁じるかには流儀の幅がある。

[^evaluator]: dbt Labs が提供する dbt-project-evaluator パッケージが代表である。公式ガイドの構成からの逸脱（source の直参照、staging 同士の依存、命名の不一致など）を検査項目として実装しており、CI で走らせて使う。

[^shipments-vault]: 出荷の主題を第7章の要領で Vault に収める拡張を選ぶなら、この読み替えは Link のロードの結合が引き受けるので（第7章の link_order_lines が book_id から ISBN への読み替えをそう行っていた）、int_shipment_items 自体が要らなくなる。

[^lookml]: 代表は Looker の LookML で、テーブルと列への意味づけの定義から問い合わせを生成する。Power BI のセマンティックモデル（DAX のメジャー定義）も同じ役割の定義層である。

[^headless]: BI の画面を持たず、定義と SQL 生成だけを提供することから、ヘッドレス BI とも呼ばれる。独立した層の実装には dbt Semantic Layer（MetricFlow）や Cube などがあり、参考文献に挙げた Airbnb の Minerva のような社内基盤の先行例もある。

[^sl-syntax]: 本文の YAML は dbt Semantic Layer（MetricFlow）の構文で、紙面では主エンティティなど一部の宣言を省いている。意味づけと指標という宣言の構成は製品をまたいで共通だが、定義言語は製品ごとに異なる。

[^metric-time]: MetricFlow は、各セマンティックモデルの既定の時間軸（agg_time_dimension）を metric_time という共通の名前に束ね、問い合わせの時間の切り口として使う。ファクトごとにどの日付で数えるかという決定が、問い合わせの側から宣言の側へ移る。

[^sl-query]: dbt Semantic Layer の CLI では dbt sl query --metrics total_revenue --group-by metric_time__month,book__title のような形になる。BI ツールからは JDBC などの API で同じ問い合わせを発行する。

## 演習と音声

- [第9章 演習問題](exercises/09-modern-data-stack.md)：四択で章の理解を確認できる。
- [読み上げ音声（mp3）](audio/09-modern-data-stack.mp3)：聴いて復習できる（[原稿](audio-scripts/09-modern-data-stack.md)）。
