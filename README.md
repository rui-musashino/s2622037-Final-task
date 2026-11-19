# s2622037-Final-task

DS Programming（データサイエンスプログラミング1）の最終課題です。

GitHub上でGoogleが管理しているリポジトリ（https://github.com/orgs/google/repositories ）をスクレイピングし、全リポジトリの「リポジトリ名・主要な言語・スターの数」をデータベースに保存します。

## 仕組み

- GitHub API は使っていません。ブラウザで見るのと同じ一覧ページ（`https://github.com/orgs/google/repositories?q=sort:name-asc&page=N`）のHTMLを `requests` で取得し、`BeautifulSoup` で解析します（一覧のデータはHTML内の `<script data-target="react-app.embeddedData">` に埋め込まれています）
- 名前順に並べて全ページ（2026年11月20日時点で99ページ・2,947件）を巡回します
- 各アクセスの前に `time.sleep(1)` を入れています。アクセス過多（HTTP 429）やサーバーエラー（5xx）のときは、さらに待ってから最大5回やり直します
- データは SQLite のデータベース `google_repos.db` に保存します

| ファイル | 内容 |
|---|---|
| `scraper.py` | 一覧ページの取得と解析 |
| `database.py` | テーブルの作成とデータの保存 |
| `main.py` | 全件をスクレイピングしてDBに保存する |
| `show_data.py` | 保存したデータを SELECT 文で表示する |
| `google_repos.db` | 実行結果のデータベース（2,947件） |

### テーブル `repositories`

| 列 | 型 | 内容 |
|---|---|---|
| `id` | INTEGER | 連番（主キー） |
| `name` | TEXT | リポジトリ名（重複なし） |
| `language` | TEXT | 主要な言語（設定されていなければ NULL） |
| `stars` | INTEGER | スターの数 |

## 実行方法

```sh
uv sync
uv run python main.py        # スクレイピングしてDBに保存（数分かかります）
uv run python show_data.py   # SELECT文で全件を表示
uv run python show_data.py --limit 20   # スター数の上位20件だけ表示
```

SQLite のコマンドで直接見ることもできます。

```sh
sqlite3 google_repos.db "SELECT name, language, stars FROM repositories ORDER BY stars DESC LIMIT 10;"
```

## 実行結果（スター数の上位10件、2026年11月20日時点）

```
リポジトリ名                                  主要な言語          スター数
material-design-icons                         (なし)                54,333
guava                                         Java                  51,928
zx                                            JavaScript            45,858
styleguide                                    Emacs Lisp            39,848
googletest                                    C++                   39,757
leveldb                                       C++                   39,562
langextract                                   Python                39,343
comprehensive-rust                            Rust                  33,547
material-design-lite                          HTML                  32,192
python-fire                                   Python                28,229
```
