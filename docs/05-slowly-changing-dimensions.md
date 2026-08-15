# 第5章 Slowly Changing Dimensions

第4章の最後で、出来上がったスタースキーマに残る宿題を確かめた。
dim_customers はソースの写しを作り直すたびに全行が現在の値へ上書きされるから、過去の注文に添えられる顧客の属性はすべて今の値になる。
「注文の時点の属性で過去を区切りたい」という問いに答えるには、変更を上書きで消さず、履歴として残す設計が要る。

ディメンションの属性の変更にどう対処するかは、Kimball が **Slowly Changing Dimensions**（SCD）として体系化している[^scd-name]。
本章では SCD の各タイプの仕組みと使い分けを扱い、第4章で予告したサロゲートキーの採番もここで具体化する。
具体例では、書籍オンラインストアに会員ランク制度を導入し、第4章の宿題だった「当時の会員ランク別の売上」に答えられる形へ顧客ディメンションを作り直す。

## 概念の解説

### ディメンションの変更という問題

ディメンションの属性は、不変ではない。
顧客は氏名やメールアドレスを変え、会員ランクは上下し、書籍は定価が改定される。
とはいえ、ファクトが毎日何千行と増えるのに比べれば、これらの変更はまれにしか起きない。
slowly（ゆっくり変化する）の名は、この頻度の非対称を指している。

まれな変更が設計の問題になるのは、ファクトとディメンションで時間の性質が違うからである。
ファクトの行はいつ起きたかが確定した出来事の記録であり、時点に固定されている。
一方、第4章までのディメンションの行は特定の時点に属さず、ただ「顧客 42 とはこういう人だ」と述べているだけである。
顧客 42 の属性が変わると、この記述が変更前と変更後のどちらを指すのかが曖昧になり、過去のファクトにどの値を添えるべきかという問いが生まれる。

どの値を添えるのが正しいかは、問いの側が決める。
現在の顧客へ案内を送るための抽出なら、添えるべきは今のメールアドレスであり、当時の値に用はない。
「当時の会員ランク別の売上」なら、今のランクを添えた集計は問いに答えていない。
正解が問いごとに違う以上、対処法は一つに定まらず、選択肢の一覧という形を取る。
Kimball はこの一覧をタイプの番号で整理した。

タイプを選ぶ単位は、テーブルではなく属性である。
同じ顧客ディメンションの中でも、メールアドレスは上書きし、会員ランクは履歴として残す、という混在が普通の姿になる。

### Type 1（上書き）と Type 0（保持）

**Type 1** は、変更された属性を新しい値で上書きする。
履歴は残らない。
第4章の dim_customers は、ソースの写しを実行のたびに作り直す設計だったから、結果として全属性が Type 1 になっていた。

用途は二つある。
一つは誤記の訂正で、間違った値は履歴として残す価値がないから、上書きが正しい。
もう一つは、当時の値を問う問いが想定されない属性である。

Type 1 が失うのは、過去の値だけではない。
過去に作った集計の再現性も失われる。
ランク別の売上レポートを先月作り、今月同じ SQL を再実行すると、その間にランクが変わった顧客の分だけ数字が動く。
数字が動いたとき、それがデータの誤りではなく上書きの仕様であることを、利用者に説明できるようにしておく必要がある。

対になる方式として、変更をそもそも受け付けない **Type 0** もある。
入会日や獲得チャネルのような、最初の値であることに意味がある属性は、ソースで値が書き換わっても元の値を守る。

### Type 2（行の追加）

当時の値で過去を区切る問いに答えるのが **Type 2** である。
属性が変わったら、行を書き換える代わりに新しい行を追加し、古い行はそのまま残す。
SCD の主役であり、単に「履歴を持つディメンション」と言えばこの方式を指すことが多い。

顧客 42 の会員ランクが regular から gold に上がると、ディメンションは次の形になる。

| customer_sk | customer_id | membership_rank | valid_from | valid_to | is_current |
|---|---|---|---|---|---|
| a13f… | 42 | regular | 2024-04-01 | 2026-07-01 | false |
| 9c2e… | 42 | gold | 2026-07-01 | 9999-12-31 | true |

この形は、三つの部品からできている。

