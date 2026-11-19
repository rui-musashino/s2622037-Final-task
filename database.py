"""スクレイピングしたリポジトリ情報を SQLite のデータベースに保存する。"""

import sqlite3

DB_PATH = "google_repos.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS repositories (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT    NOT NULL UNIQUE,  -- リポジトリ名
    language TEXT,                     -- 主要な言語（設定されていないリポジトリは NULL）
    stars    INTEGER NOT NULL          -- スターの数
)
"""


def create_table(conn: sqlite3.Connection) -> None:
    """データを保存するテーブルを作る（既にあれば何もしない）。"""
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()


def save_repositories(conn: sqlite3.Connection, repos: list[dict]) -> None:
    """リポジトリ情報を保存する。同じ名前が既にあれば最新の値で上書きする。"""
    conn.executemany(
        """
        INSERT INTO repositories (name, language, stars)
        VALUES (:name, :language, :stars)
        ON CONFLICT(name) DO UPDATE SET
            language = excluded.language,
            stars    = excluded.stars
        """,
        repos,
    )
    conn.commit()
