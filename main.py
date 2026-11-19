"""Googleのリポジトリ情報を全件スクレイピングして、データベースに保存する。"""

import sqlite3

from database import DB_PATH, create_table, save_repositories
from scraper import scrape_all


def main() -> None:
    repos = scrape_all()
    with sqlite3.connect(DB_PATH) as conn:
        create_table(conn)
        save_repositories(conn, repos)
        count = conn.execute("SELECT COUNT(*) FROM repositories").fetchone()[0]
    print(f"{len(repos)} 件を取得し、{DB_PATH} に保存しました（テーブルの件数: {count} 件）")


if __name__ == "__main__":
    main()