第一の部品はサロゲートキー（customer_sk）である。
同じ customer_id を持つ行が二つできたから、customer_id はもう 1 行を特定できず、主キーの役を降りて、同一顧客の行をまとめる**自然キー**として残る。
1 行（顧客のある期間の姿）を特定するキーは、DWH 側で新たに振るほかない。
これが第4章で予告した、履歴管理のためのサロゲートキーである。

第二の部品は有効期間（valid_from と valid_to）である。
各行に、その姿が有効だった期間を持たせる。
期間は、前の行の終わりと次の行の始まりが同じ値で接する半開区間にそろえる[^half-open]。
現在の行の終端はまだ決まっていないので、遠い未来を表す番兵値で埋めるか、NULL のままにする。

第三の部品は現在行のフラグ（is_current）である。
有効期間から導ける冗長な列だが、今の姿だけが要る問い合わせを単純な等値条件で書けるようにする。

Type 2 の要は、ファクト側の持ち方にある。
ファクトの行をロードするとき、出来事の時点で有効だったディメンション行を期間で探し、そのサロゲートキーを外部キーとして書き込む。
期間の照合はロード時に一度だけ済んでいるから、問い合わせではサロゲートキーの等値結合だけで当時の値が付き、期間の条件は現れない。

現在の値で区切る問いにも、Type 2 は答えられる。
is_current の行だけに絞って自然キーで結合し直せば、全期間のファクトに今の属性が付く。
つまり Type 2 は当時の値と現在の値の両方を出せる方式であり、表現力の点では Type 1 の上位互換である。
それでも全属性を Type 2 にはしない判断があり得ることは、使い分けの節で述べる。

Type 2 のコストは、行数ではない。
第4章で見たとおりディメンションは小さく、変更もまれだから、行の増加が容量や速度の問題になることは少ない。
実際のコストは運用にある。
変更を検出し、期間を重複や欠落なく維持し、ファクトへの割り当てを正しく保つという仕事が、パイプラインに恒久的に加わる。

### Type 3（列の追加）

**Type 3** は、行ではなく列を足す。
属性の現在値の列に加えて、直前の値（または特定時点の値）を保持する列を並べて持つ。

向いているのは、全体で一斉に一度だけ起きる変更である。
Kimball が挙げる典型は営業テリトリーの再編で、再編後も「新しい区分ならどうか」「古い区分のままならどうか」と、全期間を新旧どちらの体系でも集計したいという要望に応える。
Type 2 は行が期間で分かれるため、同じ期間を新旧両方の切り口で見るこの問いには答えられない。

裏返せば、顧客ごとにばらばらの時期に何度も変わる属性には向かない。
変更のたびに列を増やすわけにはいかないから、保持できる履歴の深さは設計時に固定される。

### Type 4 以降（部品の組み合わせ）

Type 4 から 7 までは、ここまでの部品の応用と組み合わせである。

**Type 4**（ミニディメンション）は、頻繁に変わる属性群をディメンションから切り出して、別のディメンションにする。
slowly と呼べないほど速く変わる属性（購買頻度のスコアなど）を Type 2 にすると行が増えすぎるため、値を帯域に丸めた組み合わせを 1 行とする小さなテーブルを別に立て、ファクトから直接指す。

Type 5 から 7 は、Type 1 と 2 と 3 の混成である。
たとえば **Type 6** は、Type 2 の履歴行に現在値の列を重ねて持ち（1 + 2 + 3 と呼ばれる）、当時の値と現在の値を一度の結合で両方使えるようにする。
番号を暗記する必要はない。
上書き、行の追加、列の追加、切り出しという部品を押さえておけば、残りのタイプは問いに合わせた組み合わせとして読み解ける。

### タイプの使い分けと変更の検出

使い分けは、属性ごとに、どんな問いが届くかで決まる。

- 当時の値で過去を区切る問いが届く：Type 2
- 現在の値だけでよい、または誤りの訂正：Type 1
- 最初の値に意味がある：Type 0
- 一斉の再編を新旧両方の体系で見たい：Type 3
- 当時の値は要るが、変更が速すぎて Type 2 では行が増えすぎる：Type 4

