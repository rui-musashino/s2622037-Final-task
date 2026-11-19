"""データベースに保存したリポジトリ情報を SELECT 文で表示する。

  uv run python show_data.py          # 全件をスター数の多い順に表示
  uv run python show_data.py --limit 20  # 上位20件だけ表示
"""

import argparse
import sqlite3

from database import DB_PATH


def main() -> None:
    parser = argparse.ArgumentParser(description="保存したデータをSELECT文で表示する")
    parser.add_argument("--limit", type=int, default=None, help="表示する件数（省略すると全件）")
    args = parser.parse_args()

    with sqlite3.connect(DB_PATH) as conn:
        sql = "SELECT name, language, stars FROM repositories ORDER BY stars DESC, name"
        params: tuple = ()
        if args.limit is not None:
            sql += " LIMIT ?"
            params = (args.limit,)
        rows = conn.execute(sql, params).fetchall()

        print(sql)
        print(f"{'リポジトリ名':<45} {'主要な言語':<20} {'スター数':>8}")
        print("-" * 80)
        for name, language, stars in rows:
            print(f"{name:<45} {language or '(なし)':<20} {stars:>8,}")

        total = conn.execute("SELECT COUNT(*) FROM repositories").fetchone()[0]
        print("-" * 80)
        print(f"表示 {len(rows)} 件 / 保存件数 {total} 件")

        # 参考: 主要な言語ごとのリポジトリ数（上位10）
        print("\nSELECT language, COUNT(*) ... GROUP BY language（上位10）")
        for language, count in conn.execute(
            """
            SELECT COALESCE(language, '(なし)'), COUNT(*) AS n
            FROM repositories
            GROUP BY language
            ORDER BY n DESC
            LIMIT 10
            """
        ):
            print(f"  {language:<20} {count:>5}")


if __name__ == "__main__":
    main()
