"""旧 URL から新 URL へ転送する静的ページを、ビルド後に site/ へ書き足す MkDocs hook。

教材を docs/data-modeling/ へ移した際に、それまで公開していたルート直下の URL を
壊さないために使う。転送の対応は mkdocs.yml の extra.redirects に書く。

    extra:
      redirects:
        01-overview/: data-modeling/01-overview/

キーと値はどちらもサイトルートからの相対パス（末尾の / まで含む）。各キーに対して
site/<キー>index.html を生成し、meta refresh と canonical で値の URL へ転送する。
mkdocs-redirects プラグインと同じ働きだが、依存を増やさず、プラグインが出す
無関係な警告も避けられる。
"""

import os

TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url={url}">
<link rel="canonical" href="{url}">
<title>移転しました</title>
</head>
<body>
<p>このページは <a href="{url}">{url}</a> へ移転した。</p>
</body>
</html>
"""


def on_post_build(config):
    redirects = (config.get("extra") or {}).get("redirects") or {}
    site_url = (config.get("site_url") or "/").rstrip("/") + "/"
    for old, new in redirects.items():
        target = os.path.join(config["site_dir"], old.strip("/"), "index.html")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(TEMPLATE.format(url=site_url + new.lstrip("/")))