表現力だけなら Type 2 が Type 1 を上回るが、だからといって全属性を無差別に Type 2 にはしない。
前節で述べた運用の仕事が増えるうえ、誰も問わない属性の変更まで行を分割し、履歴がノイズとしてすべての問い合わせに付いて回るからである。
履歴の問いが見込める属性に絞って Type 2 を適用し、残りを Type 1 に置くのが実務の均衡点になる。

どのタイプを選ぶにしても、その前段には変更の検出という仕事がある。
ソースシステムの多くは現在値しか持たず、変わったという事実を教えてくれない。
ソースの更新イベントを流してもらえるなら（**Change Data Capture**、CDC と呼ばれる）、そこから履歴を組み立てられる。
もらえないなら、DWH 側で定期的にソースを写し、前回の写しと比べて差分を見つけるほかない。
この比較には、取得の間隔より細かい変化を捉えられないという原理的な限界がある（日次の取得なら、日内に 2 回変わった中間の値は失われる）。
dbt はこの定期取得と比較を snapshot という機能として備えており、具体例ではこれを使う。

## 具体例

書籍オンラインストアに会員ランク制度が導入されたとしよう。
ソースの customers テーブルに membership_rank 列（regular、silver、gold）が追加され、購買実績に応じて値が変わる。
マーケティングからは、第4章の最後で予告した問いがそのまま届いている。
「ランク別の売上を知りたい。ただし顧客の今のランクではなく、注文した当時のランクで区切ってほしい。」

方針を属性ごとに決める。
membership_rank は、当時の値で区切る問いが現に届いているから Type 2 とする。
name と email は Type 1 のままとする。
過去の氏名やメールアドレスで売上を区切る問いは考えにくいからである。

### dbt snapshot による変更の検出

最初の仕事は変更の検出である。
ソースの customers は現在値しか持たないので、dbt の **snapshot** で履歴を蓄積する[^snapshot]。
snapshot は、実行のたびにソースの現在値を前回までの結果と比較し、指定した列が変わっていた行について、古い版の有効期間を閉じて新しい版の行を追加する。
Type 2 の行の追加を、汎用の仕組みとして肩代わりするものと言える。

```sql
-- snapshots/customers_snapshot.sql
{% snapshot customers_snapshot %}

{{ config(
    unique_key='customer_id',
    strategy='check',
    check_cols=['membership_rank'],
) }}

SELECT
    customer_id,
    name,
    email,
    membership_rank
FROM {{ source('shop', 'customers') }}

{% endsnapshot %}
```

check_cols には membership_rank だけを指定する。
Type 1 と決めた name や email の変更で版を増やさないためである。
snapshot の結果には、各版の有効期間として dbt_valid_from と dbt_valid_to の列が付く（現在の版の dbt_valid_to は NULL になる）。

snapshot を使う判断には、二つの限界を織り込んでおく。
第一に、履歴が残るのは snapshot の運用を始めた後だけであり、それ以前の変更は遡って復元できない。
第二に、概念の解説で述べたとおり、実行の間隔より細かい変化は失われる。
本例では日次実行とし、ランクの変更を日単位で捉えられれば問いに足りると判断した。

### Type 2 ディメンションの構築

snapshot の結果から dim_customers を組み立てる。

```sql
-- models/marts/dim_customers.sql
SELECT
    {{ dbt_utils.generate_surrogate_key(['s.customer_id', 's.dbt_valid_from']) }}
        AS customer_sk,
    s.customer_id,
    c.name,
    c.email,
    s.membership_rank,
    CASE
        WHEN ROW_NUMBER() OVER (
                 PARTITION BY s.customer_id ORDER BY s.dbt_valid_from
             ) = 1
        THEN TIMESTAMP '1900-01-01 00:00:00'
        ELSE s.dbt_valid_from
    END AS valid_from,
    COALESCE(s.dbt_valid_to, TIMESTAMP '9999-12-31 00:00:00') AS valid_to,
    s.dbt_valid_to IS NULL AS is_current
FROM {{ ref('customers_snapshot') }} AS s
JOIN {{ ref('stg_customers') }} AS c ON c.customer_id = s.customer_id
```

このモデルには、概念の解説で述べたことが三つ現れている。

- **タイプの混在**：Type 2 の membership_rank と有効期間は snapshot から取り、Type 1 の name と email は現在のソースの写しである stg_customers から結合で取る。過去の版の行にも、氏名とメールアドレスは常に今の値が付く。
- **サロゲートキーの採番**：dbt_utils の generate_surrogate_key で、自然キーと版の開始時刻の組から作るハッシュ値を振る[^surrogate-key]。ロードのたびに同じ入力から同じキーが再現されるので、テーブルを作り直してもファクト側の参照が壊れない。
- **期間の番兵値**：現在の版の valid_to を NULL のままにせず未来側の番兵値で埋め、後続の期間条件を COALESCE なしの単純な比較で書けるようにする。

最初の版の valid_from を過去側の番兵値に開いているのは、snapshot の第一の限界への手当てである。
最初の版の dbt_valid_from は snapshot を始めた時刻になっているから、そのままではそれより前の注文がどの版の期間にも当たらず、宙に浮く。
導入前の期間は最初の写しの値で代表させると決めて、期間を開いておく。
その期間のランクが正確には分からないという事実自体は、この手当てでは消えない。

### ファクトテーブルへのサロゲートキーの割り当て

ファクトのロードでは、注文の時刻で有効期間を照合してサロゲートキーを引く。

```sql
-- models/marts/fct_order_items.sql
SELECT
    i.order_id,
    i.line_no,
    CAST(o.ordered_at AS DATE) AS ordered_date,
    c.customer_sk,
    o.customer_id,
    i.book_id,
    i.quantity,
    i.unit_price,
    i.quantity * i.unit_price  AS amount
FROM {{ ref('stg_order_items') }} AS i
JOIN {{ ref('stg_orders') }} AS o ON o.order_id = i.order_id
JOIN {{ ref('dim_customers') }} AS c
    ON  c.customer_id = o.customer_id
    AND c.valid_from <= o.ordered_at
    AND o.ordered_at < c.valid_to
```

第4章の版との違いは、顧客への結合だけである。
customer_id の等値結合が期間の照合を伴う結合に変わり、書き込む外部キーが customer_sk になった。
期間の照合はこのロードの一度きりで、問い合わせ側には現れない。
customer_id も自然キーとして残しておく。
現在の属性で区切る問いと、ソースとの突き合わせに使うためである。

### 当時の値と現在の値の問い合わせ

届いていた問い「注文当時のランク別の売上」は、サロゲートキーの等値結合で書ける。

```sql
SELECT
    c.membership_rank,
    SUM(f.amount) AS total_amount
FROM fct_order_items AS f
JOIN dim_customers AS c ON c.customer_sk = f.customer_sk
GROUP BY c.membership_rank
ORDER BY total_amount DESC;
```

顧客 42 が regular だった時期の注文には regular の行が、gold に上がってからの注文には gold の行が付く。
期間の条件も日付の計算も現れないのは、照合をロード時に済ませてあるからである。

同じテーブルで、「今 gold の顧客が過去に上げた売上の合計」という現在値の問いにも答えられる。
is_current で絞った行に、自然キーで結合し直す。

```sql
SELECT
    SUM(f.amount) AS total_amount
FROM fct_order_items AS f
JOIN dim_customers AS c
    ON  c.customer_id = f.customer_id
    AND c.is_current
WHERE c.membership_rank = 'gold';
```

二つの問いの違いが、どちらのキーで結合するかの違いとして現れている。
当時の姿はサロゲートキーで、今の姿は自然キーで引くのが、Type 2 ディメンションの使い方の要領である。

### 履歴の検査

第4章で、スタースキーマの検査は設計の宣言そのものから決まると述べた。
Type 2 が加えた宣言は「各顧客の有効期間は重複も欠落もなく一列に並ぶ」であり、これも検査に翻訳できる。
期間が重複していると、ロードの期間結合で 1 明細が複数のディメンション行に当たり、ファクトの行が静かに複製される。
期間に欠落があると、その間の注文はどの行にも当たらず、結合で静かに落ちる。
どちらも集計を黙って狂わせる点で、第4章のグレイン検査と参照検査が防いだ事故と同型である。

列単位の検査は、第4章と同じく yml で宣言する。

```yaml
# models/marts/_marts.yml（第4章の検査への追加分）
models:
  - name: dim_customers
    columns:
      - name: customer_sk
        tests:
          - unique
          - not_null
  - name: fct_order_items
    columns:
      - name: customer_sk
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_sk
```

期間の重複のような行またぎの条件は、列単位の宣言では書けないので、SQL を直接書く検査（dbt では **singular test** と呼ぶ）にする。
違反した行だけを返す SELECT を書き、結果が 0 行なら合格である。

```sql
-- tests/assert_dim_customers_periods_do_not_overlap.sql
SELECT
    a.customer_id
FROM {{ ref('dim_customers') }} AS a
JOIN {{ ref('dim_customers') }} AS b
    ON  a.customer_id = b.customer_id
    AND a.customer_sk <> b.customer_sk
    AND a.valid_from < b.valid_to
    AND b.valid_from < a.valid_to
```

期間に欠落がないことや、現在行が 1 顧客につきちょうど 1 行であることも、同じ要領の singular test で検査できる。
snapshot が正しく動いている限りこれらの宣言は破れないはずだが、その「はず」を検査に落としておくのが、第2章から続けてきたロード後検査の方針である。

### 履歴はどこで作られるべきか

本章の設計は、履歴の獲得を DWH の入り口（snapshot）に、履歴の表現をスタースキーマのディメンションに置いた。
この配置には、第4章で述べた適合ディメンションの論点が重なる。
dim_customers を注文以外のプロセス（出荷や問い合わせ対応など）のスタースキーマとも共有するなら、履歴の設計をプロセスごとに繰り返すのではなく、共有される一枚の上で一度だけ行いたい。
どのディメンションを共有し、DWH 全体をどんな層で組み上げるかは、テーブル一枚の設計を超えたアーキテクチャの問いであり、第6章で Inmon と Kimball の方式を対比して扱う。
また、本章は履歴の獲得を dbt snapshot という道具に委ねたが、ソースから届く変更の保存そのものをモデリングの中核に据える流儀もある。
第7章の Data Vault で扱う。

## 参考文献

- Ralph Kimball, Margy Ross, *The Data Warehouse Toolkit*, 3rd Edition, Wiley, 2013.（第 5 章で SCD の Type 0〜7 を体系的に扱う。本章のタイプの整理は本書に従った）
- Kimball Group, "Slowly Changing Dimension Techniques". https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/ （タイプ別の要点を項目ごとに読める公式リファレンス）
- dbt Labs, "Snapshots". https://docs.getdbt.com/docs/build/snapshots （snapshot の設定と各 strategy の公式ドキュメント）
- Richard T. Snodgrass, *Developing Time-Oriented Database Applications in SQL*, Morgan Kaufmann, 1999.（有効期間を持つテーブルの設計と問い合わせを理論から扱った教科書。SCD の背後にある時間つきデータ管理の一般論が学べる）

[^scd-name]: Kimball が 1996 年に提唱した当初は Type 1 から 3 までだった。その後の実務の蓄積で拡張され、*The Data Warehouse Toolkit* 第 3 版では Type 0 から 7 までが整理されている。

[^half-open]: 終端を「含まない」側にそろえる規約である。境界のちょうどその瞬間に起きた出来事が、前後どちらの行にも当たる（重複）か、どちらにも当たらない（欠落）かという曖昧さをなくすためで、期間を持つテーブル全般の定石である。

[^snapshot]: snapshot には、比較する列を指定する check strategy のほかに、ソースの更新時刻列を使う timestamp strategy がある。ソースに信頼できる updated_at 列があるなら、全列を比較せずに済む timestamp の方が負荷が小さい。本文は、ソースの列に頼らず動く check で示した。

[^surrogate-key]: Kimball の伝統的な流儀は意味を持たない整数の連番だが、採番の状態を持たず、どの環境でも同じ計算で同じキーを再現できるハッシュ方式が、分散処理と相性がよく dbt では標準的である。generate_surrogate_key は指定した列の値を連結して MD5 ハッシュを取るマクロである。

## 演習と音声

- [第5章 演習問題](exercises/05-slowly-changing-dimensions.md)：四択で章の理解を確認できる。
- [読み上げ音声（mp3）](audio/05-slowly-changing-dimensions.mp3)：聴いて復習できる（[原稿](audio-scripts/05-slowly-changing-dimensions.md)）。
